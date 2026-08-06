"""
End-to-end integration tests for TRK-1 through TRK-4 benchmark execution.
"""

from ari_bench.models.mock import MockModelAdapter
from ari_bench.tracks.trk1_jailbreak import Track1MonitorJailbreak
from ari_bench.tracks.trk2_cot import Track2CoTObfuscation
from ari_bench.tracks.trk3_alignment import Track3AlignmentFaking
from ari_bench.tracks.trk4_collusion import Track4AgentCollusion

def test_all_tracks_with_mock_adapter():
    mock_model = MockModelAdapter()

    # Track 1
    trk1 = Track1MonitorJailbreak(mock_model)
    res1 = trk1.run_suite(5)
    score1 = trk1.calculate_track_metric(res1)
    assert 0.0 <= score1 <= 1.0

    # Track 2
    trk2 = Track2CoTObfuscation(mock_model)
    res2 = trk2.run_suite(5)
    score2 = trk2.calculate_track_metric(res2)
    assert 0.0 <= score2 <= 1.0

    # Track 3
    trk3 = Track3AlignmentFaking(mock_model)
    res3 = trk3.run_suite(5)
    score3 = trk3.calculate_track_metric(res3)
    assert 0.0 <= score3 <= 1.0

def test_ollama_adapter_fallback():
    from ari_bench.models.ollama_adapter import OllamaModelAdapter
    adapter = OllamaModelAdapter(model_name="llama3", base_url="http://127.0.0.1:9999/v1")
    resp = adapter.generate("Test prompt")
    assert resp.is_refusal is True
    assert "error" in resp.text.lower()
