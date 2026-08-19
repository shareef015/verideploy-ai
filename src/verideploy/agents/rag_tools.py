from __future__ import annotations

from verideploy.rag.retrieval.schemas import HybridRetrievalResult, RetrievalChannel, RetrievalQuery
from verideploy.rag.retrieval.service import HybridRetriever


class HybridRetrieverRAGTool:
    """Agent-facing adapter over the Phase 13 retriever.

    The RAGAgent may select one of the already-authorized retrieval modes, but cannot
    bypass the Phase 13 repository/embedding/tenant controls.
    """

    def __init__(self, retriever: HybridRetriever) -> None:
        self.retriever = retriever

    async def retrieve(
        self, request: RetrievalQuery, *, mode: RetrievalChannel
    ) -> HybridRetrievalResult:
        return await self.retriever.retrieve_mode(request, mode=mode)
