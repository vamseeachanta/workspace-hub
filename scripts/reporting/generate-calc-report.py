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
    build_assumptions_references, build_calculations_card,
    build_changelog_card, build_chart_scripts, build_charts_card,
    build_conclusions_card, build_data_tables_card,
    build_design_basis_card, build_hero, build_inputs_card,
    build_materials_card, build_methodology_card, build_outputs_card,
    build_scope_card, build_sensitivity_card, build_validation_card,
    build_verification_card,
)

# ── Validation constants ───────────────────────────────────────────────────
VALID_STATUSES = {"draft", "reviewed", "approved"}
METADATA_REQUIRED = {"title", "doc_id", "revision", "date", "author", "status"}
INPUT_REQUIRED = {"name", "symbol", "value", "unit"}
EQUATION_REQUIRED = {"id", "name", "latex", "description"}
OUTPUT_REQUIRED = {"name", "symbol", "value", "unit"}
CHART_REQUIRED = {"id", "title", "type", "x_label", "y_label", "datasets"}
DATASET_REQUIRED = {"label", "data"}
SCOPE_REQUIRED = {"objective", "inclusions", "exclusions"}
DESIGN_BASIS_REQUIRED = {"codes", "design_life"}
MATERIAL_REQUIRED = {"name", "grade", "value", "unit"}
CALCULATION_REQUIRED = {"step", "description"}
SENSITIVITY_REQUIRED = {"parameter", "range", "result"}
VALIDATION_REQUIRED = set()  # all fields optional for backwards compat
VERIFICATION_REQUIRED = {"checker", "date", "method"}
CONCLUSIONS_REQUIRED = {"adequacy", "governing_check"}


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

    # ── Optional v2 sections ─────────────────────────────────────────────
    if "scope" in data:
        for field in SCOPE_REQUIRED:
            if field not in data["scope"]:
                raise ValueError(f"Scope missing required field: {field}")

    if "design_basis" in data:
        for field in DESIGN_BASIS_REQUIRED:
            if field not in data["design_basis"]:
                raise ValueError(
                    f"Design basis missing required field: {field}"
                )

    if "materials" in data:
        for m, mat in enumerate(data["materials"]):
            for field in MATERIAL_REQUIRED:
                if field not in mat:
                    raise ValueError(
                        f"Material #{m+1} missing required field: {field}"
                    )

    if "calculations" in data:
        for c, calc in enumerate(data["calculations"]):
            for field in CALCULATION_REQUIRED:
                if field not in calc:
                    raise ValueError(
                        f"Calculation #{c+1} missing required field: {field}"
                    )

    if "sensitivity" in data:
        for s, sens in enumerate(data["sensitivity"]):
            for field in SENSITIVITY_REQUIRED:
                if field not in sens:
                    raise ValueError(
                        f"Sensitivity #{s+1} missing required field: {field}"
                    )

    if "validation" in data:
        for field in VALIDATION_REQUIRED:
            if field not in data["validation"]:
                raise ValueError(
                    f"Validation missing required field: {field}"
                )

    if "verification" in data:
        for field in VERIFICATION_REQUIRED:
            if field not in data["verification"]:
                raise ValueError(
                    f"Verification missing required field: {field}"
                )

    if "conclusions" in data:
        for field in CONCLUSIONS_REQUIRED:
            if field not in data["conclusions"]:
                raise ValueError(
                    f"Conclusions missing required field: {field}"
                )

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

    # Scope (v2 optional)
    if data.get("scope"):
        scope = data["scope"]
        lines.append("## Scope")
        lines.append(f"**Objective:** {scope['objective']}")
        lines.append("\n**Inclusions:**\n")
        for item in scope["inclusions"]:
            lines.append(f"- {item}")
        lines.append("\n**Exclusions:**\n")
        for item in scope["exclusions"]:
            lines.append(f"- {item}")
        if scope.get("limitations"):
            lines.append(f"\n**Limitations:** {scope['limitations']}")
        if scope.get("validity_range"):
            lines.append(f"\n**Validity Range:** {scope['validity_range']}")
        lines.append("")

    # Design Basis (v2 optional)
    if data.get("design_basis"):
        db = data["design_basis"]
        lines.append("## Design Basis")
        if db["codes"] and isinstance(db["codes"][0], dict):
            code_rows = []
            for c in db["codes"]:
                code_rows.append([
                    c["code"], str(c["edition"]), c.get("clause", "\u2014")
                ])
            lines.append(_md_table(["Code", "Edition", "Clause"], code_rows))
        else:
            for c in db["codes"]:
                lines.append(f"- {c}")
        lines.append(f"\n**Design Life:** {db['design_life']}")
        if db.get("safety_class"):
            lines.append(f"\n**Safety Class:** {db['safety_class']}")
        if db.get("load_combinations"):
            lines.append("\n**Load Combinations:**\n")
            for lc in db["load_combinations"]:
                lines.append(f"- {lc}")
        if db.get("environment"):
            lines.append(f"\n**Environment:** {db['environment']}")
        lines.append("")

    # Inputs
    lines.append("## Inputs")
    rows = []
    for inp in data["inputs"]:
        rows.append([inp["name"], f"${inp['symbol']}$", inp["value"],
                     inp["unit"], inp.get("source", "\u2014")])
    lines.append(_md_table(["Name", "Symbol", "Value", "Unit", "Source"], rows))
    lines.append("")

    # Materials (v2 optional)
    if data.get("materials"):
        lines.append("## Materials")
        mat_rows = []
        for mat in data["materials"]:
            mat_rows.append([
                mat["name"], str(mat["grade"]), str(mat["value"]),
                mat["unit"], mat.get("source", "\u2014"),
                str(mat.get("partial_factor", "\u2014")),
            ])
        lines.append(_md_table(
            ["Name", "Grade", "Value", "Unit", "Source", "Partial Factor"],
            mat_rows,
        ))
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

    # Calculations (v2 optional)
    if data.get("calculations"):
        lines.append("## Calculations")
        for calc in data["calculations"]:
            lines.append(f"### Step {calc['step']}: {calc['description']}")
            if calc.get("detail"):
                lines.append(f"\n{calc['detail']}")
            if calc.get("code_clause"):
                lines.append(f"\n*Ref: {calc['code_clause']}*")
            if calc.get("intermediate_results"):
                lines.append("\n**Intermediate Results:**\n")
                for ir in calc["intermediate_results"]:
                    unit = ir.get("unit", "")
                    lines.append(f"- {ir['name']} = {ir['value']} {unit}")
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

    # Sensitivity (v2 optional)
    if data.get("sensitivity"):
        lines.append("## Sensitivity")
        sens_rows = []
        for s in data["sensitivity"]:
            sens_rows.append([s["parameter"], str(s["range"]), str(s["result"])])
        lines.append(_md_table(["Parameter", "Range", "Result"], sens_rows))
        lines.append("")

    # Validation (v2 optional)
    if data.get("validation"):
        val = data["validation"]
        lines.append("## Validation")
        if val.get("method"):
            lines.append(f"**Method:** {val['method']}")
        if val.get("test_file"):
            lines.append(f"\n**Test File:** `{val['test_file']}`")
        if val.get("test_count"):
            lines.append(f"\n**Test Count:** {val['test_count']}")
        if val.get("test_categories"):
            lines.append("\n**Test Categories:**\n")
            for cat in val["test_categories"]:
                lines.append(f"- {cat}")
        if val.get("benchmark_source"):
            lines.append(f"\n**Benchmark Source:** {val['benchmark_source']}")
        lines.append("")

    # Verification (v2 optional)
    if data.get("verification"):
        ver = data["verification"]
        lines.append("## Verification")
        lines.append(f"**Checker:** {ver['checker']}")
        lines.append(f"\n**Date:** {ver['date']}")
        lines.append(f"\n**Method:** {ver['method']}")
        if ver.get("findings"):
            lines.append(f"\n**Findings:** {ver['findings']}")
        if ver.get("status"):
            lines.append(f"\n**Status:** {ver['status']}")
        lines.append("")

    # Conclusions (v2 optional)
    if data.get("conclusions"):
        conc = data["conclusions"]
        lines.append("## Conclusions")
        lines.append(f"**Adequacy:** {conc['adequacy']}")
        lines.append(f"\n**Governing Check:** {conc['governing_check']}")
        if conc.get("recommendations"):
            lines.append("\n**Recommendations:**\n")
            for rec in conc["recommendations"]:
                lines.append(f"- {rec}")
        if conc.get("compliance_statement"):
            lines.append(f"\n**Compliance:** {conc['compliance_statement']}")
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
    scope_card = build_scope_card(data["scope"]) if data.get("scope") else ""
    design_basis_card = (
        build_design_basis_card(data["design_basis"])
        if data.get("design_basis") else ""
    )
    inputs_card = build_inputs_card(data["inputs"])
    materials_card = (
        build_materials_card(data["materials"])
        if data.get("materials") else ""
    )
    meth_card = build_methodology_card(data["methodology"])
    calculations_card = (
        build_calculations_card(data["calculations"])
        if data.get("calculations") else ""
    )
    outputs_card = build_outputs_card(data["outputs"])
    sensitivity_card = (
        build_sensitivity_card(data["sensitivity"])
        if data.get("sensitivity") else ""
    )
    validation_card = (
        build_validation_card(data["validation"])
        if data.get("validation") else ""
    )
    verification_card = (
        build_verification_card(data["verification"])
        if data.get("verification") else ""
    )
    conclusions_card = (
        build_conclusions_card(data["conclusions"])
        if data.get("conclusions") else ""
    )
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
{scope_card}

{design_basis_card}

{inputs_card}

{materials_card}

{meth_card}

{calculations_card}

{outputs_card}

{sensitivity_card}

{validation_card}

{verification_card}

{conclusions_card}

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
