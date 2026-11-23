"""Tests for loop_collapse_generator — pattern groups → Python code."""

import ast

import pytest


def _make_cells(n, sheet="S1", formula_tpl="=A{r}*B{r}", base_row=5):
    """Helper to build cell dicts for a pattern group."""
    cells = []
    for i in range(n):
        r = base_row + i
        cells.append({
            "cell_ref": f"C{r}",
            "sheet": sheet,
            "formula": formula_tpl.format(r=r),
            "cached_value": float(r * 10),
            "references": [f"A{r}", f"B{r}"],
        })
    return cells


class TestPatternToPythonCode:
    """Dispatch by group size: single, explicit, loop."""

    def test_single_cell_returns_expression(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        cells = _make_cells(1)
        var_map = {"A5": "od", "B5": "wt"}
        code = pattern_to_python_code("=A1*B1", cells, var_map)
        assert "od" in code
        assert "wt" in code
        # Should be a simple assignment, not a loop
        assert "for " not in code

    def test_small_group_explicit_assignments(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        cells = _make_cells(3)
        code = pattern_to_python_code("=A1*B1", cells, {})
        # 2-5 cells → explicit assignments per cell
        assert "for " not in code
        assert code.count("=") >= 3  # at least 3 assignment lines

    def test_large_group_generates_loop(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        cells = _make_cells(8)
        code = pattern_to_python_code("=A1*B1", cells, {})
        assert "for " in code

    def test_exactly_5_cells_no_loop(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        cells = _make_cells(5)
        code = pattern_to_python_code("=A1*B1", cells, {})
        assert "for " not in code

    def test_exactly_6_cells_uses_loop(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        cells = _make_cells(6)
        code = pattern_to_python_code("=A1*B1", cells, {})
        assert "for " in code


class TestGenerateFunctionFromPattern:
    """Generate complete def blocks from patterns."""

    def test_returns_valid_python(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = _make_cells(8)
        inputs = ["A5", "B5"]
        code = generate_function_from_pattern(
            name="calc_product",
            pattern="=A1*B1",
            cells=cells,
            var_map={},
            inputs=inputs,
        )
        # Must parse as valid Python
        ast.parse(code)
        assert "def calc_product(" in code

    def test_single_cell_function(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = _make_cells(1)
        code = generate_function_from_pattern(
            name="calc_single",
            pattern="=A1*B1",
            cells=cells,
            var_map={"A5": "diameter", "B5": "length"},
            inputs=["A5", "B5"],
        )
        ast.parse(code)
        assert "def calc_single(" in code
        assert "return" in code

    def test_loop_function_has_results_dict(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = _make_cells(10)
        code = generate_function_from_pattern(
            name="calc_mass",
            pattern="=A1*B1",
            cells=cells,
            var_map={},
            inputs=["A5"],
        )
        ast.parse(code)
        assert "results" in code
        assert "for " in code

    def test_untranslatable_formula_manual_stub(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = [{
            "cell_ref": "C5", "sheet": "S1",
            "formula": "=VLOOKUP(A5,B:B,2,FALSE)",
            "cached_value": 42.0, "references": ["A5"],
        }]
        code = generate_function_from_pattern(
            name="lookup_val",
            pattern="=VLOOKUP(A1,B:B,2,FALSE)",
            cells=cells,
            var_map={},
            inputs=["A5"],
        )
        assert "# MANUAL:" in code
        ast.parse(code)

    def test_includes_docstring_with_excel_formula(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = _make_cells(1)
        code = generate_function_from_pattern(
            name="calc_x",
            pattern="=A1*B1",
            cells=cells,
            var_map={},
            inputs=["A5", "B5"],
        )
        assert '"""' in code or "'''" in code
        assert "A1*B1" in code  # pattern in docstring


class TestEdgeCases:
    """Edge cases and robustness."""

    def test_empty_cells_list(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            pattern_to_python_code,
        )

        code = pattern_to_python_code("=A1*B1", [], {})
        assert code == ""

    def test_formula_with_constants_only(self):
        from scripts.data.doc_intelligence.loop_collapse_generator import (
            generate_function_from_pattern,
        )

        cells = [{"cell_ref": "E47", "sheet": "S1",
                   "formula": "=40/3.28084*3",
                   "cached_value": 36.576, "references": []}]
        code = generate_function_from_pattern(
            name="const_val",
            pattern="=40/3.28084*3",
            cells=cells,
            var_map={},
            inputs=[],
        )
        ast.parse(code)
        assert "return" in code
