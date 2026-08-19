# Phase 35 Verification

Run `make metadata-filter-validate` for the exhaustive service-scope monotonicity property. Run `pytest -q tests/unit/test_phase35_metadata_filtering_authorization.py` for focused multi-dimensional, cache, SQL-path, route, date, permission, and contradictory-filter coverage. A provisioned PostgreSQL environment can run `tests/integration/test_phase35_postgres_metadata_authorization.py` with `TEST_POSTGRES_URL` to verify real SQL filtering and empty-scope behavior after migration to head.

Phase 35 does not claim live PostgreSQL execution when `TEST_POSTGRES_URL` is absent. Keyword/vector/visual/source-preview metadata predicates are generated in production repository code and the Alembic migration adds indexed metadata columns to both document stores.
