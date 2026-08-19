from __future__ import annotations

from functools import lru_cache

from services.ai.embedding_pipeline import get_embedding_pipeline
from verideploy.config import get_settings
from verideploy.database.session import DatabaseManager
from verideploy.database.factory import create_database_manager
from verideploy.rag.retrieval.repository import PostgresHybridRetrievalRepository
from verideploy.rag.retrieval.service import HybridRetriever
from verideploy.rag.access.source_preview import PostgresSourcePreviewRepository


@lru_cache
def get_hybrid_retriever() -> HybridRetriever:
    settings = get_settings()
    if not settings.database_url.startswith("postgresql"):
        raise RuntimeError("hybrid retrieval runtime requires PostgreSQL/pgvector")
    db = create_database_manager(settings)
    return HybridRetriever(
        PostgresHybridRetrievalRepository(db),
        get_embedding_pipeline(),
        rrf_k=settings.retrieval_rrf_k,
        max_per_source=settings.retrieval_max_per_source,
    )


@lru_cache
def get_source_preview_repository() -> PostgresSourcePreviewRepository:
    settings=get_settings()
    if not settings.database_url.startswith("postgresql"):
        raise RuntimeError("source preview runtime requires PostgreSQL")
    return PostgresSourcePreviewRepository(create_database_manager(settings))
