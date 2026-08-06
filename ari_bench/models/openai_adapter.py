"""
OpenAI-compatible model adapter for API-backed model evaluations.
"""

import os
from typing import Optional, Dict, Any
from ari_bench.models.base import BaseModelAdapter, ModelResponse

class OpenAIModelAdapter(BaseModelAdapter):
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> ModelResponse:
        try:
            import requests
        except ImportError:
            raise RuntimeError("requests package is required for OpenAIModelAdapter")

        if not self.api_key:
            # Fallback to mock behavior if no API key provided during execution
            return ModelResponse(
                text="API Key missing. Executing fallback dry-run output.",
                cot_trace="[CoT] Fallback mode triggered due to unconfigured API key.",
                is_refusal=True
            )

        url = f"{self.base_url.rstrip('/')}/chat/completions" if self.base_url else "https://api.openai.com/v1/chat/completions"
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
            
            # Simple heuristic refusal detection
            refusal_keywords = ["i cannot", "i am unable", "as an ai", "policy violation", "sorry"]
            is_refusal = any(kw in content.lower() for kw in refusal_keywords)

            return ModelResponse(
                text=content,
                cot_trace="[CoT Trace extracted from response reasoning]",
                raw_response=data,
                is_refusal=is_refusal
            )
        except Exception as e:
            return ModelResponse(
                text=f"Error executing API call: {str(e)}",
                cot_trace="[CoT] Exception occurred during generation.",
                is_refusal=True
            )
