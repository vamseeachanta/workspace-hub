"""Tests for test_generator_v2 — generate baseline + parametric tests."""

import ast

import pytest


def _synthetic_patterns():
    return {
        "=A1*B1": [
            {"cell_ref": f"C{r}", "sheet": "S1",
             "formula": f"=A{r}*B{r}", "cached_value": float(r * 10),
             "references": [f"A{r}", f"B{r}"]}
            for r in range(5, 8)
        ],
        "=SQRT(A1)": [
            {"cell_ref": "D5", "sheet": "S1",
             "formula": "=SQRT(A5)", "cached_value": 2.236,
             "references": ["A5"]}
        ],
    }


def _synthetic_classification():
    return {
        "inputs": ["A5", "B5"],
        "outputs": ["C7", "D5"],
        "chain": [],
    }


class TestGenerateTestModule:
    """Generate test module with baseline + parametric variations."""

    def test_output_is_valid_python(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
        )
        ast.parse(code)

    def test_has_baseline_tests(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
        )
        assert "def test_" in code
        assert "pytest.approx" in code

    def test_has_parametric_variations(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
        )
        # Should have parametrize decorator for variations
        assert "parametrize" in code or "variation" in code.lower()

    def test_cached_values_in_assertions(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
        )
        # At least one cached value appears
        assert "50.0" in code or "60.0" in code or "70.0" in code

    def test_imports_present(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
        )
        assert "import pytest" in code

    def test_empty_patterns(self):
        from scripts.data.doc_intelligence.test_generator_v2 import (
            generate_test_module,
        )

        code = generate_test_module(
            stem="empty",
            patterns={},
            classification={"inputs": [], "outputs": [], "chain": []},
            formulas={"formulas": []},
        )
        ast.parse(code)
