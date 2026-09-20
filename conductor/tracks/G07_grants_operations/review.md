# G07 review

Review status: in progress; local operational guardrails are implemented.

`scripts/grants_operations.py` rejects empty batches, missing or duplicate opportunity keys, and any failed source. On rejection it returns the prior accepted records instead of replacing them. Tests cover source failure preservation. Native monitoring, concurrency and schedule/delivery evidence remains open. A controlled authenticated Power Automate replay now proves one synthetic create and one same-key update, with the flow restored Off; see the G03 review and the ignored receipt `private/ops/2026-09-20-grants-flow-import-readback.json`. No unattended schedule, notification or production path was touched.
