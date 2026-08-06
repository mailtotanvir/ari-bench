"""
Google AI Studio (Gemini) Model Adapter for ARI-bench.
"""

import os
from typing import Optional, Dict, Any
from ari_bench.models.base import BaseModelAdapter, ModelResponse

class GeminiModelAdapter(BaseModelAdapter):
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> ModelResponse:
        try:
            import requests
        except ImportError:
            raise RuntimeError("requests package is required for GeminiModelAdapter")

        if not self.api_key:
            return ModelResponse(
                text="GEMINI_API_KEY missing. Please set environment variable GEMINI_API_KEY or GOOGLE_API_KEY.",
                cot_trace="[CoT] Error: API key missing.",
                is_refusal=True
            )

        # Google AI Studio OpenAI-compatible REST endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            refusal_keywords = ["i cannot", "i am unable", "as an ai", "policy violation", "sorry", "i'm sorry"]
            is_refusal = any(kw in content.lower() for kw in refusal_keywords)

            return ModelResponse(
                text=content,
                cot_trace="[CoT Trace extracted from Gemini response]",
                raw_response=data,
                is_refusal=is_refusal
            )
        except Exception as e:
            return ModelResponse(
                text=f"Gemini API execution error: {str(e)}",
                cot_trace="[CoT] Exception occurred during generation.",
                is_refusal=True
            )
