from __future__ import annotations

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User input prompt")


class GenerateResponse(BaseModel):
    response: str
    model: str
    latency_ms: float
