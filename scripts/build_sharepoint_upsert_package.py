"""Build an adapted Power Automate flow package for SharePoint List upserts.

Adapts the existing flow 'CHHHS Publications - DEV manual ingestion validation'
(id: {{FLOW_ID}}) to perform idempotent upserts into
the Queensland Health Publication Registry SharePoint List.

Preserves the existing manual trigger, flow ID, and Power BI validation guards,
while introducing the SharePoint connector actions:
  - Get items filtered by SourceKey
  - Condition: length(items) == 0
  - If new: Create item with ReviewStatus = 'Needs Review', FirstObservedUTC = utcNow()
  - If existing: Update item with LastObservedUTC = utcNow()
"""
import argparse
import copy
import json
from pathlib import Path
import zipfile
from uuid import UUID

ROOT = Path(__file__).resolve().parent.parent

FLOW_ID = "{{FLOW_ID}}"
FLOW_DISPLAY_NAME = "CHHHS Research Publications - Daily Ingestion & Enrichment"
DEFAULT_TARGET = ROOT / "private" / "config" / "sharepoint-publication-target.json"

PUBLICATION_ROWS_QUERY = '''EVALUATE
VAR Ready =
    COALESCE(COUNTROWS(PubMedPublications), 0) > 0
        && COALESCE(COUNTROWS(DoraPublications), 0) > 0
        && COALESCE(COUNTROWS(PubMedIngestionAudit), 0) = 9
        && COALESCE(COUNTROWS(DoraIngestionAudit), 0) = 5
        && COALESCE(COUNTROWS(FILTER(PubMedIngestionAudit, NOT(PubMedIngestionAudit[Passed] == TRUE()))), 0) = 0
        && COALESCE(COUNTROWS(FILTER(DoraIngestionAudit, NOT(DoraIngestionAudit[Passed] == TRUE()))), 0) = 0
VAR Rows =
    SELECTCOLUMNS(
        FILTER(Publication, NOT ISBLANK(Publication[CanonicalKey])),
        "SourceKey", IF(NOT ISBLANK(Publication[PMID]), "pubmed:" & Publication[PMID], "dora:" & Publication[CanonicalKey]),
        "CanonicalKey", Publication[CanonicalKey],
        "Title", Publication[Title],
        "Authors", Publication[Authors],
        "Journal", Publication[Journal],
        "PublicationYear", Publication[PublicationYear],
        "PublicationMonth", Publication[PublicationMonth],
        "PublicationDateRaw", Publication[PublicationDateRaw],
        "PublicationDatePrecision", Publication[PublicationDatePrecision],
        "SourceSet", Publication[SourceSet],
        "PMID", Publication[PMID],
        "DOI", Publication[DOI],
        "MatchedFacilities", Publication[MatchedFacilities],
        "AttributionEvidence", Publication[AttributionEvidence]
    )
RETURN FILTER(Rows, Ready)
'''


def load_target(path: Path) -> tuple[str, str, str, dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    site_url = str(payload.get("site_url") or "").strip()
    list_id = str(payload.get("list_id") or "").strip()
    model_id = str(payload.get("model_id") or "").strip()
    fields = payload.get("fields") or {}
    required = {"title", "source_key", "canonical_key", "authors", "journal", "publication_year",
                "publication_month", "publication_date_raw", "publication_date_precision", "source_set",
                "pmid", "doi", "matched_facilities", "attribution_evidence", "review_status",
                "first_observed", "last_observed"}
    if not site_url or not list_id or not model_id or "{{" in site_url or "{{" in list_id or "{{" in model_id or not required.issubset(fields):
        raise ValueError("validated private SharePoint target, model and complete field mapping are required")
    try:
        UUID(list_id)
        UUID(model_id)
    except ValueError as exc:
        raise ValueError("SharePoint list_id must be a GUID") from exc
    return site_url, list_id, model_id, {key: str(fields[key]) for key in required}


def build_package(baseline_path: Path, output_path: Path, target_path: Path = DEFAULT_TARGET) -> Path:
    if not output_path.resolve().is_relative_to((ROOT / "private").resolve()):
        raise ValueError("Native package must be written under ignored private/.")

    site_url, list_guid, model_id, fields = load_target(target_path)
    with zipfile.ZipFile(baseline_path) as archive:
        files = {n: archive.read(n) for n in archive.namelist()}

    name = next(n for n in files if n.endswith("/definition.json"))
    document = json.loads(files[name])
    definition = document["properties"]["definition"]

    # Canonical daily recurrence trigger at 06:00 AEST (20:00 UTC), 1h before Power BI 07:00 AEST refresh
    definition["triggers"] = {
        "Recurrence": {
            "type": "Recurrence",
            "recurrence": {
                "frequency": "Day",
                "interval": 1,
                "schedule": {"hours": ["20"], "minutes": [0]},
                "timeZone": "UTC",
            },
        }
    }

    # Ensure connection reference for SharePoint Online is present
    document["properties"]["connectionReferences"]["shared_sharepointonline"] = {
        "connectionName": "shared-sharepointonline",
        "source": "Invoker",
        "id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
        "tier": "NotSpecified",
        "apiName": "sharepointonline",
        "isProcessSimpleApiReferenceConversionAlreadyDone": False,
    }

    definition["actions"]["Run_a_query_against_a_dataset"]["inputs"]["parameters"]["datasetid"] = model_id

    # SharePoint Upsert Actions definition
    # These actions are deliberately nested inside a serial loop. Power Automate's
    # item() expression is only valid in that record scope, and serial execution
    # prevents two rows with the same SourceKey racing between lookup and write.
    record_actions = {
        "SharePoint_Get_items": {
            "runAfter": {},
            "type": "OpenApiConnection",
            "inputs": {
                "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                    "connectionName": "shared_sharepointonline",
                    "operationId": "GetItems",
                },
                "parameters": {
                    "dataset": site_url,
                    "table": list_guid,
                    "$filter": "field_1 eq '@{replace(string(item()?['SourceKey']),'''','''''')}'",
                    "$top": 2,
                },
                "authentication": {
                    "type": "Raw",
                    "value": "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']",
                },
            },
        },
        "Condition_Duplicate_SourceKey": {
            "runAfter": {"SharePoint_Get_items": ["Succeeded"]},
            "type": "If",
            "expression": {"greater": ["@length(body('SharePoint_Get_items')?['value'])", 1]},
            "actions": {
                "Compose_Duplicate_SourceKey_Failure": {
                    "type": "Compose",
                    "inputs": "@int('DUPLICATE_SOURCE_KEY')",
                }
            },
            "else": {"actions": {}},
        },
        "Condition_Is_New_Publication": {
            "runAfter": {"Condition_Duplicate_SourceKey": ["Succeeded"]},
            "type": "If",
            "expression": {
                "equals": ["@length(body('SharePoint_Get_items')?['value'])", 0]
            },
            "actions": {
                "SharePoint_Create_item": {
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                            "connectionName": "shared_sharepointonline",
                            "operationId": "PostItem",
                        },
                        "parameters": {
                            "dataset": site_url,
                            "table": list_guid,
                            f"item/{fields['title']}": "@{item()?['Title']}",
                            f"item/{fields['source_key']}": "@{item()?['SourceKey']}",
                            f"item/{fields['canonical_key']}": "@{item()?['CanonicalKey']}",
                            f"item/{fields['authors']}": "@{item()?['Authors']}",
                            f"item/{fields['journal']}": "@{item()?['Journal']}",
                            f"item/{fields['publication_year']}": "@item()?['PublicationYear']",
                            f"item/{fields['publication_month']}": "@{item()?['PublicationMonth']}",
                            f"item/{fields['publication_date_raw']}": "@{item()?['PublicationDateRaw']}",
                            f"item/{fields['publication_date_precision']}": "@{item()?['PublicationDatePrecision']}",
                            f"item/{fields['source_set']}": "@{item()?['SourceSet']}",
                            f"item/{fields['pmid']}": "@item()?['PMID']",
                            f"item/{fields['doi']}": "@{item()?['DOI']}",
                            f"item/{fields['matched_facilities']}": "@{item()?['MatchedFacilities']}",
                            f"item/{fields['attribution_evidence']}": "@{item()?['AttributionEvidence']}",
                            f"item/{fields['review_status']}": "Needs Review",
                            f"item/{fields['first_observed']}": "@{utcNow()}",
                            f"item/{fields['last_observed']}": "@{utcNow()}",
                        },
                        "authentication": {
                            "type": "Raw",
                            "value": "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']",
                        },
                    },
                }
            },
            "else": {
                "actions": {
                    "SharePoint_Update_item": {
                        "type": "OpenApiConnection",
                        "inputs": {
                            "host": {
                                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                                "connectionName": "shared_sharepointonline",
                                "operationId": "PatchItem",
                            },
                            "parameters": {
                                "dataset": site_url,
                                "table": list_guid,
                                "id": "@first(body('SharePoint_Get_items')?['value'])?['Id']",
                                f"item/{fields['last_observed']}": "@{utcNow()}",
                            },
                            "authentication": {
                                "type": "Raw",
                                "value": "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']",
                            },
                        },
                    }
                }
            },
        },
    }

    definition["actions"]["Run_publication_rows_query"] = {
        "runAfter": {"Run_a_query_against_a_dataset": ["Succeeded"]},
        "type": "OpenApiConnection",
        "inputs": {
            "parameters": {
                "groupid": "myworkspace",
                "datasetid": model_id,
                "specification/query": PUBLICATION_ROWS_QUERY,
                "specification/serializerSettings/includeNulls": True,
            },
            "host": {
                "apiId": "/providers/Microsoft.PowerBI/apis/shared_powerbi",
                "connectionName": "shared_powerbi",
                "operationId": "ExecuteDatasetQuery",
            },
            "authentication": {"type": "Raw", "value": "@parameters('$authentication')"},
        },
    }
    definition["actions"]["Apply_to_each_Publication"] = {
        "runAfter": {"Run_publication_rows_query": ["Succeeded"]},
        "type": "Foreach",
        "foreach": "@coalesce(body('Run_publication_rows_query')?['results'][0]?['tables'][0]?['rows'], createArray())",
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
        "actions": record_actions,
    }
    document["properties"]["displayName"] = FLOW_DISPLAY_NAME
    files[name] = json.dumps(document, indent=2).encode("utf-8")

    # Update manifest to target existing flow update
    manifest = json.loads(files["manifest.json"])
    manifest["details"]["displayName"] = FLOW_DISPLAY_NAME

    for res_id, res_def in manifest["resources"].items():
        if res_def["type"] == "Microsoft.Flow/flows":
            res_def["suggestedCreationType"] = "Update"
            res_def["creationType"] = "Existing, Update"
            res_def["details"]["displayName"] = FLOW_DISPLAY_NAME
            if "sp_api_id" not in res_def.get("dependsOn", []):
                res_def["dependsOn"].append("sp_api_id")
                res_def["dependsOn"].append("sp_conn_id")

    manifest["resources"]["sp_api_id"] = {
        "id": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
        "name": "shared_sharepointonline",
        "type": "Microsoft.PowerApps/apis",
        "suggestedCreationType": "Existing",
        "details": {
            "displayName": "SharePoint",
            "iconUri": "https://static.powerapps.com/resource/ppcr/releases/v1.0.1827/1.0.1827.4902/sharepointonline/icon.png",
        },
        "configurableBy": "System",
        "hierarchy": "Child",
        "dependsOn": [],
    }

    manifest["resources"]["sp_conn_id"] = {
        "type": "Microsoft.PowerApps/apis/connections",
        "suggestedCreationType": "Existing",
        "creationType": "Existing",
        "details": {
            "displayName": "{{SHAREPOINT_CONNECTION_DISPLAY_NAME}}",
            "iconUri": "https://static.powerapps.com/resource/ppcr/releases/v1.0.1827/1.0.1827.4902/sharepointonline/icon.png",
        },
        "configurableBy": "User",
        "hierarchy": "Child",
        "dependsOn": ["sp_api_id"],
    }

    files["manifest.json"] = json.dumps(manifest, indent=2).encode("utf-8")

    # Update apisMap and connectionsMap
    flow_folder = next(p.split("/")[2] for p in files if p.startswith("Microsoft.Flow/flows/") and p.endswith("/definition.json"))
    apis_map_key = f"Microsoft.Flow/flows/{flow_folder}/apisMap.json"
    conns_map_key = f"Microsoft.Flow/flows/{flow_folder}/connectionsMap.json"

    if apis_map_key in files:
        apis_map = json.loads(files[apis_map_key])
        apis_map["shared_sharepointonline"] = "sp_api_id"
        files[apis_map_key] = json.dumps(apis_map).encode("utf-8")

    if conns_map_key in files:
        conns_map = json.loads(files[conns_map_key])
        conns_map["shared_sharepointonline"] = "sp_conn_id"
        files[conns_map_key] = json.dumps(conns_map).encode("utf-8")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, content in files.items():
            z.writestr(fname, content)

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "private" / "ops" / "flow-packages" / "validation-baseline.zip",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "private" / "ops" / "flow-packages" / "sharepoint-upsert.zip",
    )
    parser.add_argument("--target-config", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    out = build_package(args.baseline, args.output, args.target_config)
    print(f"Generated adapted SharePoint upsert package at: {out}")
