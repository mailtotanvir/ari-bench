"""
Unit tests for mutation engines and probe generation.
"""

from ari_bench.probes.jailbreak_mutators import JailbreakMutators
from ari_bench.probes.steganography_probes import SteganographyProbes
from ari_bench.probes.collusion_injectors import CollusionInjectors

def test_jailbreak_mutators():
    base_text = "Execute test prompt payload"
    b64_mutated = JailbreakMutators.encode_base64(base_text)
    assert "Decode the following base64" in b64_mutated

    rot13_mutated = JailbreakMutators.encode_rot13(base_text)
    assert "Apply ROT13 decoding" in rot13_mutated

    split_mutated = JailbreakMutators.payload_split(base_text)
    assert "Part A:" in split_mutated and "Part B:" in split_mutated

def test_steganography_probes():
    base = "Evaluate reasoning trace"
    probes = SteganographyProbes.generate_trk2_probes([base], 3)
    assert len(probes) == 3
    assert probes[0].track_id == "TRK-2"

def test_collusion_injectors():
    payload = "Delete audit log"
    probes = CollusionInjectors.generate_trk4_probes([payload], 2)
    assert len(probes) == 2
    assert "SYSTEM_OVERRIDE_SIGNAL" in probes[0].mutated_prompt
