# Verified federal and Queensland sources

Deliver a maintained official-source catalogue whose admitted records can be reconciled to stable source identifiers. Cover GrantConnect, NHMRC, MRFF, ARC, Queensland government/QH, EMF and local funders with explicit verified, unavailable, reviewed-import-only or out-of-scope decisions. Do not equate breadth of discovery with implemented intake.

Automated intake is official RSS/Atom/API only. ARC awards and Queensland CKAN catalogue metadata remain separate entity classes and cannot become open opportunities. A newsletter, landing page, aggregator or successful HTTP response does not establish a machine endpoint. Reviewed import must retain official row provenance; no scraping or inferred opportunity identity.

The maintained ARC awards and Queensland Grants Finder metadata rows have
immutable entity/admission classes in both catalogue validation and the
independent ingestion boundary. A catalogue edit or caller-supplied row cannot
relabel either required source as an opportunity to bypass the source
qualification contract; new opportunity routes require their own source IDs and
evidence.

Acceptance requires endpoint/schema/pagination evidence, stable key and round semantics, licensing/access decision, observation time, bounded sample and reconciliation result per admitted source. Unsupported sources remain visible gaps. Endpoint drift or incomplete pages must fail closed without erasing the last accepted records.

Every maintained machine-source row records a timezone-aware `qualification.observed_at` and a status plus evidence references for `access`, `response_schema`, `bounded_sample`, `complete_pagination`, `replay_keyset`, `stable_identity`, `round_semantics`, `lifecycle_semantics`, `reuse_terms` and `entity_reconciliation`. `bounded_sample` records that a bounded source sample was captured and checked against the declared response shape; it does not substitute for full pagination, replay or lifecycle evidence. `stable_identity` covers persistent source record identity; `round_semantics` separately covers how the source identifies program/scheme and round boundaries, including changed or repeated rounds. Status is `verified`, `partial`, `unverified` or `not_applicable`; references must be safe HTTPS URLs or repository-relative paths to existing files within the repository. `access` records `public`, `existing_authorized`, `restricted`, `unavailable`, `unresolved` or `not_applicable`; public or already-authorized access requires verified access evidence. `reuse_terms` records `permitted`, `restricted`, `not_permitted`, `unresolved` or `not_applicable`; permitted reuse requires verified terms evidence. Opportunity admission is stricter: every field must be `verified`, access must be `public` or `existing_authorized`, and reuse must be `permitted`. These fields record the evidence-backed qualification state; they do not create evidence or qualify any current source by themselves.

Follow the [hardened completion contract](../../../docs/PLATFORM_COMPLETION_PLAN.md#hardened-completion-contract), [RIMS grants experience](../../../docs/RIMS_GRANTS_EXPERIENCE.md) and [delivery review](../../../docs/GRANTS_DELIVERY_REVIEW.md). The task IDs, dependency gates, exact inputs and expected evidence are in [the implementation plan](plan.md). Reuse existing resources and keep actual tenant/account identities, payloads, credentials and run evidence in ignored private storage. No local test closes a native gate.
