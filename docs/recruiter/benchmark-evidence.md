# Measured Engineering Evidence

This page lists values already produced by repository test/evaluation artifacts. It does not convert estimates or CI-only gates into measured local facts.

| Area | Measured evidence | Source |
|---|---:|---|
| Phase 80 cumulative regression | 700 passed / 0 failed | `evals/reports/release-candidate-benchmarks.json` |
| Python coverage | 87.32% | same Phase 80 benchmark report |
| Critical mutation probes | 4/4 killed | same Phase 80 benchmark report |
| Security critical findings | 0 | same Phase 80 benchmark report |
| Final contract families | 9 | Phase 71/80 contract evidence |
| Phase 76 Hybrid Recall@5 | 1.0 | `evals/reports/rag-performance.json` |
| Phase 76 Hybrid MRR | 1.0 | Phase 76 report |
| Phase 77 aggregate path score | 1.0 | `evals/reports/agentic-orchestration.json` |
| Phase 78 clean traceability | 1.0 | `evals/reports/multimodal-integration.json` |
| Phase 79 critical operational gaps | 0 | `evals/reports/production-operations.json` |
| Phase 82 architecture nodes | 15 | `evals/reports/final-production-architecture.json` |
| Phase 82 production data-flow edges | 19 | Phase 82 report |
| Phase 83 evidence-backed skill claims | 14 | `evals/reports/ai-engineering-jd-mapping.json` |

## Benchmark interpretation rules
- Phase 76 sub-millisecond clean-index latency is an **in-process deterministic benchmark**, not production network latency.
- Phase 74 latency/cost fields are **configured/estimated synthetic-demo values**, not production billing evidence.
- Phase 80 browser execution is CI-enforced where local Playwright dependencies were unavailable; unexecuted local browser tests are not reported as local passes.
