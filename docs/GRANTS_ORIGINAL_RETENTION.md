# Automated original retention for the admitted NIH opportunity

The existing Power Automate reviewed-import flow now retains and reopens the
complete source files before updating the already-admitted NIH parent. Direct
operator attachment uploads are no longer required. The separate acquisition
flow's scheduled full-response/ZIP archival proof remains in
[NIH recurring qualification](NIH_RECURRING_QUALIFICATION.md).

Qualification is owner-run and limited to the selected admitted opportunity.
Reviewed rows and a validated `OriginalResponsesJson` envelope remain producer
inputs. Unattended projection/admission/register/model orchestration is separate;
this increment does not activate it or admit another source opportunity.

## Retention and admission contract

`grants_import_originals.py` prepares `grants-originals-v1` from all four complete
current/replay responses, every declared attachment-folder ZIP and the reviewed
projection. It checks all projection fields and evidence-hash provenance,
semantic replay, source date facts, folder metadata, complete ZIP coverage, CRC
and members. It preserves exact input bytes and calculates file SHA256/lengths.
`--source-observed-at` retains original producer timestamp spelling when it differs
from normalized UTC; the helper does not guess a spelling to force a hash match.

The flow requires the envelope for NIH rows, binds it to source identity and
observation, validates decoded source content and expected roles, and serializes
its own runs. JSON is retained through SharePoint's REST `AttachmentFiles/add`
operation, with the original UTF-8 text and explicit octet-stream content type.
ZIPs use the qualified binary attachment operation. Reads use `GetFileContent`
with `inferContentType=false`; every saved base64 payload must equal its input.

Names are deterministic: `raw-original-<EvidenceHash>-<role>.json` for the four
JSON files and `original-<EvidenceHash>-attachment-folder-<id>.zip` for ZIPs.
Only missing names are created; existing files are reopened and compared. A
same-name byte conflict fails without overwriting it. Explicit retry policies
are disabled on the new connector operations. Native SHA256 recomputation and
complete projection admission remain producer responsibilities; the native gate
independently verifies identity/roles and saved-byte equality.

Missing NIH parents fail at `Guard_NIH_Parent_Already_Admitted` before `PostItem`.
First-time NIH parent admission is unqualified and is not silently performed by
this retention flow. Other sources retain their existing create behavior.
Existing-item originals are retained before observation-order checks, so a
rejected older observation may retain additional evidence files while accepted
typed values remain unchanged. This is not a multi-record transaction or atomic
protection against external writers.

## Native findings and qualified route

The existing flow/workflow identities and original logical SharePoint reference
were retained. Its original `runtimeSource=invoker` connection-reference map was
restored exactly and read back. A temporary Embedded mode used during format
qualification was removed; it is not treated as an equivalent credential
boundary. Fresh native owner runs used the original valid caller connection,
without account switching. Other callers and run-only permission trimming are
not qualified by these owner-only tests.

The installed FlowAgent Dataverse update path preserved stored references but
ignored supplied reference repairs. A stale unpublished draft also blocked a
published update. The supported native designer removed only the qualification
draft after candidate/preimage preservation; a complete, same-record PAC
clientdata update then restored the original map. The exact target/name and Off state were checked; stopped-state/clientdata
preconditions were used for saved updates. This Power Fx pre-read is not atomic ETag protection.
Native save/readback remained separate from runtime proof.

Native publishing rejected legacy connector authentication annotations and regex
`pattern` properties in Parse JSON schemas. Known rejected annotations were
removed; source hashing remains validated by the producer and supported schema
bounds remain native. Unknown authentication annotations are rejected locally.

`CreateAttachment` reformatted JSON despite byte-exact octet-stream inputs and
`.bin` names. A semantic JSON comparison would have missed that defect. Raw REST
JSON creation plus binary readback passed instead. Eight reformatted diagnostic
attachments remain preserved and are not counted as byte-exact originals.
[Microsoft documents the attachment REST route](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest)
and [connector operations](https://learn.microsoft.com/en-us/connectors/sharepointonline/).

## Actual outcomes — 24 October 2026

| Check | Result |
| --- | --- |
| Full original retention | Four JSON bodies and the declared ZIP independently downloaded and matched exact bytes, SHA256 and lengths; ZIP CRC/member checks pass |
| Earlier operator originals | All four remain byte-exact |
| Same-input replay | No new parent or attachment; existing accepted-field update/ISO actions still execute and can advance the parent version |
| Incomplete envelope | Fails before row processing; full parent/version/attachment frame unchanged |
| Whitespace-only byte conflict | Producer semantic admission passes, native byte gate fails; no attachment/source update; full parent version unchanged |
| Fictional missing-parent input | Explicitly not an admitted projection; fails at the intended parent guard with no parent/attachment creation; registry stays one accepted parent |
| Valid recovery | Succeeds after negative cases with all five byte gates passing |
| Final Invoker mode | Fresh owner success, incomplete/conflict/missing-parent negatives and recovery pass |
| Preservation | All accepted fields/review fields remain unchanged; all 17 file identities, ETags, lengths and modification times remain stable across replay/negative/recovery checks |
| Delivery and state | Both grants flows Off; both native owner failure-email subscriptions read back false; no email/delivery actions in this importer |

The 17 files comprise four earlier operator originals, five qualified automated
originals and eight preserved diagnostic files. Initial raw REST creation was
qualified using the same owner's existing physical connection in temporary
Embedded mode; the final owner replay/recovery and preservation checks use the
restored original Invoker map. No other caller's access is inferred.

The canonical export/source reconciliation is recorded in
[the sanitized manifest](../contracts/grants-original-retention-reconciliation-20261024.json).
The existing grants acceptance document is updated in place through the existing
versioned publisher; raw receipts, native bindings and source payloads remain
private. The shared guide, diagrams, Loop and marker retain their owners.

The inherited failure-email subscription was enabled in the preimage and was
explicitly disabled before the remaining fault tests. Absence of delivery actions
is separate from that subscription readback; no historical mail-delivery claim is
made. Daily operation, recurring register/model refresh and delivered failure
alerts remain separate unqualified gates.
