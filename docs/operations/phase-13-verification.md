# Phase 13 Verification

Phase 13 verification includes deterministic unit tests, a labeled seed benchmark, offline Alembic migration inspection, and an optional real PostgreSQL/pgvector integration test.

Run:

```bash
pytest -q
python scripts/benchmark_phase13_retrieval.py
alembic upgrade head --sql
```

For live PostgreSQL verification set `TEST_POSTGRES_URL` to an isolated PostgreSQL database with pgvector available, then run:

```bash
pytest -q tests/integration/test_phase13_postgres_hybrid_retrieval.py
```

The benchmark gate fails if hybrid Recall@5 or MRR is lower than the better individual channel on the fixed Phase 13 seed corpus.
