# Phase 29 verification

Run:

```bash
make incident-dataset-generate
make incident-dataset-validate
PYTHONPATH=src:. pytest -q tests/unit/test_phase29_synthetic_incident_dataset.py
```

`make incident-dataset-seed` requires a migrated PostgreSQL database and validates the checked-in dataset before writing. The Phase 29 acceptance gate passes only when there are at least 200 incidents and the validator reports no causality, ordering, balance, leakage, hashing, topology-reference, or determinism errors.
