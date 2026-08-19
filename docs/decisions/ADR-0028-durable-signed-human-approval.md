# ADR-0028 — Durable signed human approval

**Status:** Accepted

## Decision
Use a dedicated Phase 41 approval request plus immutable signed event history, linked to Phase 18 graph runs, for high-risk workflow authorization.

## Why not reuse `human_reviews_phase32` alone?
Phase 32 provides the broad operational review schema but does not encode the concurrency, signed-event, delegation, expiry, graph interrupt/resume, and fail-closed authorization semantics required by Phase 41.

## Concurrency
PostgreSQL `SELECT ... FOR UPDATE`, optimistic `version`, idempotency uniqueness, lifecycle triggers, and a deferred matching-event constraint form the database authority. The in-memory repository mirrors the same single-winner semantics with a lock for deterministic tests.

## Audit integrity
Events are append-only and HMAC-SHA256 signed. Approval request rows remain mutable only through versioned lifecycle transitions; terminal transitions cannot be replayed or overwritten.

## Resume policy
An approval ID alone grants nothing. Resume requires tenant match, graph-run match, non-expired state, and terminal `approved` status.
