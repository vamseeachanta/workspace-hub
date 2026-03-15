"""HTML builder functions for calculation report generator.

Builds HTML sections from validated calculation data using the
warm-parchment design system. Called by generate-calc-report.py.
"""
import json
from html import escape as html_escape


# ── KaTeX + Chart.js CDN URLs ──────────────────────────────────────────────
KATEX_VERSION = "0.16.11"
KATEX_CSS_CDN = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css"
KATEX_JS_CDN = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js"
KATEX_AUTO_CDN = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js"
CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js"


def status_badge_class(status):
    """Return CSS class for a status badge."""
    return {
        "draft": "badge-draft",
        "reviewed": "badge-reviewed",
        "approved": "badge-approved",
    }.get(status, "badge-draft")


def pass_fail_badge(pf):
    """Return HTML badge for pass/fail."""
    if pf == "pass":
        return '<span class="badge badge-pass">PASS</span>'
    elif pf == "fail":
        return '<span class="badge badge-fail">FAIL</span>'
    return "—"


def build_hero(meta, standard):
    """Build the hero header HTML."""
    s_cls = status_badge_class(meta["status"])
    reviewer_html = ""
    if meta.get("reviewer"):
        reviewer_html = (
            '\n        <div class="meta-chip"><strong>Reviewer</strong>'
            f'{html_escape(meta["reviewer"])}</div>'
        )
    project_html = ""
    if meta.get("project"):
        project_html = (
            '\n        <div class="meta-chip"><strong>Project</strong>'
            f'{html_escape(meta["project"])}</div>'
        )

    return f"""\
<div class="hero">
  <div class="hero-inner">
    <div class="eyebrow">{html_escape(meta['doc_id'])}</div>
    <h1 class="report-title">{html_escape(meta['title'])}</h1>
    <div class="meta-chips">
      <div class="meta-chip"><strong>Status</strong><span class="badge {s_cls}">{html_escape(meta['status'].upper())}</span></div>
      <div class="meta-chip"><strong>Revision</strong>{meta['revision']}</div>
      <div class="meta-chip"><strong>Date</strong>{html_escape(meta['date'])}</div>
      <div class="meta-chip"><strong>Author</strong>{html_escape(meta['author'])}</div>{reviewer_html}{project_html}
      <div class="meta-chip"><strong>Standard</strong>{html_escape(standard)}</div>
    </div>
  </div>
</div>"""


def build_inputs_card(inputs):
    """Build inputs table card."""
    rows = ""
    for inp in inputs:
        src = html_escape(str(inp.get("source", "—")))
        rows += (
            f'      <tr>\n'
            f'        <td><strong>{html_escape(inp["name"])}</strong></td>\n'
            f'        <td class="katex-inline">${html_escape(inp["symbol"])}$</td>\n'
            f'        <td>{inp["value"]}</td>\n'
            f'        <td>{html_escape(inp["unit"])}</td>\n'
            f'        <td>{src}</td>\n'
            f'      </tr>\n'
        )
    return f"""\
<div class="card">
  <h2>Inputs</h2>
  <table>
    <thead><tr><th>Name</th><th>Symbol</th><th>Value</th><th>Unit</th><th>Source</th></tr></thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>"""


def build_methodology_card(meth):
    """Build methodology card with equations."""
    eq_html = ""
    for eq in meth["equations"]:
        vars_html = ""
        if eq.get("variables"):
            var_items = ""
            for v in eq["variables"]:
                unit = f" [{html_escape(v['unit'])}]" if v.get("unit") else ""
                var_items += (
                    f'<li><span class="var-sym">${html_escape(v["symbol"])}$</span>'
                    f' — {html_escape(v["description"])}{unit}</li>\n'
                )
            vars_html = f'<ul class="variable-list">\n{var_items}</ul>'

        eq_html += (
            f'  <div class="equation-block">\n'
            f'    <div class="equation-name">Equation {eq["id"]}: '
            f'{html_escape(eq["name"])}</div>\n'
            f'    <div class="katex-display">$${html_escape(eq["latex"])}$$</div>\n'
            f'    <div class="equation-desc">{html_escape(eq["description"])}</div>\n'
            f'    <span class="eq-number">({eq["id"]})</span>\n'
            f'    {vars_html}\n'
            f'  </div>\n'
        )

    return f"""\
<div class="card">
  <h2>Methodology</h2>
  <p>{html_escape(meth['description'].strip())}</p>
  <p><strong>Standard:</strong> {html_escape(meth['standard'])}</p>
{eq_html}</div>"""


def build_outputs_card(outputs):
    """Build outputs table card with pass/fail badges."""
    rows = ""
    for out in outputs:
        pf = pass_fail_badge(out.get("pass_fail"))
        limit = out.get("limit", "")
        limit_str = f"≤ {limit}" if limit else "—"
        rows += (
            f'      <tr>\n'
            f'        <td><strong>{html_escape(out["name"])}</strong></td>\n'
            f'        <td class="katex-inline">${html_escape(out["symbol"])}$</td>\n'
            f'        <td>{out["value"]}</td>\n'
            f'        <td>{html_escape(out["unit"])}</td>\n'
            f'        <td>{pf}</td>\n'
            f'        <td>{limit_str}</td>\n'
            f'      </tr>\n'
        )
    return f"""\
<div class="card">
  <h2>Outputs</h2>
  <table>
    <thead><tr><th>Name</th><th>Symbol</th><th>Value</th><th>Unit</th><th>Pass/Fail</th><th>Limit</th></tr></thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>"""


def build_charts_card(charts):
    """Build charts card with Chart.js canvas elements."""
    if not charts:
        return ""
    canvases = ""
    for chart in charts:
        canvases += (
            f'  <div class="chart-container">\n'
            f'    <div class="chart-title">{html_escape(chart["title"])}</div>\n'
            f'    <canvas id="chart-{html_escape(chart["id"])}" height="300"></canvas>\n'
            f'  </div>\n'
        )
    return f'<div class="card">\n  <h2>Charts</h2>\n{canvases}</div>'


def _build_dataset_js(chart_type, ds):
    """Build a single Chart.js dataset config string."""
    color = ds.get("color", "#0f766e")
    if chart_type in ("scatter", "log_log"):
        points = [{"x": p[0], "y": p[1]} for p in ds["data"]]
        return (
            f'{{"label":{json.dumps(ds["label"])},'
            f'"data":{json.dumps(points)},'
            f'"borderColor":"{color}","backgroundColor":"{color}80",'
            f'"showLine":true,"pointRadius":4}}'
        )
    elif chart_type == "bar":
        values = [p[1] for p in ds["data"]]
        return (
            f'{{"label":{json.dumps(ds["label"])},'
            f'"data":{json.dumps(values)},'
            f'"backgroundColor":"{color}cc","borderColor":"{color}",'
            f'"borderWidth":1}}'
        )
    else:
        points = [{"x": p[0], "y": p[1]} for p in ds["data"]]
        return (
            f'{{"label":{json.dumps(ds["label"])},'
            f'"data":{json.dumps(points)},'
            f'"borderColor":"{color}","fill":false,"tension":0.1}}'
        )


def build_chart_scripts(charts):
    """Build Chart.js initialization scripts for each chart."""
    if not charts:
        return ""

    scripts = []
    for chart in charts:
        chart_type = chart["type"]
        cjs_type = "scatter" if chart_type in ("log_log", "scatter") else chart_type
        datasets_str = ",".join(
            _build_dataset_js(chart_type, ds) for ds in chart["datasets"]
        )

        x_scale = chart.get("x_scale", "linear")
        y_scale = chart.get("y_scale", "linear")

        if chart_type == "bar":
            labels = [p[0] for p in chart["datasets"][0]["data"]]
            scales_js = (
                f'"x":{{"title":{{"display":true,'
                f'"text":{json.dumps(chart["x_label"])}}}}},'
                f'"y":{{"title":{{"display":true,'
                f'"text":{json.dumps(chart["y_label"])}}}'
                + (f',"type":"logarithmic"' if y_scale == "log" else "")
                + "}}"
            )
            config = (
                f'{{"type":"bar","data":{{"labels":{json.dumps(labels)},'
                f'"datasets":[{datasets_str}]}},'
                f'"options":{{"responsive":true,"scales":{{{scales_js}}}}}}}'
            )
        else:
            x_t = "logarithmic" if x_scale == "log" else "linear"
            y_t = "logarithmic" if y_scale == "log" else "linear"
            scales_js = (
                f'"x":{{"type":"{x_t}",'
                f'"title":{{"display":true,'
                f'"text":{json.dumps(chart["x_label"])}}}}},'
                f'"y":{{"type":"{y_t}",'
                f'"title":{{"display":true,'
                f'"text":{json.dumps(chart["y_label"])}}}}}'
            )
            config = (
                f'{{"type":"{cjs_type}","data":{{"datasets":[{datasets_str}]}},'
                f'"options":{{"responsive":true,"scales":{{{scales_js}}}}}}}'
            )

        scripts.append(
            f'new Chart(document.getElementById("chart-{chart["id"]}"), '
            f'{config});'
        )

    return "\n".join(scripts)


def build_data_tables_card(data_tables):
    """Build data tables card."""
    if not data_tables:
        return ""
    tables_html = ""
    for dt in data_tables:
        headers = "".join(
            f"<th>{html_escape(c['name'])}"
            + (f" ({html_escape(c['unit'])})" if c.get("unit") else "")
            + "</th>"
            for c in dt["columns"]
        )
        rows = ""
        for row in dt["rows"]:
            cells = "".join(f"<td>{html_escape(str(v))}</td>" for v in row)
            rows += f"      <tr>{cells}</tr>\n"
        tables_html += (
            f'  <h3>{html_escape(dt["title"])}</h3>\n'
            f'  <table>\n'
            f'    <thead><tr>{headers}</tr></thead>\n'
            f'    <tbody>\n{rows}    </tbody>\n'
            f'  </table>\n'
        )
    return f'<div class="card">\n  <h2>Data Tables</h2>\n{tables_html}</div>'


def build_scope_card(scope):
    """Build scope card with objective and inclusions/exclusions."""
    obj = html_escape(scope["objective"])
    incl = "\n".join(
        f"    <li>{html_escape(i)}</li>" for i in scope["inclusions"]
    )
    excl = "\n".join(
        f"    <li>{html_escape(e)}</li>" for e in scope["exclusions"]
    )
    optional = ""
    if scope.get("limitations"):
        lims = scope["limitations"]
        if isinstance(lims, list):
            lim_items = "\n".join(
                f"    <li>{html_escape(l)}</li>" for l in lims
            )
            optional += f'\n  <h3>Limitations</h3>\n  <ul>\n{lim_items}\n  </ul>'
        else:
            optional += (
                f'\n  <p><strong>Limitations:</strong> '
                f'{html_escape(str(lims))}</p>'
            )
    if scope.get("validity_range"):
        optional += (
            f'\n  <p><strong>Validity Range:</strong> '
            f'{html_escape(scope["validity_range"])}</p>'
        )
    return f"""\
<div class="card">
  <h2>Scope</h2>
  <p><strong>Objective:</strong> {obj}</p>
  <h3>Inclusions</h3>
  <ul>
{incl}
  </ul>
  <h3>Exclusions</h3>
  <ul>
{excl}
  </ul>{optional}
</div>"""


def build_design_basis_card(design_basis):
    """Build design basis card with codes table."""
    codes = design_basis["codes"]
    if codes and isinstance(codes[0], dict):
        code_rows = ""
        for c in codes:
            clause = html_escape(str(c.get("clause", "—")))
            code_rows += (
                f'      <tr>\n'
                f'        <td>{html_escape(c["code"])}</td>\n'
                f'        <td>{html_escape(str(c["edition"]))}</td>\n'
                f'        <td>{clause}</td>\n'
                f'      </tr>\n'
            )
        codes_html = (
            '  <table>\n'
            '    <thead><tr><th>Code</th><th>Edition</th><th>Clause</th></tr></thead>\n'
            '    <tbody>\n'
            f'{code_rows}    </tbody>\n'
            '  </table>'
        )
    else:
        items = "\n".join(
            f"    <li>{html_escape(str(c))}</li>" for c in codes
        )
        codes_html = f'  <ul>\n{items}\n  </ul>'
    dl = design_basis["design_life"]
    optional = ""
    if design_basis.get("safety_class"):
        optional += (
            f'\n  <p><strong>Safety Class:</strong> '
            f'{html_escape(str(design_basis["safety_class"]))}</p>'
        )
    if design_basis.get("load_combinations"):
        lc_items = "\n".join(
            f"    <li>{html_escape(lc)}</li>"
            for lc in design_basis["load_combinations"]
        )
        optional += f'\n  <h3>Load Combinations</h3>\n  <ul>\n{lc_items}\n  </ul>'
    if design_basis.get("environment"):
        optional += (
            f'\n  <p><strong>Environment:</strong> '
            f'{html_escape(design_basis["environment"])}</p>'
        )
    return f"""\
<div class="card">
  <h2>Design Basis</h2>
{codes_html}
  <p><strong>Design Life:</strong> {dl}</p>{optional}
</div>"""


def build_materials_card(materials):
    """Build materials table card."""
    rows = ""
    for mat in materials:
        src = html_escape(str(mat.get("source", "—")))
        pf = mat.get("partial_factor", "—")
        rows += (
            f'      <tr>\n'
            f'        <td>{html_escape(mat["name"])}</td>\n'
            f'        <td>{html_escape(str(mat["grade"]))}</td>\n'
            f'        <td>{mat["value"]}</td>\n'
            f'        <td>{html_escape(mat["unit"])}</td>\n'
            f'        <td>{src}</td>\n'
            f'        <td>{pf}</td>\n'
            f'      </tr>\n'
        )
    return f"""\
<div class="card">
  <h2>Materials</h2>
  <table>
    <thead><tr><th>Name</th><th>Grade</th><th>Value</th><th>Unit</th><th>Source</th><th>Partial Factor</th></tr></thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>"""


def build_calculations_card(calculations):
    """Build calculations card with numbered steps."""
    steps_html = ""
    for calc in calculations:
        step_num = calc["step"]
        desc = html_escape(calc["description"])
        detail_html = ""
        if calc.get("detail"):
            detail_html = (
                f'\n    <div class="calc-detail">'
                f'{html_escape(calc["detail"])}</div>'
            )
        clause_html = ""
        if calc.get("code_clause"):
            clause_html = (
                f'\n    <div class="calc-clause"><em>Ref: '
                f'{html_escape(calc["code_clause"])}</em></div>'
            )
        intermediate_html = ""
        if calc.get("intermediate_results"):
            ir_items = ""
            for ir in calc["intermediate_results"]:
                ir_items += (
                    f'      <li>{html_escape(ir["name"])} = '
                    f'{ir["value"]} {html_escape(str(ir.get("unit", "")))}</li>\n'
                )
            intermediate_html = (
                f'\n    <ul class="intermediate-results">\n{ir_items}    </ul>'
            )
        steps_html += (
            f'  <div class="calc-step">\n'
            f'    <h3>Step {step_num}: {desc}</h3>'
            f'{detail_html}{clause_html}{intermediate_html}\n'
            f'  </div>\n'
        )
    return f"""\
<div class="card">
  <h2>Calculations</h2>
{steps_html}</div>"""


def build_sensitivity_card(sensitivity):
    """Build sensitivity analysis table card."""
    rows = ""
    for s in sensitivity:
        rows += (
            f'      <tr>\n'
            f'        <td>{html_escape(s["parameter"])}</td>\n'
            f'        <td>{html_escape(str(s["range"]))}</td>\n'
            f'        <td>{html_escape(str(s["result"]))}</td>\n'
            f'      </tr>\n'
        )
    return f"""\
<div class="card">
  <h2>Sensitivity Analysis</h2>
  <table>
    <thead><tr><th>Parameter</th><th>Range</th><th>Result</th></tr></thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>"""


def build_validation_card(validation):
    """Build validation card with test summary."""
    method = html_escape(validation.get("method", ""))
    optional = ""
    if validation.get("test_file"):
        optional += (
            f'\n  <p><strong>Test File:</strong> '
            f'<code>{html_escape(validation["test_file"])}</code></p>'
        )
    if validation.get("test_count"):
        optional += (
            f'\n  <p><strong>Test Count:</strong> {validation["test_count"]}</p>'
        )
    if validation.get("test_categories"):
        cat_items = "\n".join(
            f"    <li>{html_escape(c)}</li>"
            for c in validation["test_categories"]
        )
        optional += (
            f'\n  <h3>Test Categories</h3>\n  <ul>\n{cat_items}\n  </ul>'
        )
    if validation.get("benchmark_source"):
        optional += (
            f'\n  <p><strong>Benchmark Source:</strong> '
            f'{html_escape(validation["benchmark_source"])}</p>'
        )
    return f"""\
<div class="card">
  <h2>Validation</h2>
  <p><strong>Method:</strong> {method}</p>{optional}
</div>"""


def build_verification_card(verification):
    """Build verification card with checker record."""
    checker = html_escape(verification["checker"])
    date = html_escape(verification["date"])
    method = html_escape(verification["method"])
    optional = ""
    if verification.get("findings"):
        optional += (
            f'\n  <p><strong>Findings:</strong> '
            f'{html_escape(verification["findings"])}</p>'
        )
    if verification.get("status"):
        optional += (
            f'\n  <p><strong>Status:</strong> '
            f'{html_escape(verification["status"])}</p>'
        )
    return f"""\
<div class="card">
  <h2>Verification</h2>
  <p><strong>Checker:</strong> {checker}</p>
  <p><strong>Date:</strong> {date}</p>
  <p><strong>Method:</strong> {method}</p>{optional}
</div>"""


def build_conclusions_card(conclusions):
    """Build conclusions card with adequacy statement."""
    adequacy = html_escape(conclusions["adequacy"])
    governing = html_escape(conclusions["governing_check"])
    optional = ""
    if conclusions.get("recommendations"):
        rec_items = "\n".join(
            f"    <li>{html_escape(r)}</li>"
            for r in conclusions["recommendations"]
        )
        optional += (
            f'\n  <h3>Recommendations</h3>\n  <ul>\n{rec_items}\n  </ul>'
        )
    if conclusions.get("compliance_statement"):
        optional += (
            f'\n  <p><strong>Compliance:</strong> '
            f'{html_escape(conclusions["compliance_statement"])}</p>'
        )
    return f"""\
<div class="card">
  <h2>Conclusions</h2>
  <p><strong>Adequacy:</strong> {adequacy}</p>
  <p><strong>Governing Check:</strong> {governing}</p>{optional}
</div>"""


def build_assumptions_references(data):
    """Build assumptions and references sections."""
    parts = []
    if data.get("assumptions"):
        items = "\n".join(
            f"    <li>{html_escape(a)}</li>" for a in data["assumptions"]
        )
        parts.append(
            f'<div class="card">\n  <details open>\n'
            f'    <summary>Assumptions</summary>\n    <ol>\n{items}\n'
            f'    </ol>\n  </details>\n</div>'
        )
    if data.get("references"):
        items = "\n".join(
            f"    <li>{html_escape(r)}</li>" for r in data["references"]
        )
        parts.append(
            f'<div class="card">\n  <details open>\n'
            f'    <summary>References</summary>\n    <ol>\n{items}\n'
            f'    </ol>\n  </details>\n</div>'
        )
    return "\n".join(parts)


def build_changelog_card(change_log):
    """Build change log table card."""
    if not change_log:
        return ""
    rows = ""
    for cl in change_log:
        rows += (
            f"      <tr><td>{cl['rev']}</td>"
            f"<td>{html_escape(cl['date'])}</td>"
            f"<td>{html_escape(cl['description'])}</td></tr>\n"
        )
    return (
        f'<div class="card">\n  <h2>Change Log</h2>\n  <table>\n'
        f'    <thead><tr><th>Rev</th><th>Date</th><th>Description</th></tr></thead>\n'
        f'    <tbody>\n{rows}    </tbody>\n  </table>\n</div>'
    )
