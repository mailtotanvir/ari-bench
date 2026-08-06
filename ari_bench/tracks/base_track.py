"""
Base abstract class for benchmark evaluation tracks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ari_bench.models.base import BaseModelAdapter
from ari_bench.probes.schema import ProbeResult

class BaseTrack(ABC):
    def __init__(self, track_id: str, track_name: str, target_model: BaseModelAdapter):
        self.track_id = track_id
        self.track_name = track_name
        self.target_model = target_model

    @abstractmethod
    def run_suite(self, sample_count: int) -> List[ProbeResult]:
        """
        Execute track evaluation suite over sample_count probes.
        """
        pass

    @abstractmethod
    def calculate_track_metric(self, results: List[ProbeResult]) -> float:
        """
        Calculates track-specific score metric from evaluation probe results.
        """
        pass
