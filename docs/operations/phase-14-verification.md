# Phase 14 verification

Run:

```bash
PYTHONPATH=src:. pytest -q
PYTHONPATH=src:. python scripts/benchmark_visual_retrieval.py
PYTHONPATH=src:. alembic upgrade head --sql
```

Live PostgreSQL verification additionally requires `TEST_POSTGRES_URL` and runs the Phase 12–14 integration suites. A ColPali runtime additionally requires compatible `transformers`, `torch`, model weights, and sufficient hardware; the default test suite never downloads model weights.
