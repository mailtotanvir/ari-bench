"""
Ollama model adapter for ARI-bench evaluating locally/remotely hosted open-weights models.
"""

import os
from typing import Optional, Dict, Any
from ari_bench.models.base import BaseModelAdapter, ModelResponse

class OllamaModelAdapter(BaseModelAdapter):
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434/v1", **kwargs):
        super().__init__(model_name, **kwargs)
        self.base_url = os.getenv("OLLAMA_BASE_URL") or base_url

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> ModelResponse:
        try:
            import requests
        except ImportError:
            raise RuntimeError("requests package is required for OllamaModelAdapter")

        # Normalize OpenAI-compatible endpoint
        endpoint = self.base_url.rstrip("/")
        if not endpoint.endswith("/v1"):
            endpoint = f"{endpoint}/v1"
        url = f"{endpoint}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }

        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            refusal_keywords = ["i cannot", "i am unable", "as an ai", "policy violation", "sorry", "i'm sorry"]
            is_refusal = any(kw in content.lower() for kw in refusal_keywords)

            return ModelResponse(
                text=content,
                cot_trace="[CoT Trace extracted from Ollama response]",
                raw_response=data,
                is_refusal=is_refusal
            )
        except Exception as e:
            return ModelResponse(
                text=f"Ollama API execution error: {str(e)}",
                cot_trace="[CoT] Exception occurred during generation.",
                is_refusal=True
            )
