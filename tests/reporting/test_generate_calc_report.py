"""TDD tests for calculation report generator.

Tests cover: YAML validation, Markdown generation, HTML generation, end-to-end.
Run: uv run --no-project python -m pytest tests/reporting/ -v
"""
import os

import pytest

from conftest import EXAMPLE_GIRTH, EXAMPLE_SCR


# ── Phase 1: Validation ────────────────────────────────────────────────────

class TestValidation:
    """load_and_validate must accept valid data and reject invalid."""

    def test_valid_minimal(self, minimal_valid):
        from generate_calc_report import load_and_validate
        result = load_and_validate(minimal_valid)
        assert result["metadata"]["title"] == "Test Calc"

    def test_valid_girth_weld(self, girth_weld_data):
        from generate_calc_report import load_and_validate
        result = load_and_validate(girth_weld_data)
        assert result["metadata"]["doc_id"] == "CALC-001"

    def test_valid_scr(self, scr_data):
        from generate_calc_report import load_and_validate
        result = load_and_validate(scr_data)
        assert result["metadata"]["doc_id"] == "CALC-002"

    def test_missing_metadata(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["metadata"]
        with pytest.raises(ValueError, match="metadata"):
            load_and_validate(minimal_valid)

    def test_missing_title(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["metadata"]["title"]
        with pytest.raises(ValueError, match="title"):
            load_and_validate(minimal_valid)

    def test_missing_inputs(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["inputs"]
        with pytest.raises(ValueError, match="inputs"):
            load_and_validate(minimal_valid)

    def test_missing_methodology(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["methodology"]
        with pytest.raises(ValueError, match="methodology"):
            load_and_validate(minimal_valid)

    def test_missing_outputs(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["outputs"]
        with pytest.raises(ValueError, match="outputs"):
            load_and_validate(minimal_valid)

    def test_missing_equation_latex(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["methodology"]["equations"][0]["latex"]
        with pytest.raises(ValueError, match="latex"):
            load_and_validate(minimal_valid)

    def test_invalid_status(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["metadata"]["status"] = "invalid_status"
        with pytest.raises(ValueError, match="status"):
            load_and_validate(minimal_valid)

    def test_empty_inputs_list(self, minimal_valid):
        from generate_calc_report import load_and_validate
        minimal_valid["inputs"] = []
        with pytest.raises(ValueError, match="inputs"):
            load_and_validate(minimal_valid)

    def test_input_missing_symbol(self, minimal_valid):
        from generate_calc_report import load_and_validate
        del minimal_valid["inputs"][0]["symbol"]
        with pytest.raises(ValueError, match="symbol"):
            load_and_validate(minimal_valid)

    def test_optional_charts_valid(self, girth_weld_data):
        from generate_calc_report import load_and_validate
        result = load_and_validate(girth_weld_data)
        assert "charts" in result
        assert len(result["charts"]) == 2

    def test_optional_data_tables_valid(self, girth_weld_data):
        from generate_calc_report import load_and_validate
        result = load_and_validate(girth_weld_data)
        assert "data_tables" in result


# ── Phase 2: Markdown generation ────────────────────────────────────────────

class TestMarkdownGeneration:
    """render_markdown must produce correct Markdown with LaTeX math."""

    def test_title_in_output(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "# Test Calc" in md

    def test_doc_id_in_header(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "CALC-TEST" in md

    def test_inputs_table(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "| Name |" in md
        assert "Load" in md
        assert "$P$" in md

    def test_latex_equation_block(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "$$" in md
        assert "\\frac{P}{P_{Rd}}" in md

    def test_equation_numbering(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        assert "Equation 1" in md
        assert "Equation 2" in md
        assert "Equation 3" in md

    def test_outputs_table(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "Unity Check" in md
        assert "0.65" in md

    def test_pass_fail_in_outputs(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        assert "PASS" in md.upper()

    def test_assumptions_section(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "## Assumptions" in md
        assert "linear elastic" in md

    def test_references_section(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        assert "## References" in md
        assert "EN 1993-1-1" in md

    def test_methodology_prose(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        assert "## Methodology" in md
        assert "Palmgren-Miner" in md

    def test_change_log_present(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        assert "Change Log" in md or "Revision History" in md

    def test_sections_order(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        sections = ["Inputs", "Methodology", "Outputs", "Assumptions", "References"]
        positions = [md.index(f"## {s}") for s in sections]
        assert positions == sorted(positions), "Sections must appear in order"


# ── Phase 3: HTML generation ───────────────────────────────────────────────

class TestHTMLGeneration:
    """render_html must produce valid HTML with KaTeX + Chart.js."""

    def test_html_is_valid_document(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_title_in_html(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "Test Calc" in html

    def test_warm_parchment_css(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "--bg:" in html or "#f3efe6" in html
        assert "Georgia" in html

    def test_hero_section(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "CALC-001" in html
        assert "hero" in html

    def test_meta_chips(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "meta-chip" in html or "pill" in html

    def test_katex_included(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "katex" in html.lower() or "KaTeX" in html

    def test_latex_rendered_in_html(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "\\frac{P}{P_{Rd}}" in html

    def test_chartjs_included_when_charts(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "Chart" in html or "chart" in html

    def test_chart_canvas_elements(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert '<canvas' in html
        assert 'sn_curve' in html

    def test_data_table_in_html(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "Top Damage Contributors" in html or "damage_contributors" in html

    def test_pass_fail_badges(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "badge-pass" in html or "badge-fail" in html

    def test_footer_present(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "calculation-report" in html.lower() or "Generated by" in html

    def test_no_chart_when_absent(self, minimal_valid):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(minimal_valid)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "<canvas" not in html

    def test_status_badge(self, girth_weld_data):
        from generate_calc_report import load_and_validate, render_markdown, render_html
        data = load_and_validate(girth_weld_data)
        md = render_markdown(data)
        html = render_html(data, md)
        assert "draft" in html.lower()


# ── Phase 4: End-to-end (file I/O) ─────────────────────────────────────────

class TestEndToEnd:
    """End-to-end: YAML file → HTML file on disk."""

    def test_girth_weld_e2e(self, tmp_path):
        from generate_calc_report import generate_report
        out = str(tmp_path / "report.html")
        generate_report(EXAMPLE_GIRTH, fmt="html", output_path=out)
        assert os.path.exists(out)
        content = open(out).read()
        assert "Pipeline Girth Weld" in content
        assert len(content) > 1000

    def test_scr_e2e(self, tmp_path):
        from generate_calc_report import generate_report
        out = str(tmp_path / "report.html")
        generate_report(EXAMPLE_SCR, fmt="html", output_path=out)
        assert os.path.exists(out)
        content = open(out).read()
        assert "Steel Catenary Riser" in content

    def test_markdown_output(self, tmp_path):
        from generate_calc_report import generate_report
        out = str(tmp_path / "report.md")
        generate_report(EXAMPLE_GIRTH, fmt="md", output_path=out)
        assert os.path.exists(out)
        content = open(out).read()
        assert "$$" in content

    def test_default_output_path(self, tmp_path):
        """Without --output, writes next to input file."""
        import shutil
        src = str(tmp_path / "test-calc.yaml")
        shutil.copy(EXAMPLE_GIRTH, src)
        from generate_calc_report import generate_report
        generate_report(src, fmt="html")
        expected = str(tmp_path / "test-calc.html")
        assert os.path.exists(expected)
