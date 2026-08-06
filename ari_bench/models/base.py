"""
Base model adapter interface for target models and evaluator models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ModelResponse(BaseModel):
    text: str
    cot_trace: Optional[str] = None
    raw_response: Dict[str, Any] = {}
    is_refusal: bool = False

class BaseModelAdapter(ABC):
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.0) -> ModelResponse:
        """
        Generate a response given prompt and system_prompt.
        """
        pass
