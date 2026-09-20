# Grant-source verification snapshot

Verification date: 2026-09-21 (Australia/Brisbane). This is source-page
evidence, not a tenant ingestion or unattended-feed acceptance receipt.

| Source | Evidence observed | Intake decision |
|---|---|---|
| NHMRC | The official funding calendar exposes current and upcoming schemes with application-open, minimum-data and closing dates. The page warns that dates are planning dates and final guidelines must be checked. | Keep the bounded HTML adapter as `Needs Review`; do not promote to unattended RSS/API intake. |
| MRFF | The official calendar exposes open, forecast and closed opportunities, including application, minimum-data and closing dates. Forecast dates are explicitly indicative and GrantConnect is the notification authority. | Keep open/forecast/closed rows review-gated; do not promote to unattended RSS/API intake. |
| ARC | The official Grants Dataset page documents a public JSON API and distinguishes funded-project data from opportunity discovery. | Keep the API route `awards_only`; never treat awards as open opportunities. |
| Queensland Grants Finder | The public CKAN package endpoint is a valid metadata response, but the reviewed package exposes contribution-resource metadata rather than opportunity rows. | Keep `metadata_only`; follow linked agency pages for actual calls. |

The bounded review-only adapter was also re-run against fresh HTTPS responses:
NHMRC produced 13 candidate rows and MRFF produced 179 candidate rows. These
are still `Needs Review` candidates, not accepted opportunities; no source row
URL, eligibility decision or tenant write was invented.

## Acceptance boundary

These observations refresh authority-page evidence only. They do not prove a
permitted RSS/Atom endpoint, stable API contract for opportunities, row-level
eligibility review, SharePoint write, Power Automate run, schedule, notification
or organisation-wide target. The fail-closed reviewed-import path remains the
approved fallback for current opportunities until a row has a source URL,
source/row identity, observed timestamp, review notes and `ReviewStatus=Reviewed`.

Official references:

- https://www.nhmrc.gov.au/funding/calendar
- https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar
- https://www.arc.gov.au/funding-research/funding-outcomes/grants-dataset
- https://www.data.qld.gov.au/dataset/grants-finder
