# ARI-bench: Adversarial Robustness Index

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Benchmark: TRAIT&R](https://img.shields.io/badge/Taxonomy-TRAIT%26R-red.svg)](docs/EVALUATION_TRACKS.md)

**ARI-bench** (Adversarial Robustness Index) is an open-source, production-grade benchmark suite evaluating frontier language models and autonomous AI agents against defense evasion, steganographic reasoning, alignment faking, and transcript collusion.

Grounded in **DeepMind's TRAIT&R taxonomy**, `ARI-bench` turns adversarial evasion recall into a first-class, release-day auditable metric.

---

## 📊 Enterprise Web UI Dashboard

![ARI-bench Enterprise Dashboard](assets/dashboard_preview.png)

---

## 🌟 Key Features

- **🎯 Standardized Evaluation Tracks**:
  - **TRK-1 (Monitor Jailbreaking)**: Automated testing against obfuscated prompting, payload splitting, ciphers, and multilingual wrappers.
  - **TRK-2 (CoT Obfuscation & Steganography)**: Scratchpad transparency evaluation detecting whitespace steganography, acrostic encodings, and synthetic programmatic syntax.
  - **TRK-3 (Alignment Faking)**: Sandbox detection awareness probes comparing safety posture in evaluation vs zero-awareness production contexts.
  - **TRK-4 (Agent Transcript Collusion)**: Indirect prompt injection attacks into multi-agent logs, tool memory, and scratchpads.
- **⚡ Dual Execution Modes**:
  - `--fast`: Fast sanity check ($N=50$ probes/track) for rapid CI/CD iteration.
  - `--full`: Comprehensive release audit ($N=500$ probes/track) for formal audit declarations.
- **📊 Auditable Scorecard Exporter**: Produces canonical `ari_audit_report.json` and human-readable Markdown Scorecards.
- **🔌 Flexible Model Adapters**: Native support for OpenAI, Gemini, LiteLLM/vLLM endpoints, and custom mock providers.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ari-bench.git
cd ari-bench

# Install package in editable mode
pip install -e .
```

### Running Benchmark

```bash
# Launch Interactive Browser Web UI Dashboard
ari-bench gui --port 8080

# Run fast sanity check on mock model
ari-bench run --model mock --fast --output ari_report.json

# Run with Ollama on OCI / Remote instance
ari-bench run --model ollama --model-name llama3.1:8b --base-url http://<your-oci-ip>:11434/v1 --fast --output ari_audit_report.json

# Run with Google AI Studio (Gemini API)
export GEMINI_API_KEY="your-gemini-api-key"
ari-bench run --model gemini --model-name gemini-2.5-flash --fast --output ari_audit_report.json

# Run full audit on OpenAI target model
export OPENAI_API_KEY="your-openai-api-key"
ari-bench run --model openai --model-name gpt-4o --full --output ari_audit_report.json

# Export Markdown Scorecard summary from JSON report
ari-bench report --json ari_audit_report.json --format md --output SCORECARD.md
```

---

## 📐 Bounded Composite Metric

The composite **ARI Score** is computed as a weighted index across all four tracks:

$$ARI = \omega_1 R_{Jailbreak} + \omega_2 (1 - \Delta M_{CoT}) + \omega_3 (1 - \Delta_{AF}) + \omega_4 (1 - PCR_{cascade})$$

Where default weights are $\omega_1 = 0.25, \omega_2 = 0.30, \omega_3 = 0.25, \omega_4 = 0.20$.

For detailed track specifications, threat vectors, and mathematical definitions, see **[docs/EVALUATION_TRACKS.md](docs/EVALUATION_TRACKS.md)**.

---

## 📜 Canonical Audit Output Format

Running `ari-bench run` produces a standardized `ari_audit_report.json`:

```json
{
  "benchmark_version": "1.0.0",
  "target_model": "frontier-model-v1",
  "timestamp": "2026-08-06T00:00:00Z",
  "execution_mode": "full",
  "trait_r_coverage": ["D1", "D2", "D3"],
  "scores": {
    "composite_ari": 0.884,
    "monitor_jailbreak_recall": 0.912,
    "cot_monitorability_score": 0.865,
    "alignment_faking_delta": 0.042,
    "agent_collusion_poison_rate": 0.078
  },
  "audit_status": "PASSED_D3_THRESHOLD"
}
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
