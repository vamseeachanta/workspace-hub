#!/usr/bin/env python3
"""Generate AI Agent Capability Radar HTML from YAML config.

Usage:
    uv run --no-project python scripts/ai/generate-agent-radar.py
    uv run --no-project python scripts/ai/generate-agent-radar.py --output /tmp/radar.html
    uv run --no-project python scripts/ai/generate-agent-radar.py --open  # generate + xdg-open

Reads:  config/ai-tools/agent-capability-scores.yaml
Writes: config/ai-tools/agent-capability-radar.html (default)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCORES_PATH = REPO_ROOT / "config" / "ai-tools" / "agent-capability-scores.yaml"
DEFAULT_OUT = REPO_ROOT / "config" / "ai-tools" / "agent-capability-radar.html"


def load_yaml(path: Path) -> dict:
    """Minimal YAML loader — avoids PyYAML dependency for hub scripts."""
    try:
        import yaml  # noqa: F811

        return yaml.safe_load(path.read_text())
    except ImportError:
        pass
    # Fallback: use Python's json via a quick yq-style parse
    try:
        result = subprocess.run(
            ["python3", "-c", f"import yaml, json, sys; print(json.dumps(yaml.safe_load(open('{path}'))))"],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"ERROR: Cannot parse {path}. Install PyYAML: uv add pyyaml", file=sys.stderr)
        sys.exit(1)


def build_dataset_js(agents: dict, is_dashed: bool = False) -> str:
    """Build Chart.js datasets array from agent config."""
    datasets = []
    for key, agent in agents.items():
        ds = {
            "label": agent["label"],
            "data": agent["scores"],
            "borderColor": agent["color"],
            "backgroundColor": agent["color"] + "1a",
            "borderWidth": 2.5,
            "pointRadius": 3,
            "pointBackgroundColor": agent["color"],
        }
        if is_dashed:
            ds["borderDash"] = [4, 3]
            ds["borderWidth"] = 1.5
        datasets.append(ds)
    return json.dumps(datasets, indent=6)


def build_legend_rows_providers(agents: dict) -> str:
    """Build HTML table rows for provider comparison legend."""
    rows = []
    for agent in agents.values():
        badge = agent.get("badge", {})
        badge_html = ""
        if badge:
            badge_html = f' <span class="badge {badge["class"]}">{badge["text"]}</span>'
        rows.append(
            f'      <tr>'
            f'<td><span class="swatch" style="background:{agent["color"]}"></span>'
            f'{agent["label"].split(" (")[0]}{badge_html}</td>'
            f'<td>{agent["role"]}</td>'
            f'<td>{agent["default_model"]}</td>'
            f'<td>{agent["cost_display"]}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def build_legend_rows_tiers(models: dict) -> str:
    """Build HTML table rows for Claude tier legend."""
    risk_colors = {"HIGH": "#f07c7c", "LOW": "#7cf0a0", "MINIMAL": "#7cf0a0"}
    rows = []
    for model in models.values():
        rc = risk_colors.get(model["quota_risk"], "#ccc")
        rows.append(
            f'      <tr>'
            f'<td><span class="swatch" style="background:{model["color"]}"></span>'
            f'{model["label"]}</td>'
            f'<td>{model["route"]}</td>'
            f'<td style="color:{rc}">{model["quota_risk"]}</td>'
            f'<td>{model["effort"]}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def build_routing_notes(notes: list[str]) -> str:
    """Build HTML list items from routing notes."""
    items = []
    for note in notes:
        # Convert **bold** to <strong>
        import re
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", note)
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
        html = html.replace("&", "&amp;").replace("&amp;mdash;", "&mdash;")
        items.append(f"    <li>{html}</li>")
    return "\n".join(items)


def generate_html(cfg: dict) -> str:
    """Generate the full HTML radar chart from config."""
    pc = cfg["provider_comparison"]
    ct = cfg["claude_tiers"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    provider_labels = json.dumps(pc["dimensions"])
    provider_datasets = build_dataset_js(pc["agents"])
    provider_legend = build_legend_rows_providers(pc["agents"])

    tier_labels = json.dumps(ct["dimensions"])
    tier_datasets = build_dataset_js(ct["models"])
    tier_legend = build_legend_rows_tiers(ct["models"])

    routing_html = build_routing_notes(cfg.get("routing_notes", []))

    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Capability Radar — Workspace Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background: #0f1117; color: #e0e0e0;
        min-height: 100vh; display: flex; flex-direction: column;
        align-items: center; padding: 24px;
      }}
      h1 {{ font-size: 1.5rem; font-weight: 600; margin-bottom: 4px; color: #fff; }}
      .subtitle {{ font-size: 0.85rem; color: #888; margin-bottom: 20px; }}
      .container {{
        display: flex; flex-wrap: wrap; gap: 24px; justify-content: center;
        max-width: 1400px; width: 100%;
      }}
      .chart-card {{
        background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px;
        padding: 20px; flex: 1 1 580px; max-width: 680px; min-width: 400px;
      }}
      .chart-card h2 {{
        font-size: 1.1rem; font-weight: 500; margin-bottom: 12px;
        color: #ccc; text-align: center;
      }}
      .chart-wrapper {{ position: relative; width: 100%; max-height: 480px; }}
      .legend-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 0.8rem; }}
      .legend-table th {{
        text-align: left; padding: 6px 8px; border-bottom: 1px solid #333;
        color: #888; font-weight: 500;
      }}
      .legend-table td {{ padding: 5px 8px; border-bottom: 1px solid #222; }}
      .legend-table .swatch {{
        display: inline-block; width: 12px; height: 12px; border-radius: 2px;
        margin-right: 6px; vertical-align: middle;
      }}
      .notes {{
        background: #14161e; border: 1px solid #2a2d3a; border-radius: 12px;
        padding: 16px 20px; max-width: 1400px; width: 100%; margin-top: 8px;
        font-size: 0.82rem; line-height: 1.6; color: #999;
      }}
      .notes h3 {{ color: #bbb; font-size: 0.9rem; margin-bottom: 8px; }}
      .notes ul {{ padding-left: 18px; }}
      .notes li {{ margin-bottom: 4px; }}
      .notes code {{ background: #222; padding: 1px 5px; border-radius: 3px; font-size: 0.78rem; }}
      .badge {{
        display: inline-block; font-size: 0.7rem; padding: 1px 6px;
        border-radius: 4px; margin-left: 4px; vertical-align: middle;
      }}
      .badge-primary {{ background: #1e3a5f; color: #7cb3f0; }}
      .badge-gate {{ background: #4a2020; color: #f07c7c; }}
      .badge-research {{ background: #1e4a2a; color: #7cf0a0; }}
      .badge-alt {{ background: #3a3a1e; color: #e0d07c; }}
      .timestamp {{ font-size: 0.75rem; color: #555; margin-top: 16px; text-align: center; }}
    </style>
    </head>
    <body>
    <h1>AI Agent Capability Radar</h1>
    <p class="subtitle">Workspace-hub multi-agent ecosystem &mdash; capability profiles for routing decisions</p>
    <div class="container">
      <div class="chart-card">
        <h2>Provider Comparison (Default Models)</h2>
        <div class="chart-wrapper"><canvas id="providerRadar"></canvas></div>
        <table class="legend-table">
          <tr><th>Agent</th><th>Role</th><th>Default Model</th><th>Cost Tier</th></tr>
    {provider_legend}
        </table>
      </div>
      <div class="chart-card">
        <h2>Claude Model Tiers (Internal Routing)</h2>
        <div class="chart-wrapper"><canvas id="claudeRadar"></canvas></div>
        <table class="legend-table">
          <tr><th>Model</th><th>Route</th><th>Quota Risk</th><th>Effort</th></tr>
    {tier_legend}
        </table>
      </div>
    </div>
    <div class="notes">
      <h3>Routing Quick Reference</h3>
      <ul>
    {routing_html}
      </ul>
    </div>
    <p class="timestamp">Generated: {ts} | Source: config/ai-tools/agent-capability-scores.yaml | Script: scripts/ai/generate-agent-radar.py</p>
    <script>
    Chart.defaults.color = '#999';
    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
    Chart.defaults.font.size = 11;
    const scaleOpts = {{
      r: {{
        min: 0, max: 10,
        ticks: {{ stepSize: 2, backdropColor: 'transparent', color: '#555', font: {{ size: 10 }} }},
        grid: {{ color: '#2a2d3a' }},
        angleLines: {{ color: '#2a2d3a' }},
        pointLabels: {{ color: '#bbb', font: {{ size: 12, weight: 500 }} }}
      }}
    }};
    new Chart(document.getElementById('providerRadar'), {{
      type: 'radar',
      data: {{ labels: {provider_labels}, datasets: {provider_datasets} }},
      options: {{
        responsive: true, maintainAspectRatio: true,
        plugins: {{
          legend: {{ position: 'top', labels: {{ boxWidth: 14, padding: 12, usePointStyle: true }} }},
          tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': ' + ctx.raw + '/10' }} }}
        }},
        scales: scaleOpts
      }}
    }});
    new Chart(document.getElementById('claudeRadar'), {{
      type: 'radar',
      data: {{ labels: {tier_labels}, datasets: {tier_datasets} }},
      options: {{
        responsive: true, maintainAspectRatio: true,
        plugins: {{
          legend: {{ position: 'top', labels: {{ boxWidth: 14, padding: 12, usePointStyle: true }} }},
          tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': ' + ctx.raw + '/10' }} }}
        }},
        scales: scaleOpts
      }}
    }});
    </script>
    </body>
    </html>
    """)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI Agent Capability Radar HTML")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUT, help="Output HTML path")
    parser.add_argument("--scores", "-s", type=Path, default=SCORES_PATH, help="Scores YAML path")
    parser.add_argument("--open", action="store_true", help="Open in browser after generation")
    args = parser.parse_args()

    if not args.scores.exists():
        print(f"ERROR: Scores file not found: {args.scores}", file=sys.stderr)
        sys.exit(1)

    cfg = load_yaml(args.scores)
    html = generate_html(cfg)
    args.output.write_text(html)
    print(f"Generated: {args.output} ({len(html):,} bytes)")

    if args.open:
        try:
            subprocess.run(["xdg-open", str(args.output)], check=False)
        except FileNotFoundError:
            print("xdg-open not available; open the file manually.", file=sys.stderr)


if __name__ == "__main__":
    main()
