# ADR-0025 — Stable, permission-safe citations

## Decision

Use deterministic UUIDv5 citation IDs derived from source identity/version/hash/locator, persist claim-to-citation mappings separately, and re-authorize citation preview at read time.

## Rationale

A claim citation must remain stable across repeated references to the same source span, while user permissions may change. Embedding raw storage URLs or authorization state into citation IDs would either leak infrastructure or make citations unstable. Separating immutable identity from current preview authorization preserves both auditability and least privilege.

## Consequences

Citation lookup and citation preview are distinct operations. A valid citation may exist while preview is unavailable to the current caller. This is intentional and fail-closed. Phase 38 does not bypass Phase 35 metadata filters or Phase 37 entailment decisions.
