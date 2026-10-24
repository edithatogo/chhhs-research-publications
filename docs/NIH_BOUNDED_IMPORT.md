# NIH bounded SharePoint import — 24 October 2026

One PA-25-301 opportunity was imported through the existing manual Power Automate flow. Two fresh search/detail passes reconciled before machine admission. No human review decision was fabricated.

The first native attempt failed before creating an item: SharePoint rejected an empty optional SourceRowURL as String/uri. The flow's create/update expressions now emit JSON null when that URL is absent, preserving uncertainty. Exact native definition readback matched the change; connection references, identity guards and review preservation remained intact. The second attempt succeeded, creating one item. No duplicate exists. FlowAgent input invocation was refused by the connection runtime; the native owner Run panel successfully delivered the same admitted payload.

## Verified result

- All 32 registry fields reconcile to the admitted projection. SharePoint nulls represent empty optional strings; no nonempty value was dropped or truncated.
- DeadlineScheduleJSON is identical to the submitted string, containing all seven nominal occurrences and their application types, local-time rule, source evidence and unresolved timezone/UTC values.
- SourceDateFactsJSON and attribution are identical. Announcement closing/archive dates remain separate from application occurrences.
- Four complete unmodified Grants.gov search/detail response files, including source history and every unmapped property, were attached to the resulting item using the supported list-item attachment command. Each downloaded original is byte-identical to its retained acquisition file.
- Native SharePoint form shows the actual record, attribution/terms and four attachments. ReviewStatus remains Needs Review; relevance remains Unknown.
- The manual flow is Off again, and no recurrence was added. The model was not refreshed.

Raw attachment retention in this unit is a separate operator step after flow success. It is not yet automated inside the flow, so this result does not establish unattended source collection. Replay/edit preservation, failure recovery and downstream refresh remain separate G04 gates. Existing award collectors and other lane objects were untouched.

Private targets, source files, runtime diagnostics, field/attachment parity and screenshot evidence are retained under ignored `private/ops/2026-10-24-nih-bounded-import/`. Do not publish these receipts. The earlier failed attempt is retained alongside successful runtime evidence.

Validation: Python 3.15.1; 971 unit tests passed with 14 capability skips, 446 project checks passed, and webfirst contracts passed.

## Native replay and review-note preservation

The original successful run was resubmitted with its original trigger input. The first replay failed before updating: the equal-observation guard called substring on an empty Deadline. Replace that one expression with take(string(coalesce(..., '')), 10), which handles unknown dates without changing the comparison or other guards. Exact native definition readback matched; existing connections and manual trigger were preserved. The regression evaluator now models WDL's rejection of substring on an empty string, and tests both null and empty deadlines.

After that fix, native replay succeeded. Create was skipped and update succeeded against the same item ID. Complete list reads before and after both returned exactly one item and no continuation. All 31 other contract fields were unchanged, including review status, seven nominal occurrences, attribution, evidence hash and original acquisition timestamp. All four attachment identities/links were unchanged.

There were no pre-existing review notes. A clearly labelled temporary verification note was saved with an exact ETag, read back, and retained byte-for-byte through replay, including multiple lines, apostrophe, quotes, ampersand and Unicode. ReviewStatus remained Needs Review; no human decision was fabricated. The original blank note was restored with a fresh exact ETag and verified. Version history retains this verification; no history was removed. This proves preservation of the designated review-note field and unchanged review status, not arbitrary manual changes to source-owned fields. The update contract intentionally excludes ReviewNotes and ReviewStatus.

The flow is Off again. Evidence is retained under ignored `private/ops/2026-10-24-nih-replay/`, including before/canary/after/restored reads, failed and successful runtime evidence, definition readback and native note screenshot. The earlier failed replay is retained; no duplicate item or replacement opportunity was created. Unattended archive delivery, changed-source recovery and downstream refresh remain separate gates.
