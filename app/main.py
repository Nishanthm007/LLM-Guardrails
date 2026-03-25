from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI

from app.schemas import GenerateRequest, GenerateResponse
from app.simulator import DeterministicMockLLM

app = FastAPI(
    title="LLM Guardrails Challenge - Baseline API",
    version="0.1.0",
    description="Phase 1 baseline service without guardrails.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "1-baseline"}


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest) -> GenerateResponse:
    start = perf_counter()
    model_output = DeterministicMockLLM.generate(payload.prompt)
    latency_ms = round((perf_counter() - start) * 1000, 3)

    return GenerateResponse(
        response=model_output,
        model="deterministic-mock-v1",
        latency_ms=latency_ms,
    )
