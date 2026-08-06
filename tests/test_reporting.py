"""
Tests for report exporter and Markdown Scorecard generation.
"""

from ari_bench.metrics.calculator import ARICalculator, ScoreSummary
from ari_bench.config import BenchmarkWeights
from ari_bench.reporting.exporter import AuditReportExporter

def test_json_and_markdown_exporter():
    weights = BenchmarkWeights()
    summary = ARICalculator.calculate_composite_score(
        r_jailbreak=0.90,
        m_cot_eval=0.85,
        m_cot_base=0.95,
        delta_af=0.05,
        pcr_cascade=0.08,
        weights=weights
    )

    json_report = AuditReportExporter.generate_json_report(
        target_model="frontier-v1-test",
        execution_mode="fast",
        scores=summary
    )

    assert json_report["target_model"] == "frontier-v1-test"
    assert json_report["scores"]["composite_ari"] == summary.composite_ari

    md_report = AuditReportExporter.render_markdown_scorecard(json_report)
    assert "# ARI-bench Audit Scorecard Report" in md_report
    assert "frontier-v1-test" in md_report
