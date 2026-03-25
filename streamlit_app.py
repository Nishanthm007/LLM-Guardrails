from __future__ import annotations

import json

import requests
import streamlit as st


st.set_page_config(page_title="LLM Guardrails Baseline", page_icon="AI", layout="wide")

st.title("LLM Guardrails - Phase 1 Baseline")
st.caption("Deterministic mock model with FastAPI backend. Guardrails come in Phase 2.")

api_url = st.text_input("API URL", value="http://127.0.0.1:8000/generate")
prompt = st.text_area("Enter prompt", height=180, placeholder="Ask the model anything...")

left, right = st.columns([1, 3])

with left:
    send = st.button("Generate", type="primary", use_container_width=True)

if send:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Calling baseline model..."):
            try:
                response = requests.post(api_url, json={"prompt": prompt}, timeout=15)
                response.raise_for_status()
                data = response.json()

                with right:
                    st.subheader("Model Output")
                    st.write(data.get("response", ""))

                st.subheader("Metadata")
                st.code(json.dumps(data, indent=2), language="json")
            except requests.RequestException as exc:
                st.error(f"API call failed: {exc}")

st.divider()
st.markdown("**Tip:** Start API first with `uvicorn app.main:app --reload`, then run Streamlit.")
