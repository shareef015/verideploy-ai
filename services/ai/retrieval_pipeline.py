from __future__ import annotations
from functools import lru_cache

from services.ai.retrieval import get_hybrid_retriever
from verideploy.config import get_settings
from verideploy.database.factory import create_database_manager
from verideploy.rag.orchestration.postgres_parent import PostgresParentResolver
from verideploy.rag.orchestration.repository import PostgresRetrievalPipelineTraceRepository
from verideploy.rag.orchestration.service import RetrievalPipeline


@lru_cache
def get_retrieval_pipeline() -> RetrievalPipeline:
    settings = get_settings()
    if not settings.database_url.startswith("postgresql"):
        raise RuntimeError("retrieval orchestration runtime requires PostgreSQL/pgvector")
    db = create_database_manager(settings)
    return RetrievalPipeline(
        retriever=get_hybrid_retriever(),
        parent_resolver=PostgresParentResolver(db),
        traces=PostgresRetrievalPipelineTraceRepository(db),
    )
