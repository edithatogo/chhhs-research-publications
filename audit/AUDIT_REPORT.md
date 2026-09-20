# Source PBIX audit

Audit date: 11 September 2026. No source query was executed.

## Root cause

The adapted file retained the original binary DataModel exactly. The previous research tab was only an unapplied script, not a replacement of the active model.

- DataModel bytes: 8,389,006
- SHA-256: `00e72ca2699ffa5302ef12345dd7fedc603ce600cd03e43e5b6ee929b938ceaa`
- Legacy report string locations: 515 (includes repeated bindings, not 515 separate visual defects).
- Three old TMDL scripts, report linguistic schema, mobile state, diagram state and connections were unchanged.

## Page audit

| Page | Visuals | Legacy string locations | Old date filters |
|---|---:|---:|---|
| Monthly Research | 4 | 144 | 2014L, 'Dec' |
| Research Portfolio | 4 | 132 | 2014L, 'Dec' |
| Publication Tooltip | 3 | 88 | None found |
| Clinical Trials & Evidence | 5 | 151 | 2014L, 'Dec' |

## Additional defects in the proposed replacement

- Research data was mapped to Employee, Gender, Ethnicity, Age and Business unit names. Measures were still named New Hires, Separations, Actives and Bad Hires.
- Power Query strings used backslash-escaped quotes, which are not the correct M text-literal escaping convention.
- Date parsing clipped every day after 28 to 28; missing or invalid years could become the current year.
- Some errors were converted to empty result sets. Search result completeness was not reconciled.
- Broad Yarrabah affiliation matching could include independent services.
- There was no persistent first-seen registry. A refresh timestamp is not a publication discovery date.

## Remediation

Create a new cache-free PBIP using research-native tables, M queries, DAX measures and documented PBIR visuals. Do not carry over any old DataModel, TMDLScripts, Connections, DiagramState, LinguisticSchema, MobileState, filter state or bookmarks. Preserve the source outside the deliverable.

## Verification boundary

Binary hashes and readable metadata were inspected directly. No native Power BI engine exists in this container. The replacement requires a recorded Desktop open/refresh/save acceptance test before it is called a verified native PBIX.

