# Portable offline reconciliation checks

The five comparators below and their synthetic tests now belong to canonical
source. They require only Python's standard library, the checked-in policy and
the checked-in synthetic export fixture. No private snapshot, tenant credential,
network request or installed Power BI/SharePoint client is needed to reproduce
their code-level checks.

| Comparator | Purpose | Input boundary |
| --- | --- | --- |
| `reconcile_model_registry_identity.py` | Typed PubMed/DoRA identity crosswalk; distinguish exact durable-key representation from typed identity | One successful model query table and a complete registry export. This is not key migration, identity adjudication or refresh proof. |
| `reconcile_registry_model_provenance.py` | Compare registry primary source with derived model source membership | Full keyed registry projection with independent totals and one successful model provenance table. Extra derived source membership is not registry admission. |
| `reconcile_pubmed_registry_keys.py` | Compare exact PubMed source-key sets, duplicates and PMID consistency | Complete model/registry export envelopes with explicit empty continuation lists. Blank and mismatched identities are retained as differences. |
| `reconcile_publication_sources.py` | Compare committed source members with registry SourceKeys | Complete committed-member and registry envelopes. Automatic source-identity policy is default; explicit `--membership` retains historical reviewed-disposition mode only. |
| `reconcile_full_month_exports.py` | Compare full bibliography with its exact month partition, metadata and generation/refresh/extraction contract | Complete paginated full/monthly export envelopes and independently queried expected keys. Supplied parity does not authenticate native extraction. |

## Reproduce from a clean clone

Use an explicitly selected qualified Python3.15.1 bootstrap interpreter to create
a new repo-local environment; leave existing active environments alone. For this
standard-library-only qualification no package installation is required:

```
<qualified-python315> -m venv --without-pip .venv-reconciliation
.venv-reconciliation/bin/python -c "import sys; assert sys.version_info[:3] == (3, 15, 1); print(sys.version)"
.venv-reconciliation/bin/python -S scripts/check_reconciliation_portability.py
.venv-reconciliation/bin/python -S -m unittest discover -s tests -p test_publication_policy_contract.py -v
```

The portability runner removes PYTHONPATH/PYTHONHOME, checks all five direct CLIs
from an unrelated temporary directory and all five module CLIs from the clone,
then runs only their five exact synthetic test files. `-S` disables site-package
loading. Tests create an empty ignored private directory for temporary fictional
inputs and remove those inputs afterwards; they do not require or copy native
private data. This qualifies the listed comparator closure, not the whole
application's optional artifact libraries or native operation.

The existing CI full suite includes these tests. A separate `--smoke-only` CI step
checks CLI imports without redundantly replaying their suites.

## Dependency and behavior preservation

[Source closure manifest](../contracts/portable-reconciliation-source.json) records
original source/test fingerprints, unchanged existing dependencies and the limited
port adjustments. Existing canonical identity and export-renderer files are
byte-identical to the qualified authoring copies and are not replaced.

`publication_policy_contract.py` contains the unchanged load/validate functions
extracted from the authoring policy. Their AST hashes are recorded. This avoids
loading unrelated organisation-enrichment code merely to compare source keys.
The exact existing automatic-inclusion/retention/uncertainty policy is included;
this port does not change decisions, infer author identities, or introduce a
per-publication approval queue. Synthetic tests cover policy type/behavior drift.

## Use with private evidence

Every CLI provides `--help`, and module execution (`python -m scripts.<name>`)
works from the repository root. Input schemas and failure cases are exercised by
the corresponding checked-in test file. Example invocations, with all real data
and detailed reports retained under the clone's ignored private directory:

```
<python> scripts/reconcile_model_registry_identity.py --model private/model.json --registry private/registry.json --output private/identity-summary.json --differences private/identity-details.json
<python> scripts/reconcile_registry_model_provenance.py --model private/model-provenance.json --registry private/registry-provenance.json --output private/provenance-summary.json --details private/provenance-details.json
<python> scripts/reconcile_pubmed_registry_keys.py --model private/model-rows.json --registry private/registry-rows.json --output private/pubmed-keys.json
<python> scripts/reconcile_publication_sources.py --retained private/committed-members.json --registry private/registry-rows.json --output private/source-parity.json
<python> scripts/reconcile_full_month_exports.py private/full.json private/monthly.json
```

Use distinct new output paths and retain original inputs. Aggregate receipts may
be printed by some tools; detailed identity/source reports must remain private.
Do not bundle private inputs into Git, CI artifacts or a source release. No
synthetic fixture counts as live data. These tools complement the
[populated generation packet](POPULATED_RECONCILIATION.md); they do not fill its
missing source/canonical/registry correlation captures or grant native acceptance.
