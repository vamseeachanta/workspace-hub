"""Tests for module_assembler — assemble one .py module per workbook."""

import ast

import pytest


def _synthetic_patterns():
    """Create synthetic pattern data for testing."""
    return {
        "=A1*B1": [
            {"cell_ref": f"C{r}", "sheet": "Input Data",
             "formula": f"=A{r}*B{r}", "cached_value": float(r * 10),
             "references": [f"A{r}", f"B{r}"]}
            for r in range(5, 13)
        ],
        "=SQRT(A1)": [
            {"cell_ref": f"D{r}", "sheet": "Input Data",
             "formula": f"=SQRT(A{r})", "cached_value": float(r),
             "references": [f"A{r}"]}
            for r in range(5, 8)
        ],
        "=40/3.28084*3": [
            {"cell_ref": "E47", "sheet": "Input Data",
             "formula": "=40/3.28084*3", "cached_value": 36.576,
             "references": []}
        ],
    }


def _synthetic_classification():
    return {
        "inputs": ["A5", "B5", "A6", "B6"],
        "outputs": ["C12", "D7", "E47"],
        "chain": [],
    }


class TestAssembleModule:
    """Assemble complete Python module from patterns."""

    def test_output_is_valid_python(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        ast.parse(code)

    def test_contains_functions(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        assert "def " in code
        # Should have at least one function per pattern group
        assert code.count("def ") >= 3

    def test_has_imports(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        assert "import math" in code

    def test_has_module_docstring(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        assert '"""' in code.split("\n")[0] or '"""' in code.split("\n")[1]

    def test_under_500_lines(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        line_count = len(code.strip().split("\n"))
        assert line_count < 500, f"Module has {line_count} lines (max 500)"

    def test_empty_patterns(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="empty",
            patterns={},
            classification={"inputs": [], "outputs": [], "chain": []},
            named_ranges=[],
            domain="test",
        )
        ast.parse(code)
        # Still valid Python even with no functions
        assert '"""' in code

    def test_has_main_block(self):
        from scripts.data.doc_intelligence.module_assembler import (
            assemble_module,
        )

        code = assemble_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            named_ranges=[],
            domain="installation",
        )
        assert 'if __name__ == "__main__":' in code
