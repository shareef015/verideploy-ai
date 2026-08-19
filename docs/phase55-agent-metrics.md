# Phase 55 — Agent Metrics

Phase 55 adds deterministic, execution-aware evaluation for VeriDeploy's multi-agent and LangGraph workflows. It evaluates what the agent system *did*, not only the final prose answer.

## Metrics

- **Routing accuracy** — exact expected-vs-actual supervisor route.
- **Planning quality** — order-aware sequence F1 using longest-common-subsequence overlap between expected and actual plan steps.
- **Tool-selection correctness** — set F1 over expected and actually selected tools.
- **Task completion** — binary completion against the evaluation contract.
- **Tool success** — successful tool executions divided by attempted tool executions.
- **Retry efficiency** — full credit inside the case retry budget and a bounded penalty for excess retries.
- **Escalation accuracy** — expected-vs-actual human escalation behavior.
- **LangGraph path correctness** — order-aware sequence F1 over expected and persisted workflow node paths.
- **Failure-to-trace linkage** — percentage of failure records containing both an OpenTelemetry trace ID and span ID.

The report retains raw retry counts separately so operators can inspect operational churn without hiding it inside a composite score.

## Failure linkage

Every benchmark failure record includes `case_id`, `category`, `correlation_id`, `failure_id`, `component`, `trace_id`, and `span_id`. This connects Phase 55 evaluation failures to the Phase 47 persisted execution timeline, Phase 48 LLMOps correlation model, and Phase 50 OpenTelemetry traces.

## Dataset and gate

The deterministic benchmark reuses all 500 Phase 52 cases. Each of the seven categories maps to an expected agent route, plan, tool contract, and LangGraph path. Synthetic deviations are derived only from stable SHA-256 buckets, which makes the benchmark reproducible and free of paid model calls.

Run locally:

```bash
PYTHONPATH=src python scripts/benchmark_agent_metrics.py --report evals/reports/phase55-agent-metrics.json
```

CI fails when any production threshold regresses. Model calls are not required for this gate.
