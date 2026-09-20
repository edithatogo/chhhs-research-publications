# G07 review

Review status: in progress; local operational guardrails are implemented.

`scripts/grants_operations.py` rejects empty batches, missing or duplicate opportunity keys, and any failed source. On rejection it returns the prior accepted records instead of replacing them. Tests cover source failure preservation. Native two-cycle, concurrency, monitoring and schedule/delivery evidence remains open.
