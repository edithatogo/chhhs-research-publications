# E01 digest native repair — 22 October 2026

The digest's `DefinitionRequestMissingFields` save failure is resolved. Native
validation exposed several distinct defects in the prepared assembly:

- Two condition fragments used `Condition` instead of native `If`.
- Connector inputs retained six injected authentication properties.
- The freshness branch did not join the completed source-coverage branch, so a
  downstream loop referenced an action outside its dependency path.
- Parse JSON rejected regex patterns. The fixed `utcNow()` producer preserves
  UTC; explicit canonical date comparisons preserve the date-shape checks.
- Extending an already long completeness expression exceeded the native limit.
  A small additional guard now gates the same rendering path, retaining the
  original completeness expression.

The supported Dataverse save returned 204. Independent service readback proves
the complete 58-action executable graph: manual trigger, existing used connection
identities, source/coverage/freshness gates, no email action and false send
authority. The compiler omits only the local query-template fingerprint from the
definition and the unused Outlook reference from executable references. The
original full preimages and fingerprint remain private.

The first manual no-send run reached the Power BI query. It exposed a separate
runtime defect: single-letter date format strings produced a month/day label and
a short date inside DAX `DATE()`. Numeric `MM` and `dd` formats are now saved and
read back. This is a repaired runtime defect, not yet full digest runtime
acceptance. No email was sent or production schedule enabled.

The pure preparation helper is `scripts/digest_native_definition.py`. Four focused
tests cover nested branches, retained bindings/guards, idempotence, numeric date
formats and refusal of unexpected UTC-producer/dependency changes. The existing
local digest builder calls it; that previously untracked builder remains local
and is not included in an unrelated broad commit.

The second run proved numeric DAX construction but exposed 21 optional enrichment
fields absent from the selected native `Publication` table. Its saved model
definition confirms 30 canonical fields. The explicit source projection now uses
those fields, retains all required identity/abstract/date/link inputs and reports
unavailable optional fields without inventing values. The source query and
coverage branch then passed. The third run exposed historical bootstrap commit
markers without ModelID/ProcessingChain. Inventory parsing now accepts that older
shape, while the exact model/workspace/history/materialization admission condition
is unchanged; absent steps become an empty inventory. The fourth run passed this
inventory path and failed closed at `Require_current_pubmed_source_manifest` with
`ok=false`. No qualified source manifest met the current 24-hour window. A genuine
qualified PubMed source materialization/commit is required before prompt/render
qualification can continue. Do not weaken freshness or relabel this technical
dependency as a later E08 observation.

Independent source-archive inspection confirms the latest PubMed marker with a
processing chain records source materialization completed on 12 October at
15:48:38 UTC. Later top-level commit files concern OpenAlex, not a newer PubMed
materialization. The freshness failure therefore has a concrete source-age basis.
The repaired digest is Stopped, with exact final readback, all 58 actions intact,
the email action replaced by Compose and send authority false.

The writer's one-query manual qualification succeeded natively: 1,341 canonical
publications, 1,274 retained PubMed rows, 709 retained DoRA rows and 1,983 history
rows. This proves its actual model readiness query, not registry write/recovery
or concurrency acceptance. A historical-run resubmit was denied for another
initiator; no run was created. A fresh supported browser run succeeded after the
manual trigger name was corrected. The original complete writer and Stopped
state must be restored after controlled qualification.

Controlled writer qualification subsequently passed: the full row projection
returned one genuine canonical record; the seven-action bounded upsert and its
fresh replay both succeeded. Independent complete register keysets remained
exactly 1,648 IDs/keys. Record 1573 retained every existing substantive value;
the upsert filled empty `SourceFullTitle` from the exact preserved title, and
replay changed only run metadata. The full CSV export was untouched. Supported
restoration returned 204; independent native readback proves the original complete
11-action graph, connection references and Stopped state exactly. This is bounded
technical runtime/replay/restoration evidence, not a newly claimed full-register
rewrite or production activation.

Crossref's same recovery handle remains Running. The complete stored folder
inventory contains 1,007 DOI result files (indices 0–1006), all 27 query archives
previously qualified, and no generation manifest. Its last observed DOI file was
written at 15:48:20 UTC on 21 October. Preserve this run and last-good generation;
an active run and partial stored results do not prove generation completion.

Private evidence remains in `private/ops/2026-10-21-e01-runtime-qualification/`,
including the native definition acceptance, first digest run/action output,
numeric-date candidate, writer readiness terminal run/output and pending restore
checkpoint. The preserved Crossref recovery handle remains authoritative; do not
resubmit it. Full output reconciliation and remaining controlled technical cases
stay in E01. Later natural occurrences and elapsed operating windows stay in E08.
