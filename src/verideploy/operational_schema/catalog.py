from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SchemaBinding:
    concept: str
    table: str
    introduced_phase: int
    tenant_scoped: bool = True


REQUIRED_SCHEMA_CONCEPTS = (
    "releases", "pull_requests", "commits", "incidents", "documents", "pages", "chunks",
    "visual_indexes", "investigations", "checkpoints", "reviews", "agent_runs", "tools", "models",
    "evaluations", "feedback", "jobs", "outbox", "inbox", "audit",
)

OPERATIONAL_SCHEMA_CATALOG = {
    "releases": SchemaBinding("releases", "releases_phase32", 32),
    "pull_requests": SchemaBinding("pull_requests", "pull_requests_phase32", 32),
    "commits": SchemaBinding("commits", "commits_phase32", 32),
    "incidents": SchemaBinding("incidents", "incidents_phase32", 32),
    "documents": SchemaBinding("documents", "retrieval_documents", 13),
    "pages": SchemaBinding("pages", "visual_pages", 14),
    "chunks": SchemaBinding("chunks", "retrieval_chunks", 13),
    "visual_indexes": SchemaBinding("visual_indexes", "visual_page_indexes", 14),
    "investigations": SchemaBinding("investigations", "investigations_phase32", 32),
    "checkpoints": SchemaBinding("checkpoints", "investigation_checkpoints_phase32", 32),
    "reviews": SchemaBinding("reviews", "human_reviews_phase32", 32),
    "agent_runs": SchemaBinding("agent_runs", "agent_runs_phase19", 19),
    "tools": SchemaBinding("tools", "tool_registry_phase32", 32),
    "models": SchemaBinding("models", "model_registry_phase32", 32),
    "evaluations": SchemaBinding("evaluations", "evaluations_phase32", 32),
    "feedback": SchemaBinding("feedback", "feedback_phase32", 32),
    "jobs": SchemaBinding("jobs", "jobs_phase32", 32),
    "outbox": SchemaBinding("outbox", "outbox_phase32", 32),
    "inbox": SchemaBinding("inbox", "inbox_phase32", 32),
    "audit": SchemaBinding("audit", "audit_events_phase32", 32),
}


def validate_schema_catalog() -> dict[str, object]:
    missing = sorted(set(REQUIRED_SCHEMA_CONCEPTS) - set(OPERATIONAL_SCHEMA_CATALOG))
    duplicate_tables: list[str] = []
    seen: set[str] = set()
    for binding in OPERATIONAL_SCHEMA_CATALOG.values():
        if binding.table in seen:
            duplicate_tables.append(binding.table)
        seen.add(binding.table)
        if not binding.tenant_scoped:
            raise ValueError(f"operational schema concept must be tenant scoped: {binding.concept}")
    if missing:
        raise ValueError(f"missing schema concepts: {', '.join(missing)}")
    # Reuse of a historical canonical table is intentional; duplicate concept bindings are not.
    if duplicate_tables:
        raise ValueError(f"duplicate schema table bindings: {', '.join(sorted(set(duplicate_tables)))}")
    return {
        "valid": True,
        "concept_count": len(REQUIRED_SCHEMA_CONCEPTS),
        "phase32_tables": sorted(b.table for b in OPERATIONAL_SCHEMA_CATALOG.values() if b.introduced_phase == 32),
        "reused_tables": sorted(b.table for b in OPERATIONAL_SCHEMA_CATALOG.values() if b.introduced_phase < 32),
    }
