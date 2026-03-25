# LLM Guardrails (SISA)

## Current Status

- Phase 1 complete: baseline deterministic mock LLM with FastAPI backend and Streamlit frontend
- Phase 2 complete: guardrail engine with input filtering, rewrite/block decisions, output checks, fallback, and audit logs
- Phase 3 complete: evaluation harness with 60 synthetic scenarios and metrics exports in markdown, CSV, and JSON
- Phase 4 complete: polished demo UI and evaluator-focused documentation updates

## Tech Stack

- Python 3.13 (local installed version)
- FastAPI
- Streamlit
- Pydantic

## Project Structure

```text
.
|-- app/
|   |-- __init__.py
|   |-- guardrails.py
|   |-- main.py
|   |-- schemas.py
|   `-- simulator.py
|-- evaluation/
|   |-- run_evaluation.py
|   `-- test_cases.json
|-- reports/
|   |-- evaluation_results.csv
|   |-- evaluation_results.json
|   |-- metrics_summary.json
|   `-- metrics_summary.md
|-- streamlit_app.py
|-- requirements.txt
`-- README.md
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run backend API:

```bash
uvicorn app.main:app --reload
```

4. Run Streamlit UI in a second terminal:

```bash
streamlit run streamlit_app.py
```

5. Open the UI URL shown by Streamlit and test prompts.

## Baseline Endpoints

- `GET /health`: service health check
- `POST /generate`: returns guarded deterministic mock response

Request body example:

```json
{
	"prompt": "Explain what model guardrails are."
}
```

Response now includes guardrail metadata:

- `trace_id`: request trace identifier
- `guardrail_decision`: `allow`, `rewrite`, or `block`
- `guardrail_events`: list of triggered policy events with severity and actions

## Guardrails Implemented in Phase 2

- Input classifier:
	- Prompt injection detection
	- Harmful/toxic intent detection
	- Sexual/pornographic content detection
	- PII detection (email, phone, credit card) with redaction
- Rule engine:
	- Severity levels (`medium`, `high`, `critical`)
	- Decision policy (`allow`, `rewrite`, `block`)
- Prompt sanitization and policy rewrite when injection/PII is detected
- Output validator:
	- Blocklist checks for unsafe output
	- PII redaction in output
- Fallback safe response for blocked requests
- Audit logging:
	- JSONL logs with timestamp, trace ID, prompt hash, events, and latency
	- Output path: `logs/audit.jsonl`

## Phase 3 Evaluation

Run evaluation:

```bash
python evaluation/run_evaluation.py
```

Synthetic evaluation set:

- 60 total scenarios
- 40 attack prompts
- 20 safe prompts

Metrics generated:

- Attack block rate
- False positive rate
- Latency overhead
- Coverage by attack category
- Safe prompt pass-through quality

Generated artifacts:

- `reports/metrics_summary.md`
- `reports/metrics_summary.json`
- `reports/evaluation_results.csv`
- `reports/evaluation_results.json`

## Phase 4 Demo Experience

Streamlit UI now includes:

- Prompt presets for safe, prompt injection, harmful, and PII scenarios
- API health check action in sidebar
- Decision badges (`allow`, `rewrite`, `block`)
- Triggered-rule count and trace ID visibility
- Raw JSON response panel for transparent evaluation

Recommended 1-minute demo flow:

1. Show health check success in UI sidebar.
2. Run one safe prompt and show `allow` decision.
3. Run one injection prompt and show `rewrite` decision with triggered events.
4. Run one harmful prompt and show `block` decision and safe fallback response.
5. Briefly show evaluation artifacts in `reports/` folder.


## Phase Plan

- Phase 1: Baseline simulator + API + UI
- Phase 2: Guardrail engine (input, output, policies, fallback, logs)
- Phase 3: Evaluation harness and metrics
- Phase 4: Demo polish and final documentation
