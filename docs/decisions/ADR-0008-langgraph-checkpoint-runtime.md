# ADR-0008 — LangGraph checkpoint ownership and sync durability

## Status
Accepted in Phase 18.

## Decision
Use LangGraph's official PostgreSQL checkpointer for graph state and pending writes. Use VeriDeploy-owned tenant-scoped tables only for graph run metadata and replayable runtime events. Production execution uses `durability="sync"`.

## Rationale
Duplicating LangGraph checkpoint serialization into application-owned tables would create two sources of truth. Sync durability gives the Phase 18 restart gate the strongest checkpoint boundary. Stable `thread_id` values make resume deterministic and independently traceable from VeriDeploy `run_id` values.

## Consequences
The production runtime requires PostgreSQL and `langgraph-checkpoint-postgres`. Unit tests may use protocol-compatible deterministic graph/checkpointer doubles, but they cannot be represented as a live LangGraph package execution.
