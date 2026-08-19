# ADR-0020 — Complete operational schema while reusing canonical RAG tables

## Decision
Keep Phase 13 retrieval documents/chunks, Phase 14 visual pages/indexes, and Phase 19 agent runs as the canonical tables. Add only missing Phase 32 operational tables and expose one authoritative schema catalog.

## Rationale
Duplicating RAG or agent-run storage would create inconsistent truth and migrations. Phase 32 is a completeness phase, not a storage rewrite. Lifecycle state changes are guarded in application code and PostgreSQL; tenant identity is enforced by RLS plus link-validation triggers.
