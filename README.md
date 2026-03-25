# LLM Guardrails (SISA) - Hiring Challenge

This repository contains my submission project for the AI PRISM Research Intern challenge.

## Selected Topic

- Topic 2: LLM Guardrails

## Current Status

- Phase 1 complete: baseline deterministic mock LLM with FastAPI backend and Streamlit frontend
- Guardrails are intentionally not enforced yet (implemented in Phase 2)

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
|   |-- main.py
|   |-- schemas.py
|   `-- simulator.py
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
- `POST /generate`: returns deterministic mock response

Request body example:

```json
{
	"prompt": "Explain what model guardrails are."
}
```

## Phase Plan

- Phase 1: Baseline simulator + API + UI
- Phase 2: Guardrail engine (input, output, policies, fallback, logs)
- Phase 3: Evaluation harness and metrics
- Phase 4: Demo polish and final documentation
- Phase 5: Submission assets (PPT content + final summary)
