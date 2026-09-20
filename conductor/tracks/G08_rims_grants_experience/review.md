# G08 review

Review status: in progress; local planning and idempotency contracts are implemented.

- `validate_policy` requires a version, organisation, anchor, lead time, holiday-calendar version and effective dates.
- `delivery_event_key` gives future notifications a stable deduplication key; it does not send messages or create calendar events.
- Existing subscription matching remains candidate generation only and does not authorize delivery.

## Local report/model surface — 2026-09-20

- Added an empty-safe `GrantsRegistry` semantic-model table using the existing
  SharePoint read definition, with stable opportunity/deadline/review fields
  and explicit measures for total, open and needs-review opportunities.
- Added three additive pages to the existing PBIP: `FundingOpportunities`,
  `FundingCalendar` and `MyFundingWatchlist`. The calendar preserves raw
  deadline text and precision; the watchlist is explicitly a report preview,
  not a personal subscription or notification service.
- Expanded the local dashboard contract to seven pages and added model-binding,
  geometry and page-order tests. This is a source/report definition change,
  not native Power BI page authoring or readback.

Native funding pages, SharePoint list persistence, authenticated preference
isolation, calendar update/cancellation and notification delivery remain open.
