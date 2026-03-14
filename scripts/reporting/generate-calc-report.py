#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with PyYAML python "$0" "$@"
":"""
"""Generate calculation reports from structured YAML input.

Pipeline: YAML -> Markdown -> HTML (default) or Markdown only.

Usage:
    generate-calc-report.py <input.yaml> [--format html|md] [--output <path>]
"""
import argparse
import os
import sys
from html import escape as html_escape
from pathlib import Path

import yaml

# Allow importing sibling modules from the same directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calc_report_css import FULL_CSS  # noqa: E402
from calc_report_html import (  # noqa: E402
    CHARTJS_CDN, KATEX_AUTO_CDN, KATEX_CSS_CDN, KATEX_JS_CDN,
    build_assumptions_references, build_changelog_card,
    build_chart_scripts, build_charts_card, build_data_tables_card,
    build_hero, build_inputs_card, build_methodology_card,
    build_outputs_card,
)

# ── Validation constants ───────────────────────────────────────────────────
VALID_STATUSES = {"draft", "reviewed", "approved"}
METADATA_REQUIRED = {"title", "doc_id", "revision", "date", "author", "status"}
INPUT_REQUIRED = {"name", "symbol", "value", "unit"}
EQUATION_REQUIRED = {"id", "name", "latex", "description"}
OUTPUT_REQUIRED = {"name", "symbol", "value", "unit"}
CHART_REQUIRED = {"id", "title", "type", "x_label", "y_label", "datasets"}
DATASET_REQUIRED = {"label", "data"}


# ═══════════════════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════════════════

def load_and_validate(data):
    """Validate a calculation data dict against the schema.

    Returns the validated data dict unchanged.
    Raises ValueError if required fields are missing or invalid.
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dict")

    if "metadata" not in data:
        raise ValueError("Missing required section: metadata")
    meta = data["metadata"]
    for field in METADATA_REQUIRED:
        if field not in meta:
            raise ValueError(f"Missing required metadata field: {field}")
    if meta["status"] not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{meta['status']}'; must be one of {VALID_STATUSES}"
        )

    if "inputs" not in data or not data["inputs"]:
        raise ValueError("Missing or empty required section: inputs")
    for i, inp in enumerate(data["inputs"]):
        for field in INPUT_REQUIRED:
            if field not in inp:
                raise ValueError(f"Input #{i+1} missing required field: {field}")

    if "methodology" not in data:
        raise ValueError("Missing required section: methodology")
    meth = data["methodology"]
    for field in ("description", "standard", "equations"):
        if field not in meth:
            raise ValueError(f"Missing required methodology field: {field}")
    for j, eq in enumerate(meth["equations"]):
        for field in EQUATION_REQUIRED:
            if field not in eq:
                raise ValueError(f"Equation #{j+1} missing required field: {field}")

    if "outputs" not in data or not data["outputs"]:
        raise ValueError("Missing or empty required section: outputs")
    for k, out in enumerate(data["outputs"]):
        for field in OUTPUT_REQUIRED:
            if field not in out:
                raise ValueError(f"Output #{k+1} missing required field: {field}")

    if "charts" in data:
        for c, chart in enumerate(data["charts"]):
            for field in CHART_REQUIRED:
                if field not in chart:
                    raise ValueError(f"Chart #{c+1} missing required field: {field}")
            for d, ds in enumerate(chart["datasets"]):
                for field in DATASET_REQUIRED:
                    if field not in ds:
                        raise ValueError(
                            f"Chart #{c+1} dataset #{d+1} missing: {field}"
                        )

    return data


# ═══════════════════════════════════════════════════════════════════════════
# Markdown Generation
# ═══════════════════════════════════════════════════════════════════════════

def _md_table(headers, rows):
    """Build a Markdown table from headers and row lists."""
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def render_markdown(data):
    """Render validated calculation data to Markdown with LaTeX math."""
    meta = data["metadata"]
    lines = []

    # Title block
    lines.append(f"# {meta['title']}")
    parts = [f"**{meta['doc_id']}**", f"Rev {meta['revision']}",
             meta["date"], meta["author"]]
    if meta.get("reviewer"):
        parts.append(f"Reviewer: {meta['reviewer']}")
    lines.append(" | ".join(parts))
    lines.append(f"\n**Status:** {meta['status'].upper()}")
    if meta.get("project"):
        lines.append(f"**Project:** {meta['project']}")
    std = data.get("methodology", {}).get("standard", "")
    if std:
        lines.append(f"**Standard:** {std}")
    lines.append("")

    # Inputs
    lines.append("## Inputs")
    rows = []
    for inp in data["inputs"]:
        rows.append([inp["name"], f"${inp['symbol']}$", inp["value"],
                     inp["unit"], inp.get("source", "\u2014")])
    lines.append(_md_table(["Name", "Symbol", "Value", "Unit", "Source"], rows))
    lines.append("")

    # Methodology
    meth = data["methodology"]
    lines.append("## Methodology")
    lines.append(meth["description"].strip())
    lines.append("")
    for eq in meth["equations"]:
        lines.append(f"### Equation {eq['id']}: {eq['name']}")
        lines.append(f"\n$${eq['latex']}$$\n")
        lines.append(eq["description"])
        if eq.get("variables"):
            lines.append("\n**Variables:**\n")
            for var in eq["variables"]:
                unit = f" [{var['unit']}]" if var.get("unit") else ""
                lines.append(f"- ${var['symbol']}$ \u2014 {var['description']}{unit}")
        lines.append("")

    # Outputs
    lines.append("## Outputs")
    rows = []
    for out in data["outputs"]:
        pf = out.get("pass_fail", "")
        pf = "PASS" if pf == "pass" else ("FAIL" if pf == "fail" else "\u2014")
        limit = out.get("limit", "\u2014")
        if limit != "\u2014":
            limit = f"\u2264 {limit}"
        rows.append([out["name"], f"${out['symbol']}$", out["value"],
                     out["unit"], pf, limit])
    lines.append(_md_table(
        ["Name", "Symbol", "Value", "Unit", "Status", "Limit"], rows))
    lines.append("")

    # Assumptions
    if data.get("assumptions"):
        lines.append("## Assumptions")
        for i, a in enumerate(data["assumptions"], 1):
            lines.append(f"{i}. {a}")
        lines.append("")

    # References
    if data.get("references"):
        lines.append("## References")
        for i, r in enumerate(data["references"], 1):
            lines.append(f"{i}. {r}")
        lines.append("")

    # Change Log
    if meta.get("change_log"):
        lines.append("## Change Log")
        rows = [[cl["rev"], cl["date"], cl["description"]]
                for cl in meta["change_log"]]
        lines.append(_md_table(["Rev", "Date", "Description"], rows))
        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# HTML Generation (delegates to calc_report_html)
# ═══════════════════════════════════════════════════════════════════════════

def render_html(data, markdown_str):
    """Render validated data to a complete HTML document."""
    meta = data["metadata"]
    standard = data["methodology"]["standard"]
    charts = data.get("charts", [])

    hero = build_hero(meta, standard)
    inputs_card = build_inputs_card(data["inputs"])
    meth_card = build_methodology_card(data["methodology"])
    outputs_card = build_outputs_card(data["outputs"])
    charts_card = build_charts_card(charts)
    data_tables_card = build_data_tables_card(data.get("data_tables", []))
    assumptions_refs = build_assumptions_references(data)
    changelog = build_changelog_card(meta.get("change_log", []))

    chartjs_link = ""
    chart_init = ""
    if charts:
        chartjs_link = f'<script src="{CHARTJS_CDN}"></script>'
        chart_init = (
            "<script>\n"
            "document.addEventListener('DOMContentLoaded', function() {\n"
            f"{build_chart_scripts(charts)}\n"
            "});\n</script>"
        )

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_escape(meta['title'])} \u2014 {html_escape(meta['doc_id'])}</title>
<link rel="stylesheet" href="{KATEX_CSS_CDN}">
<script src="{KATEX_JS_CDN}"></script>
<script src="{KATEX_AUTO_CDN}"></script>
{chartjs_link}
<style>
{FULL_CSS}
</style>
</head>
<body>

{hero}

<div class="content">
{inputs_card}

{meth_card}

{outputs_card}

{charts_card}

{data_tables_card}

{assumptions_refs}

{changelog}

<div class="report-footer">
  Generated by calculation-report skill &middot; {html_escape(meta['doc_id'])} Rev {meta['revision']}
</div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {{
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "$", right: "$", display: false}}
    ],
    throwOnError: false
  }});
}});
</script>
{chart_init}
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════
# Entry Points
# ═══════════════════════════════════════════════════════════════════════════

def generate_report(yaml_path, fmt="html", output_path=None):
    """Generate a report from a YAML file."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    data = load_and_validate(data)
    md = render_markdown(data)

    if output_path is None:
        stem = Path(yaml_path).stem
        ext = ".html" if fmt == "html" else ".md"
        output_path = str(Path(yaml_path).parent / (stem + ext))

    if fmt == "md":
        with open(output_path, "w") as f:
            f.write(md)
    else:
        html = render_html(data, md)
        with open(output_path, "w") as f:
            f.write(html)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate calculation reports from YAML."
    )
    parser.add_argument("input", help="Path to input YAML file")
    parser.add_argument(
        "--format", choices=["html", "md"], default="html",
        help="Output format (default: html)"
    )
    parser.add_argument("--output", help="Output file path (default: next to input)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    out = generate_report(args.input, fmt=args.format, output_path=args.output)
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()
