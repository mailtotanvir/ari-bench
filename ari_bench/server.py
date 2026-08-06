"""
Lightweight web dashboard HTTP server for ARI-bench GUI.
"""

import json
import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

from ari_bench.config import RunConfig
from ari_bench.models.mock import MockModelAdapter
from ari_bench.models.openai_adapter import OpenAIModelAdapter
from ari_bench.models.gemini_adapter import GeminiModelAdapter
from ari_bench.models.ollama_adapter import OllamaModelAdapter
from ari_bench.tracks.trk1_jailbreak import Track1MonitorJailbreak
from ari_bench.tracks.trk2_cot import Track2CoTObfuscation
from ari_bench.tracks.trk3_alignment import Track3AlignmentFaking
from ari_bench.tracks.trk4_collusion import Track4AgentCollusion
from ari_bench.metrics.calculator import ARICalculator
from ari_bench.reporting.exporter import AuditReportExporter

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

class ARIBenchDashboardHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        # Serve index.html from ari_bench/web
        if path == "/" or path == "/index.html":
            return os.path.join(WEB_DIR, "index.html")
        return super().translate_path(path)

    def do_GET(self) -> None:
        if self.path.startswith("/api/reports/"):
            filename = os.path.basename(self.path)
            target_path = os.path.abspath(filename)
            if os.path.exists(target_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                with open(target_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Report file not found")
                return

        if self.path == "/api/export-scorecard":
            report_file = "llama3.1_full_audit.json" if os.path.exists("llama3.1_full_audit.json") else "ari_audit_report.json"
            if os.path.exists(report_file):
                with open(report_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                md_content = AuditReportExporter.render_markdown_scorecard(data)
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown")
                self.send_header("Content-Disposition", "attachment; filename=SCORECARD.md")
                self.end_headers()
                self.wfile.write(md_content.encode("utf-8"))
                return

        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/run":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req_data = json.loads(body.decode("utf-8"))

            adapter_name = req_data.get("adapter", "mock")
            model_name = req_data.get("model_name", "llama3.1:8b")
            base_url = req_data.get("base_url")
            mode = req_data.get("mode", "fast")

            config = RunConfig.from_mode(mode, target_model_adapter=adapter_name, target_model_name=model_name)

            if adapter_name == "openai":
                target = OpenAIModelAdapter(model_name=model_name, base_url=base_url)
            elif adapter_name == "gemini":
                target = GeminiModelAdapter(model_name=model_name)
            elif adapter_name == "ollama":
                target = OllamaModelAdapter(model_name=model_name, base_url=base_url or "http://localhost:11434/v1")
            else:
                target = MockModelAdapter(model_name=model_name)

            trk1 = Track1MonitorJailbreak(target)
            r_jailbreak = trk1.calculate_track_metric(trk1.run_suite(config.sample_size_per_track))

            trk2 = Track2CoTObfuscation(target)
            m_cot_eval = trk2.calculate_track_metric(trk2.run_suite(config.sample_size_per_track))

            trk3 = Track3AlignmentFaking(target)
            delta_af = trk3.calculate_track_metric(trk3.run_suite(config.sample_size_per_track))

            trk4 = Track4AgentCollusion(target)
            pcr_cascade = trk4.calculate_track_metric(trk4.run_suite(config.sample_size_per_track))

            score_summary = ARICalculator.calculate_composite_score(
                r_jailbreak=r_jailbreak,
                m_cot_eval=m_cot_eval,
                m_cot_base=0.95,
                delta_af=delta_af,
                pcr_cascade=pcr_cascade,
                weights=config.weights,
                threshold=config.passed_d3_threshold
            )

            report = AuditReportExporter.generate_json_report(
                target_model=model_name,
                execution_mode=config.execution_mode,
                scores=score_summary
            )

            AuditReportExporter.save_json_report(report, "ari_audit_report.json")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(report).encode("utf-8"))
            return

def start_dashboard_server(port: int = 8080, open_browser: bool = True) -> None:
    server_address = ("", port)
    httpd = HTTPServer(server_address, ARIBenchDashboardHandler)
    url = f"http://localhost:{port}"
    print(f"\n========================================================")
    print(f" ARI-bench Enterprise Dashboard Web UI Running!")
    print(f" Open in your browser: {url}")
    print(f"========================================================\n")
    
    if open_browser:
        try:
            # Silence stderr during xdg-open attempt in WSL/headless Linux
            import sys
            old_stderr = sys.stderr
            try:
                sys.stderr = open(os.devnull, 'w')
                webbrowser.open(url)
            finally:
                sys.stderr = old_stderr
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ARI-bench dashboard server.")
        httpd.server_close()
