"""Prepare same-identity flow and scoped TMDL candidates; never deploy them."""
from __future__ import annotations

import copy
import hashlib
import json
from uuid import NAMESPACE_URL, uuid5

try:
    from .grants_deadline_schedule import SCHEDULE_FIELDS, NIH_ATTRIBUTION
except ImportError:
    from grants_deadline_schedule import SCHEDULE_FIELDS, NIH_ATTRIBUTION


def patch_flow(document: dict) -> dict:
    result = copy.deepcopy(document)
    found = {"PostItem": 0, "PatchItem": 0, "ordering": 0}

    def walk(value):
        if isinstance(value, dict):
            operation = value.get("inputs", {}).get("host", {}).get("operationId") if isinstance(value.get("inputs"), dict) else None
            if operation in ("PostItem", "PatchItem"):
                params = value["inputs"]["parameters"]
                if "item/OpportunityKey" not in params:
                    raise ValueError("unexpected SharePoint writer")
                if operation == "PatchItem" and any(k in params for k in ("item/ReviewStatus", "item/ReviewNotes")):
                    raise ValueError("update must preserve reviewer fields")
                for name in SCHEDULE_FIELDS:
                    key = "item/" + name
                    expression = "@{item()?['" + name + "']}"
                    if key in params and params[key] != expression:
                        raise ValueError("schedule mapping drift")
                    params[key] = expression
                found[operation] += 1
            if "Condition_Observation_Not_Older" in value:
                expr = value["Condition_Observation_Not_Older"]["expression"]
                same = expr["or"][1]["and"]
                if "@ticks(item()?['RetrievedUTC'])" not in json.dumps(same[0]):
                    raise ValueError("unexpected same-time guard")
                for name in SCHEDULE_FIELDS:
                    equality = {"equals": ["@string(coalesce(item()?['" + name + "'], ''))",
                        "@string(coalesce(first(body('SharePoint_Get_items')?['value'])?['" + name + "'], ''))"]}
                    if equality not in same:
                        same.append(equality)
                found["ordering"] += 1
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(result)
    if found != {"PostItem": 1, "PatchItem": 1, "ordering": 1}:
        raise ValueError(f"unexpected writer/ordering count: {found}")
    return result


def model_candidate(parent: bytes, occurrence_m: str, *, expected_sha256: str) -> bytes:
    if hashlib.sha256(parent).hexdigest() != expected_sha256:
        raise ValueError("model preimage fingerprint mismatch")
    text = parent.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    anchor = "\t\tpartition 'Grants Registry' = m"
    if text.count(anchor) != 1 or "\ttable 'Grants Registry'" not in text:
        raise ValueError("expected exact parent table script")
    if any("column " + n + nl in text for n in SCHEDULE_FIELDS):
        raise ValueError("schedule model fields already present; rebase instead of duplicate")
    def tag(name):
        return str(uuid5(NAMESPACE_URL, "rims/grants-schedule/v1/" + name))
    fields = ""
    for name in SCHEDULE_FIELDS:
        column_tag = str(uuid5(NAMESPACE_URL, "chhhs-research/GrantsRegistry/" + name))
        fields += nl.join([f"\t\tcolumn {name}", "\t\t\tdataType: string",
            f"\t\t\tlineageTag: {column_tag}", "\t\t\tsummarizeBy: none",
            f"\t\t\tsourceColumn: {name}", "", ""])
    fields += nl.join(["\t\tmeasure 'Funding Source Attribution' = " + json.dumps(NIH_ATTRIBUTION),
                      "\t\t\tdescription: Grants.gov API attribution and non-endorsement notice.",
                      "\t\t\tformatString: @",
                      f"\t\t\tlineageTag: {tag('attribution-measure')}", "", ""])
    text = text.replace(anchor, fields + anchor)
    # A separate import partition derives rows from the existing parent query.
    table = ["", "\ttable 'Grants Deadline Occurrences'",
             "\t\tdescription: Published application schedule; one local occurrence per parent opportunity and application date. Effective deadlines remain unresolved.",
             f"\t\tlineageTag: {tag('occurrence-table')}", ""]
    names = ("OpportunityKey", "OccurrenceKey", "ApplicationType", "NominalDueDate",
             "EffectiveDueDate", "SourceLocalTime", "SourceTimezoneRule", "SourceURL",
             "TemporalStatus", "SourceAttribution", "SourceOccurrenceJSON")
    for name in names:
        table += [f"\t\tcolumn {name}", "\t\t\tdataType: string",
                  f"\t\t\tlineageTag: {tag('occurrence/' + name)}",
                  "\t\t\tsummarizeBy: none", f"\t\t\tsourceColumn: {name}", ""]
    table += ["\t\tpartition 'Grants Deadline Occurrences' = m", "\t\t\tmode: import", "\t\t\tsource ="]
    table += ["\t\t\t\t" + line for line in occurrence_m.splitlines()]
    table += ["", "\t\tannotation PBI_ResultType = Table", ""]
    table += [f"\trelationship {tag('parent-relationship')}",
              "\t\tfromColumn: 'Grants Deadline Occurrences'.OpportunityKey",
              "\t\ttoColumn: 'Grants Registry'.OpportunityKey", ""]
    return (text + nl.join(table)).encode("utf-8")
