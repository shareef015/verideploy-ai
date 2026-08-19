# ADR-0009 — Keep RAGAgent reasoning separate from retrieval execution

## Status
Accepted in Phase 20.

## Decision
The RAGAgent may produce only a validated query-analysis plan. Retrieval execution remains behind an internal `RAGRetrievalPort` implemented by the Phase 13 `HybridRetriever`. The model cannot construct SQL, select arbitrary backends, bypass tenant metadata, or declare its own evidence sufficient.

Trusted service/environment scope overrides omission and blocks conflicting model-generated scope. Query expansion is bounded by schema and tool budget. Evidence sufficiency is deterministic.

## Consequences

- Tool selection is directly unit-testable.
- Keyword-only operation provably avoids embedding cost.
- Dense-only operation provably avoids full-text search.
- Historical incident/runbook/architecture filtering is consistent across lexical and dense channels.
- Agent runs remain reproducible through Phase 19 prompt/input hashing and tool-usage persistence.
- Later agents can consume an explicit insufficient-evidence state instead of assuming retrieval always succeeded.
