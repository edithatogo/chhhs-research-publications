# Grant operational acceptance

Accept the integrated grants system through repeated native runs, controlled failures and recoverability, not merely successful imports or local validation. Preserve last accepted data and review work when sources, connections or downstream actions fail. Reconcile source/list/model/export keys and make source health, freshness, rejected batches and recovery visible.

Mandatory gates are two consecutive complete cycles (including unchanged replay and changed record), concurrency/idempotency, actionable failure monitoring, least-privilege access, restore rehearsal and documented operational ownership. Publication counts remain unchanged. Activation, external delivery, publication/sharing and capacity each retain their separate explicit approval boundary; an unactivated service is not operationally mature.

Follow the [hardened completion contract](../../../docs/PLATFORM_COMPLETION_PLAN.md#hardened-completion-contract), [RIMS grants experience](../../../docs/RIMS_GRANTS_EXPERIENCE.md) and [delivery review](../../../docs/GRANTS_DELIVERY_REVIEW.md). The task IDs, dependency gates, exact inputs and expected evidence are in [the implementation plan](plan.md). Reuse existing resources and keep actual tenant/account identities, payloads, credentials and run evidence in ignored private storage. No local test closes a native gate.
