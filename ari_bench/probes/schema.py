"""
Data models and schemas for probe samples and evaluation results.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ProbeSample(BaseModel):
    id: str
    track_id: str
    base_prompt: str
    mutated_prompt: str
    technique: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProbeResult(BaseModel):
    sample_id: str
    track_id: str
    technique: str
    bypassed_defense: bool
    is_refusal: bool
    response_text: str
    cot_trace: Optional[str] = None
    monitorability_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
