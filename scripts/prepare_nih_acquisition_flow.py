"""Build the bounded native NIH acquisition/archive qualification stage.

No register/model write or message delivery is authorized by this builder.
HTTP JSON is retained as the complete native-decoded response, not wire bytes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

SOURCE = "us-grants-gov-nih-pa-25-301"
FON = "PA-25-301"
OPPORTUNITY_ID = 357812
ROOT = "/Documents/CHHHS Research System - DEV/01 Source archive"


def prepare(site: str, folder: str = ROOT, *, minutes: int | None = None,
            fault: bool = False) -> dict:
    parsed = urlparse(site)
    if (parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith(".sharepoint.com") or parsed.query
            or parsed.fragment or "'" in site or ".." in site
            or not folder.startswith("/Documents/") or ".." in folder or "'" in folder):
        raise ValueError("Use the existing qualified SharePoint site and archive folder")
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= 60):
        raise ValueError("qualification interval must be 1..60 minutes")

    def action(kind, inputs, after=None, **extra):
        return {"type": kind, "runAfter": {after: ["Succeeded"]} if after else {},
                "inputs": inputs, **extra}

    def sp(op, params, after=None):
        return action("OpenApiConnection", {
            "host": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                     "connectionName": "shared_sharepointonline", "operationId": op},
            "parameters": {"dataset": site, **params}, "retryPolicy": {"type": "none"}}, after)

    def save(name, value, after, target="@outputs('Run_folder')"):
        return sp("CreateFile", {"folderPath": target, "name": name,
                                 "body": f"@base64ToBinary(base64({value}))"}, after)

    def read(path, after):
        return sp("GetFileContentByPath", {"path": path, "inferContentType": False}, after)

    def guard(expr, after, code="NIH_ARCHIVE_VERIFICATION_FAILED"):
        return action("Compose", f"@if({expr},true,json('{code}'))", after)

    requests = []
    for suffix in ["current", "replay"]:
        requests.extend([
            {"role": "search-" + suffix, "endpoint": "search2", "request": {
                "oppNum": FON, "rows": 10, "oppStatuses": "forecasted|posted|closed|archived"}},
            {"role": "detail-" + suffix, "endpoint": "fetchOpportunity",
             "request": {"opportunityId": OPPORTUNITY_ID}},
        ])
    scope = {"source": SOURCE, "opportunity_id": OPPORTUNITY_ID, "fon": FON,
             "request_count": 4, "requests": requests,
             "representation": "complete Power Automate decoded JSON response serialized to UTF-8; not HTTP wire bytes",
             "register_updated": False, "model_refreshed": False, "accepted": False,
             "attachment_policy": "retain every current synopsis folder ZIP via the official opportunity-page download route; verify binary readback"}
    source_guard = (
        "and(equals(outputs('Fetch_response')?['statusCode'],200),"
        "equals(body('Fetch_response')?['errorcode'],0),"
        "if(equals(item()?['endpoint'],'search2'),"
        "and(equals(body('Fetch_response')?['data']?['hitCount'],1),"
        "equals(body('Fetch_response')?['data']?['startRecord'],0),"
        "equals(length(body('Fetch_response')?['data']?['oppHits']),1),"
        f"equals(first(body('Fetch_response')?['data']?['oppHits'])?['id'],'{OPPORTUNITY_ID}'),"
        f"equals(first(body('Fetch_response')?['data']?['oppHits'])?['number'],'{FON}'),"
        "equals(first(body('Fetch_response')?['data']?['oppHits'])?['oppStatus'],'posted'),"
        f"equals(body('Fetch_response')?['data']?['searchParams']?['oppNum'],'{FON}')),"
        f"and(equals(body('Fetch_response')?['data']?['id'],{OPPORTUNITY_ID}),"
        f"equals(body('Fetch_response')?['data']?['opportunityNumber'],'{FON}'),"
        "equals(body('Fetch_response')?['data']?['ost'],'POSTED'),"
        "equals(body('Fetch_response')?['data']?['listed'],'L'),"
        "equals(body('Fetch_response')?['data']?['draftMode'],'N'))))")
    loop = {
        "Fetch_response": action("Http", {"uri": "@concat('https://api.grants.gov/v1/api/',item()?['endpoint'])",
            "method": "POST", "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "body": "@item()?['request']", "retryPolicy": {"type": "none"}}),
        "Response_text": action("Compose", "@string(body('Fetch_response'))", "Fetch_response"),
        "Save_response": save("@concat(item()?['role'],'.json')", "outputs('Response_text')", "Response_text"),
        "Read_response": read("@concat(outputs('Run_folder'),'/',item()?['role'],'.json')", "Save_response"),
        "Verify_response": guard("equals(base64(outputs('Response_text')),body('Read_response')?['$content'])", "Read_response"),
        "Guard_source": guard(source_guard, "Verify_response", "NIH_SOURCE_REJECTED"),
        "Record_response": action("AppendToArrayVariable", {"name": "Responses", "value": {
            "role": "@item()?['role']", "http_status": "@outputs('Fetch_response')?['statusCode']",
            "request": "@item()?['request']", "response": "@json(outputs('Response_text'))",
            "content_base64": "@body('Read_response')?['$content']",
            "archive_path": "@concat(outputs('Run_folder'),'/',item()?['role'],'.json')"}}, "Guard_source"),
    }
    pipeline = {
        "Create_folder": sp("HttpRequest", {"parameters/method": "POST", "parameters/uri": "_api/web/folders",
            "parameters/headers": {"Accept": "application/json;odata=nometadata", "Content-Type": "application/json;odata=nometadata"},
            "parameters/body": {"ServerRelativeUrl": "@concat('" + parsed.path.rstrip("/") + "',outputs('Run_folder'))"}}),
        "Save_scope": save("scope.json", "string(outputs('Scope'))", "Create_folder"),
        "For_each_response": {"type": "Foreach", "foreach": "@outputs('Scope')?['requests']",
            "runAfter": {"Save_scope": ["Succeeded"]}, "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": loop},
        "Require_four_archived": guard("equals(length(variables('Responses')),4)", "For_each_response"),
        "Guard_attachment_scope": guard("and(lessOrEquals(length(variables('Responses')[1]?['response']?['data']?['synopsisAttachmentFolders']),10),equals(variables('Responses')[1]?['response']?['data']?['synopsisAttachmentFolders'],variables('Responses')[3]?['response']?['data']?['synopsisAttachmentFolders']))", "Require_four_archived"),
        "For_each_attachment_folder": {"type": "Foreach",
            "foreach": "@variables('Responses')[1]?['response']?['data']?['synopsisAttachmentFolders']",
            "runAfter": {"Guard_attachment_scope": ["Succeeded"]},
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": {
                "Guard_folder_identity": guard(f"and(equals(item()?['opportunityId'],{OPPORTUNITY_ID}),greater(item()?['id'],0),greater(item()?['zipLobSize'],0),lessOrEquals(item()?['zipLobSize'],52428800))", None),
                "Fetch_attachment": action("Http", {"uri": "@concat('https://apply07.grants.gov/grantsws/rest/opportunity/folder/download/',string(item()?['id']))",
                    "method": "GET", "retryPolicy": {"type": "none"}}, "Guard_folder_identity"),
                "Save_attachment": sp("CreateFile", {"folderPath": "@outputs('Run_folder')",
                    "name": "@concat('attachment-folder-',string(item()?['id']),'.zip')", "body": "@body('Fetch_attachment')"}, "Fetch_attachment"),
                "Read_attachment": read("@concat(outputs('Run_folder'),'/attachment-folder-',string(item()?['id']),'.zip')", "Save_attachment"),
                "Verify_attachment": guard("and(equals(outputs('Fetch_attachment')?['statusCode'],200),not(empty(body('Fetch_attachment')?['$content'])),equals(body('Read_attachment')?['$content'],body('Fetch_attachment')?['$content']))", "Read_attachment"),
                "Record_attachment": action("AppendToArrayVariable", {"name": "Attachments", "value": {
                    "folder_metadata": "@item()", "download_url": "@concat('https://apply07.grants.gov/grantsws/rest/opportunity/folder/download/',string(item()?['id']))",
                    "archive_path": "@concat(outputs('Run_folder'),'/attachment-folder-',string(item()?['id']),'.zip')",
                    "content_base64": "@body('Read_attachment')?['$content']"}}, "Verify_attachment"),
            }},
        "Qualification_guard": guard("false" if fault else "true", "For_each_attachment_folder", "NIH_QUALIFICATION_INJECTED_FAILURE"),
        "Acquisition_manifest": action("Compose", {"format": "rims-nih-acquisition-v1", "source": SOURCE,
            "run": "@workflow()?['run']?['name']", "observed_utc": "@outputs('Observed_utc')",
            "scope": "@outputs('Scope')", "responses": "@variables('Responses')",
            "acquisition_complete": True, "accepted": False, "register_updated": False, "model_refreshed": False,
            "attachment_folders": "@variables('Attachments')",
            "attachment_files_retained": True, "end_to_end_qualified": False}, "Qualification_guard"),
        "Save_manifest": save("acquisition.json", "string(outputs('Acquisition_manifest'))", "Acquisition_manifest"),
        "Read_manifest": read("@concat(outputs('Run_folder'),'/acquisition.json')", "Save_manifest"),
        "Verify_manifest": guard("equals(base64(string(outputs('Acquisition_manifest'))),body('Read_manifest')?['$content'])", "Read_manifest"),
    }
    failure = {
        "Failure_receipt": action("Compose", {"format": "rims-nih-failure-v1", "source": SOURCE,
            "run": "@workflow()?['run']?['name']", "observed_utc": "@outputs('Observed_utc')",
            "archive_folder": "@outputs('Run_folder')", "accepted": False, "register_updated": False,
            "model_refreshed": False, "notification_delivered": False,
            "actions": "@result('Acquisition')", "verified_response_prefix": "@variables('Responses')",
            "recovery": "preserve last-good register/model; inspect run and retained originals; start a fresh generation"}),
        "Save_failure": save("@concat('nih-acquisition-failed-',workflow()?['run']?['name'],'.json')",
                             "string(outputs('Failure_receipt'))", "Failure_receipt", folder),
        "Read_failure": read("@concat('" + folder + "/nih-acquisition-failed-',workflow()?['run']?['name'],'.json')", "Save_failure"),
        "Verify_failure": guard("equals(base64(string(outputs('Failure_receipt'))),body('Read_failure')?['$content'])", "Read_failure"),
        "Terminate_failure": {"type": "Terminate", "runAfter": {"Verify_failure": ["Succeeded", "Failed", "TimedOut", "Skipped"]},
            "inputs": {"runStatus": "Failed", "runError": {"code": "NihAcquisitionRejected",
                "message": "Acquisition/archive failed. Preserve last-good register/model. Inspect the failure receipt; notification delivery is not qualified."}}},
    }
    recurrence = {"frequency": "Minute", "interval": minutes} if minutes else {
        "frequency": "Day", "interval": 1, "timeZone": "E. Australia Standard Time",
        "schedule": {"hours": [6], "minutes": [0]}}
    return {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0", "parameters": {"$authentication": {"defaultValue": {}, "type": "SecureObject"},
            "$connections": {"defaultValue": {}, "type": "Object"}},
        "triggers": {"Recurrence": {"type": "Recurrence", "recurrence": recurrence,
            "runtimeConfiguration": {"concurrency": {"runs": 1}}}},
        "actions": {"Scope": action("Compose", scope), "Observed_utc": action("Compose", "@utcNow()", "Scope"),
            "Run_folder": action("Compose", "@concat('" + folder + "/nih-acquisition-',workflow()?['run']?['name'])", "Observed_utc"),
            "Initialize_responses": action("InitializeVariable", {"variables": [
                {"name": "Responses", "type": "array", "value": []},
                {"name": "Attachments", "type": "array", "value": []}]}, "Run_folder"),
            "Acquisition": {"type": "Scope", "runAfter": {"Initialize_responses": ["Succeeded"]}, "actions": pipeline},
            "Observe_failure": {"type": "Scope", "runAfter": {"Acquisition": ["Failed", "TimedOut"]}, "actions": failure}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True)
    parser.add_argument("--folder", default=ROOT)
    parser.add_argument("--qualification-minutes", type=int)
    parser.add_argument("--inject-failure", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(prepare(args.site, args.folder, minutes=args.qualification_minutes,
                                            fault=args.inject_failure), indent=2) + "\n")


if __name__ == "__main__":
    main()
