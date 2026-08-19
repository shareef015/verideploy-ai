# Phase 32 verification

Run:

```bash
PYTHONPATH=src:. python scripts/validate_schema.py
pytest -q tests/unit/test_phase32_operational_schema.py
pytest -q
DATABASE_URL=postgresql+psycopg://... alembic upgrade 0014_phase32_complete_operational_schema --sql
DATABASE_URL=postgresql+psycopg://... alembic downgrade 0014_phase32_complete_operational_schema:0013_phase31_evidence_graph --sql
```

A provisioned PostgreSQL run additionally uses `TEST_POSTGRES_URL` to test lifecycle rejection, outbox idempotency, append-only audit, and tenant-link enforcement.
