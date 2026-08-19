from .base import BaseAgent
from .contracts import AgentAuthorization, AgentName, AgentRequest, SupervisorDecision, ToolBudget

class SupervisorAgent(BaseAgent[SupervisorDecision]):
    agent_name=AgentName.SUPERVISOR; prompt_name="supervisor"; output_model=SupervisorDecision; schema_name="agent_supervisor_decision"
    prompt_version="1.5.0"

    async def run(self, request: AgentRequest, *, authorization: AgentAuthorization) -> SupervisorDecision:
        budget=ToolBudget(max_calls=0)
        output, run=await self._generate(request, authorization=authorization, budget=budget, payload={"objective": request.objective, "context": request.context, "allowed_permissions": sorted(p.value for p in authorization.allowed_permissions)})
        try: authorization.require(output.required_permissions)
        except Exception as exc:
            self.repository.fail(tenant_id=request.tenant_id, run_id=run.run_id, error_code=type(exc).__name__, tool_calls_used=0); raise
        self.repository.complete(tenant_id=request.tenant_id, run_id=run.run_id, output=output.model_dump(mode="json"), tool_calls_used=0)
        return output
