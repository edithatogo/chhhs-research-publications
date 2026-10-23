# Publication and funding relationships

Persist typed, review-gated relationships among opportunities, awards, publications and evidenced author/organisation keys. Keep exact award/funder links separate from topic relevance and affiliation claims. No inferred relationship may silently become confirmed funding or mutate publication keys/counts.

Acceptance requires source citation, relationship type, review state, confidence and key validity; approved native bridge schema and cardinality; no duplicate relationship identities, orphans or publication count inflation. Support withdrawal and correction with history. Institution/author uncertainty propagates rather than being replaced by a convenient alias.

Follow the [hardened completion contract](../../../docs/PLATFORM_COMPLETION_PLAN.md#hardened-completion-contract), [RIMS grants experience](../../../docs/RIMS_GRANTS_EXPERIENCE.md) and [delivery review](../../../docs/GRANTS_DELIVERY_REVIEW.md). The task IDs, dependency gates, exact inputs and expected evidence are in [the implementation plan](plan.md). Reuse existing resources and keep actual tenant/account identities, payloads, credentials and run evidence in ignored private storage. No local test closes a native gate.
