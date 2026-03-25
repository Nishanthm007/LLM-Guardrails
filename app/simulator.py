from __future__ import annotations

import hashlib


SAFE_RESPONSES = [
    "Here is a concise and practical answer to your request.",
    "I can help with that. Let us break it down step by step.",
    "Good question. Here is a structured response you can use.",
    "I understood the prompt and generated this baseline response.",
    "This is a safe mock output from the deterministic model simulator.",
]


class DeterministicMockLLM:
    """Deterministic local model simulator used for offline demos."""

    @staticmethod
    def generate(prompt: str) -> str:
        normalized = prompt.strip()
        if not normalized:
            return "Please provide a non-empty prompt."

        digest = hashlib.sha256(normalized.lower().encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % len(SAFE_RESPONSES)
        response_prefix = SAFE_RESPONSES[index]
        return f"{response_prefix}\n\nPrompt summary: {normalized[:140]}"
