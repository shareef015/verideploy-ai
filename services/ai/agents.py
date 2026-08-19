from __future__ import annotations

from functools import lru_cache

from services.ai.ai_gateway import get_ai_gateway
from verideploy.agents.factory import create_agent_runtime_components
from verideploy.agents.planner import PlanningAgent
from verideploy.agents.rag import RAGAgent
from verideploy.agents.rag_tools import HybridRetrieverRAGTool
from verideploy.agents.visual import VisualEvidenceAgent
from verideploy.agents.runtime import RuntimeEvidenceAgent
from verideploy.agents.rca import RCAAgent
from verideploy.agents.critic import CriticAgent, HybridCriticFollowupRetrieval
from verideploy.agents.runtime_tools import LiveRuntimeEndpoints, LiveRuntimeTool, RuntimeSource, SyntheticRuntimeTool
from verideploy.config import get_settings
from verideploy.agents.visual_tools import StoredVisualAnalysisTool, VisualDocumentSearchTool
from verideploy.agents.supervisor import SupervisorAgent
from services.ai.retrieval import get_hybrid_retriever
from services.ai.visual_retrieval import get_visual_retrieval_service
from services.ai.image_intelligence import get_image_intelligence_service


@lru_cache
def get_supervisor_agent() -> SupervisorAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return SupervisorAgent(model=model, prompts=prompts, repository=repository)


@lru_cache
def get_planning_agent() -> PlanningAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return PlanningAgent(model=model, prompts=prompts, repository=repository)


@lru_cache
def get_rag_agent() -> RAGAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return RAGAgent(
        model=model,
        prompts=prompts,
        repository=repository,
        retrieval=HybridRetrieverRAGTool(get_hybrid_retriever()),
    )


@lru_cache
def get_visual_evidence_agent() -> VisualEvidenceAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return VisualEvidenceAgent(
        model=model,
        prompts=prompts,
        repository=repository,
        search=VisualDocumentSearchTool(get_visual_retrieval_service()),
        analyzer=StoredVisualAnalysisTool(get_image_intelligence_service()),
    )


@lru_cache
def get_runtime_evidence_agent() -> RuntimeEvidenceAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    settings = get_settings()
    if settings.runtime_evidence_adapter == "live":
        endpoints = LiveRuntimeEndpoints(
            prometheus_url=settings.prometheus_base_url, grafana_url=settings.grafana_base_url,
            tempo_url=settings.tempo_base_url, loki_url=settings.loki_base_url,
            bearer_token=settings.runtime_observability_token.get_secret_value() if settings.runtime_observability_token else None,
        )
        tools = {source: LiveRuntimeTool(source, endpoints, timeout_seconds=settings.runtime_http_timeout_seconds) for source in RuntimeSource}
    else:
        tools = {source: SyntheticRuntimeTool(source) for source in RuntimeSource}
    return RuntimeEvidenceAgent(model=model, prompts=prompts, repository=repository, tools=tools)


@lru_cache
def get_rca_agent() -> RCAAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return RCAAgent(model=model, prompts=prompts, repository=repository)


@lru_cache
def get_critic_agent() -> CriticAgent:
    model, prompts, repository = create_agent_runtime_components(gateway=get_ai_gateway())
    return CriticAgent(
        model=model, prompts=prompts, repository=repository,
        followup=HybridCriticFollowupRetrieval(HybridRetrieverRAGTool(get_hybrid_retriever())),
    )
