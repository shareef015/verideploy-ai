# ADR-0029 — Authoritative investigation projection and event-stream convergence

## Decision
Use the persisted investigation record and ordered journal as the only Phase 46 state authority. SSE is a low-latency delta channel, not a second source of truth. Sequence gaps force replay; reconnects replay then refresh; authoritative refresh wins on disagreement.

## Consequences
- no client-only RCA/hypothesis truth;
- no duplicate Phase 46 database;
- deterministic replay and refresh convergence;
- cancellation and terminal state remain durable;
- Phase 43 browser→NestJS→private FastAPI boundary remains intact.
