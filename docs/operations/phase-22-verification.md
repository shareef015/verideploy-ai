# Phase 22 Verification

Run `python -m pytest -q tests/unit/test_phase22_runtime_evidence_agent.py` and `python -m pytest -q`.

The focused suite verifies UTC/time-zone equivalence, immutable baseline windows, permission/scope enforcement, pre-execution budgets, deterministic synthetic data, live read-only HTTP contracts, live-query scope rejection, source-failure degradation, anomaly extraction, Phase 15 evidence compatibility, prompt/routing contracts, and private API authorization.

No live observability endpoints are contacted by default. Live adapters are tested with `httpx.MockTransport`.
