# NIH PA-25-301 source admission — 24 October 2026

Source admission is qualified for one announcement: **PA-25-301 / Grants.gov ID 357812**. It does not establish general NIH coverage, CHHHS eligibility, native ingestion acceptance or unattended operation. The existing flow remains Off.

## Evidence and scope

| Admission check | Evidence-backed decision |
| --- | --- |
| Access and response schema | Official public Grants.gov search2 and fetchOpportunity JSON contracts; four fresh complete HTTP 200 responses retained privately, two search/detail passes. No credentials or API key supplied. |
| Pagination and replay | Exact FON query includes forecasted, posted, closed and archived; both reads returned hitCount 1, startRecord 0 and the same single ID/FON. Full semantic detail matches across replay, allowing order independence only for applicant categories keyed by their IDs. No broad-query completeness claim. |
| Stable identity | Official grantor rules require the opportunity number to be unique across agencies. Current and historical versions retain the same numeric ID and FON. Revisions are not new opportunities. This is observed/documented identity, not an assurance against future source mistakes. |
| Round and dates | The announcement FON is retained in the existing RoundID field; seven child occurrence keys represent nominal future application dates, not new source rounds. Announcement close/archive/expiry facts remain distinct. |
| Lifecycle | Official forecasted/posted/closed/archived and synopsis-deletion semantics are documented. The selected adapter accepts only a complete, same-identity, published/posted result; source changes fail closed for investigation. A missing result never directs deletion. Live closure/deletion transitions and native last-good recovery are not claimed. |
| Reuse and attribution | Current API terms permit retrieval, display and analysis, subject to attribution and no false source representation. Unmodified API envelopes are retained; normalized/derived values are distinguished. The prescribed notice and official terms link are saved and visibly verified in the existing Grants Registry form header. |
| Entity reconciliation | Complete original API payloads and history are retained. The prepared row preserves its stable key and 32-field contract, all seven nominal occurrences, source date facts and attribution. Fresh native field readback matches all 32 physical fields; the saved 37-part isolated model contains the parent fields, child table and relationship. Current flow mappings retain review fields on update. Real ingestion/refresh parity remains the subsequent G04 gate. |

## Date and eligibility limits

The nominal dates are 2026-11-05, 2027-02-05, 2027-03-05, 2027-06-05, 2027-07-05, 2027-10-05 and 2027-11-05. The source states 5 PM local time of the applicant organisation. No applicant timezone, UTC/Brisbane instant, holiday adjustment, effective due date, CHHHS relevance or applicant eligibility is inferred. Full source statements remain linked, including current foreign-organisation restrictions and related notices.

## Native attribution and recovery

The supported list-footer trial saved correctly but did not render on the empty-list screen. Its formatting and count aggregate were removed; the original unformatted/unaggregated view behavior, fields and query are preserved. The server now represents cleared values as empty strings and Off rather than the original nulls. The list content type had no existing form formatter; only its header was added, preserving fields and any body/footer absence. Native exact readback and two independent form opens verify the notice and terms link. The blank preview was cancelled; no list item was created. Rollback restores the recorded empty original ClientFormCustomFormatter on that exact content type after a fresh drift check. No permissions, flow state, schedules or billing changed.

The formatter is versioned in `config/grants-source-attribution.form.json`. Exact target identities, original/postimage payloads, current full fields, flow definition, raw API responses and acceptance receipts remain under ignored `private/ops/2026-10-24-nih-admission/`. Earlier model restore and 37-part scope receipts remain under ignored `private/ops/2026-10-24-grants-native-type/`.

## Original response fingerprints

| Capture | Bytes | SHA256 |
| --- | ---: | --- |
| search-current.json | 3260 | `7e3fc7cafa3c0350e3c96ad17ba47f3dc69ac98e95690ec14fbe3e80d68dc8e8` |
| detail-current.json | 19667 | `68acfb7401ee8b90e1223559397c5dbc26f56e839c318674093275f79bf5b61e` |
| search-replay.json | 3260 | `4fa9f397565a3d7635c5037af39a35e93088f4f6f7cbf92192567902781760d7` |
| detail-replay.json | 19667 | `2d4ba6668cd340f8bfdf4d9e76de78201020f523bac91409c1c74547eaa24689` |

## Operations and stopping conditions

Reacquire exact search and full detail twice before each operator import. Archive complete originals before projection; retain source and observation timestamps separately. Stop on any access/schema/identity/status/pagination/replay/schedule/attribution drift. Keep the last accepted observation, report uncertainty and requalify; do not automatically tombstone missing records. Catalogue enabled=true permits the qualified bounded source read and validation only; it does not activate a cloud flow or recurrence. Set enabled=false to stop source probes and prevent admission; preserve archived history. The current operator is the user/model owner; future operational role assignment and scheduled observations remain separate.

## Official references

- [API guide](https://www.grants.gov/api/api-guide)
- [Search contract](https://www.grants.gov/api/common/search2)
- [Detail contract](https://www.grants.gov/api/common/fetchopportunity)
- [Unique opportunity-number rule](https://www.grants.gov/system-to-system/grantor-system-to-system/web-services/create-opportunity-package)
- [Source status definitions](https://grants.gov/help/search-grants/search-grants-tab)
- [Synopsis deletion semantics](https://grants.gov/help/grantors/delete-synopsis)
- [API terms and attribution](https://www.grants.gov/api/terms-conditions)
- [Official NIH announcement](https://grants.nih.gov/grants/guide/pa-files/PA-25-301.html)
- [NCATS participation notice](https://grants.nih.gov/grants/guide/notice-files/NOT-TR-26-007.html)
