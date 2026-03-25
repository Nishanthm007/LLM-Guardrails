from __future__ import annotations

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User input prompt")


class GuardrailEventModel(BaseModel):
    rule_id: str
    category: str
    severity: str
    action: str
    detail: str


class GenerateResponse(BaseModel):
    response: str
    model: str
    latency_ms: float
    trace_id: str
    guardrail_decision: str
    guardrail_events: list[GuardrailEventModel]
