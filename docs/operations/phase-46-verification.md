# Phase 46 verification

Run `python scripts/validate_incident_screen.py` and `pytest -q tests/unit/test_phase46_incident_investigation_screen.py`.

The acceptance gate is satisfied only when replay from the durable journal and authoritative refresh project the same investigation state, and the frontend contains explicit sequence-gap/replay/reconciliation logic.
