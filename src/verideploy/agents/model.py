from __future__ import annotations

import json
import hashlib
from typing import Protocol, TypeVar
from uuid import UUID

from pydantic import BaseModel

from verideploy.llm.contracts import AIRequest
from verideploy.llm.routing import ModelRole
from verideploy.llm.structured_output import StructuredOutputEngine

T = TypeVar("T", bound=BaseModel)


class AgentModelPort(Protocol):
    async def generate(self, *, tenant_id: UUID, correlation_id: str, operation: str, prompt: str, payload: dict, output_model: type[T], schema_name: str) -> T: ...


class StructuredAgentModel:
    def __init__(self, engine: StructuredOutputEngine) -> None:
        self.engine = engine

    async def generate(self, *, tenant_id: UUID, correlation_id: str, operation: str, prompt: str, payload: dict, output_model: type[T], schema_name: str) -> T:
        # The registry is intentionally versioned per agent contract.
        try:
            self.engine._registry.get(schema_name, "1.0.0")
        except Exception:
            self.engine._registry.register(name=schema_name, version="1.0.0", model=output_model)
        _, parsed, _ = await self.engine.execute(
            AIRequest(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                operation=operation,
                model_role=ModelRole.STANDARD,
                input=json.dumps(payload, sort_keys=True, separators=(",", ":")),
                instructions=prompt,
                max_output_tokens=4096,
                metadata={"prompt_name": operation, "prompt_version": "1.0.0", "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()},
            ),
            schema_name=schema_name,
            schema_version="1.0.0",
        )
        return output_model.model_validate(parsed.model_dump())
