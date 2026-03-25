from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI

from app.guardrails import GuardrailEngine, SAFE_FALLBACK_MESSAGE
from app.schemas import GenerateRequest, GenerateResponse, GuardrailEventModel
from app.simulator import DeterministicMockLLM

app = FastAPI(
    title="LLM Guardrails Challenge - API",
    version="0.2.0",
    description="Phase 2 adds guardrail classification, rewriting, output checks, and audit logs.",
)

guardrail_engine = GuardrailEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "2-guardrails"}


@app.post("/generate", response_model=GenerateResponse)
def generate(payload: GenerateRequest) -> GenerateResponse:
    start = perf_counter()

    input_result = guardrail_engine.process_input(payload.prompt)

    if input_result.decision == "block":
        model_output = SAFE_FALLBACK_MESSAGE
    else:
        model_output = DeterministicMockLLM.generate(input_result.safe_prompt)

    validated_output, output_events = guardrail_engine.validate_output(model_output)
    all_events = [*input_result.events, *output_events]

    final_decision = input_result.decision
    if output_events and any(event.severity == "critical" for event in output_events):
        final_decision = "block"

    latency_ms = round((perf_counter() - start) * 1000, 3)

    guardrail_engine.log_audit(
        trace_id=input_result.trace_id,
        raw_prompt=payload.prompt,
        safe_prompt=input_result.safe_prompt,
        decision=final_decision,
        events=all_events,
        model="deterministic-mock-v1",
        latency_ms=latency_ms,
    )

    return GenerateResponse(
        response=validated_output,
        model="deterministic-mock-v1",
        latency_ms=latency_ms,
        trace_id=input_result.trace_id,
        guardrail_decision=final_decision,
        guardrail_events=[GuardrailEventModel(**event.__dict__) for event in all_events],
    )
