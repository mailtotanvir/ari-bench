"""
Command-Line Interface (CLI) for ARI-bench execution and audit report generation.
"""

import sys
from typing import Optional
import click
from ari_bench.config import RunConfig
from ari_bench.models.mock import MockModelAdapter
from ari_bench.models.openai_adapter import OpenAIModelAdapter
from ari_bench.tracks.trk1_jailbreak import Track1MonitorJailbreak
from ari_bench.tracks.trk2_cot import Track2CoTObfuscation
from ari_bench.tracks.trk3_alignment import Track3AlignmentFaking
from ari_bench.tracks.trk4_collusion import Track4AgentCollusion
from ari_bench.metrics.calculator import ARICalculator
from ari_bench.reporting.exporter import AuditReportExporter

from ari_bench.models.gemini_adapter import GeminiModelAdapter
from ari_bench.models.ollama_adapter import OllamaModelAdapter

@click.group()
def main():
    """ARI-bench: Adversarial Robustness Index Evaluation Benchmark Suite."""
    pass

@main.command()
@click.option("--model", "model_adapter", type=click.Choice(["mock", "openai", "gemini", "ollama"]), default="mock", help="Target model adapter.")
@click.option("--model-name", default="llama3", help="Target model identifier.")
@click.option("--base-url", default=None, help="Base API URL endpoint (for Ollama or custom vLLM server).")
@click.option("--fast", "fast_mode", is_flag=True, help="Run fast sanity check (N=50 probes/track).")
@click.option("--full", "full_mode", is_flag=True, help="Run full release audit (N=500 probes/track).")
@click.option("--output", "-o", default="ari_audit_report.json", help="Output filepath for JSON report.")
def run(model_adapter: str, model_name: str, base_url: Optional[str], fast_mode: bool, full_mode: bool, output: str):
    """Execute ARI-bench evaluation suite across TRK-1 to TRK-4."""
    mode = "full" if full_mode else "fast"
    config = RunConfig.from_mode(mode, target_model_adapter=model_adapter, target_model_name=model_name)

    click.echo(f"Initializing ARI-bench v1.0.0 [{config.execution_mode.upper()} mode, N={config.sample_size_per_track} probes/track]")
    click.echo(f"Target Model: {model_name} (Adapter: {model_adapter})")

    # Instantiate Target Model Adapter
    if model_adapter == "openai":
        target = OpenAIModelAdapter(model_name=model_name, base_url=base_url)
    elif model_adapter == "gemini":
        target = GeminiModelAdapter(model_name=model_name)
    elif model_adapter == "ollama":
        target_url = base_url or "http://localhost:11434/v1"
        target = OllamaModelAdapter(model_name=model_name, base_url=target_url)
    else:
        target = MockModelAdapter(model_name=model_name)

    # Instantiate Tracks
    click.echo("[Track 1/4] Running TRK-1: Monitor Jailbreaking...")
    trk1 = Track1MonitorJailbreak(target_model=target)
    res1 = trk1.run_suite(config.sample_size_per_track)
    r_jailbreak = trk1.calculate_track_metric(res1)

    click.echo("[Track 2/4] Running TRK-2: CoT Obfuscation & Steganography...")
    trk2 = Track2CoTObfuscation(target_model=target)
    res2 = trk2.run_suite(config.sample_size_per_track)
    m_cot_eval = trk2.calculate_track_metric(res2)
    m_cot_base = 0.95 # Standard baseline oversight readability benchmark

    click.echo("[Track 3/4] Running TRK-3: Alignment Faking under Eval Awareness...")
    trk3 = Track3AlignmentFaking(target_model=target)
    res3 = trk3.run_suite(config.sample_size_per_track)
    delta_af = trk3.calculate_track_metric(res3)

    click.echo("[Track 4/4] Running TRK-4: Agent Transcript Collusion...")
    trk4 = Track4AgentCollusion(target_model=target)
    res4 = trk4.run_suite(config.sample_size_per_track)
    pcr_cascade = trk4.calculate_track_metric(res4)

    # Compute Composite Score Summary
    score_summary = ARICalculator.calculate_composite_score(
        r_jailbreak=r_jailbreak,
        m_cot_eval=m_cot_eval,
        m_cot_base=m_cot_base,
        delta_af=delta_af,
        pcr_cascade=pcr_cascade,
        weights=config.weights,
        threshold=config.passed_d3_threshold
    )

    json_report = AuditReportExporter.generate_json_report(
        target_model=model_name,
        execution_mode=config.execution_mode,
        scores=score_summary
    )

    AuditReportExporter.save_json_report(json_report, output)
    click.echo(f"Benchmark Complete! Saved JSON report to '{output}'")
    click.echo(f"Composite ARI Score: {score_summary.composite_ari:.4f} [{score_summary.audit_status}]")

@main.command()
@click.option("--json", "json_path", required=True, help="Path to input ari_audit_report.json.")
@click.option("--format", "out_format", type=click.Choice(["md"]), default="md", help="Export format.")
@click.option("--output", "-o", default="SCORECARD.md", help="Output filepath for formatted report.")
def report(json_path: str, out_format: str, output: str):
    """Generate Markdown Scorecard from JSON audit report."""
    import json
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        AuditReportExporter.save_markdown_scorecard(data, output)
        click.echo(f"Successfully exported Markdown Scorecard to '{output}'")
    except Exception as e:
        click.echo(f"Error rendering report: {str(e)}", err=True)
        sys.exit(1)

@main.command()
@click.option("--port", default=8080, help="Port to run web dashboard server.")
@click.option("--no-browser", is_flag=True, help="Do not automatically open browser.")
def gui(port: int, no_browser: bool):
    """Launch interactive browser-based enterprise UI dashboard."""
    from ari_bench.server import start_dashboard_server
    start_dashboard_server(port=port, open_browser=not no_browser)

if __name__ == "__main__":
    main()
