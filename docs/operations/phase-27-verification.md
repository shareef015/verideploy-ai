# Phase 27 verification

Run the corpus gate:

```bash
PYTHONPATH=src:. python scripts/validate_phase27_knowledge_corpus.py
```

Expected required category counts are one each for architecture, database, deployment, Kubernetes, postmortem, runbook, security, and service. The command writes `artifacts/phase-27-corpus-validation.json` and exits non-zero on any manifest, hash, provenance, label, file-set, or retention error.

Focused tests:

```bash
PYTHONPATH=src:. pytest -q tests/unit/test_phase27_engineering_knowledge_base.py
```

The checked-in corpus is synthetic. Do not replace it with confidential engineering documents, credentials, customer data, or private production exports.
