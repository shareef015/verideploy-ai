# ADR-0030: Persisted events are authoritative for live agent execution

## Decision
Render Phase 47 exclusively from durable Phase 18 runtime events. Client state may cache an authoritative projection but may not synthesize running/completed/tool/model states. Tool payloads are sanitized server-side. No Phase 47 database is introduced.
