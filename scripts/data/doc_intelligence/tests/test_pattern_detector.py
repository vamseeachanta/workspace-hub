"""Tests for pattern_detector — normalize formulas and detect row patterns."""

import pytest


class TestNormalizeFormula:
    """Normalize Excel formulas to row-1 canonical form."""

    def test_simple_arithmetic_row5(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # =A5*B5 at row 5 should normalize to =A1*B1
        result = normalize_formula("=A5*B5", "C5")
        assert result == "=A1*B1"

    def test_already_row1(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        result = normalize_formula("=A1+B1", "C1")
        assert result == "=A1+B1"

    def test_absolute_row_ref_unchanged(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # $A$3 is absolute — should stay as $A$3 regardless of cell position
        result = normalize_formula("=$A$3*B5", "C5")
        assert result == "=$A$3*B1"

    def test_mixed_ref_dollar_col(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # $A5 → col absolute, row relative → row shifts to 1
        result = normalize_formula("=$A5+C5", "D5")
        assert result == "=$A1+C1"

    def test_mixed_ref_dollar_row(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # A$5 → row absolute, col relative → stays A$5
        result = normalize_formula("=A$5+B10", "C10")
        assert result == "=A$5+B1"

    def test_cross_sheet_ref(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        result = normalize_formula("=Sheet1!A5*2", "B5")
        assert result == "=Sheet1!A1*2"

    def test_function_with_refs(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        result = normalize_formula("=SQRT(A10)+PI()", "B10")
        assert result == "=SQRT(A1)+PI()"

    def test_no_refs_constant(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # Pure constant formula stays unchanged
        result = normalize_formula("=40/3.28084*3", "E47")
        assert result == "=40/3.28084*3"

    def test_translator_failure_returns_original(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            normalize_formula,
        )

        # Malformed formula — should return original as fallback
        result = normalize_formula("=???BROKEN", "A1")
        assert result == "=???BROKEN"


class TestDetectRowPatterns:
    """Group formulas by their canonical normalized form."""

    def test_identical_formulas_across_rows(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        formulas = [
            {"cell_ref": "C5", "sheet": "S1", "formula": "=A5*B5",
             "cached_value": 10, "references": ["A5", "B5"]},
            {"cell_ref": "C6", "sheet": "S1", "formula": "=A6*B6",
             "cached_value": 20, "references": ["A6", "B6"]},
            {"cell_ref": "C7", "sheet": "S1", "formula": "=A7*B7",
             "cached_value": 30, "references": ["A7", "B7"]},
        ]
        patterns = detect_row_patterns(formulas)
        # All three normalize to =A1*B1 → one pattern group
        assert len(patterns) == 1
        canonical = list(patterns.keys())[0]
        assert canonical == "=A1*B1"
        assert len(patterns[canonical]) == 3

    def test_different_formulas_separate_groups(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        formulas = [
            {"cell_ref": "C5", "sheet": "S1", "formula": "=A5*B5",
             "cached_value": 10, "references": ["A5", "B5"]},
            {"cell_ref": "D5", "sheet": "S1", "formula": "=A5+B5",
             "cached_value": 5, "references": ["A5", "B5"]},
        ]
        patterns = detect_row_patterns(formulas)
        assert len(patterns) == 2

    def test_absolute_refs_form_own_group(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        # =$A$3*B5 and =$A$3*B6 should group together
        formulas = [
            {"cell_ref": "C5", "sheet": "S1", "formula": "=$A$3*B5",
             "cached_value": 10, "references": ["$A$3", "B5"]},
            {"cell_ref": "C6", "sheet": "S1", "formula": "=$A$3*B6",
             "cached_value": 20, "references": ["$A$3", "B6"]},
        ]
        patterns = detect_row_patterns(formulas)
        assert len(patterns) == 1

    def test_empty_input(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        patterns = detect_row_patterns([])
        assert patterns == {}

    def test_pattern_cells_preserve_original_data(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        formulas = [
            {"cell_ref": "C5", "sheet": "S1", "formula": "=A5*B5",
             "cached_value": 10, "references": ["A5", "B5"]},
        ]
        patterns = detect_row_patterns(formulas)
        cell = list(patterns.values())[0][0]
        assert cell["cell_ref"] == "C5"
        assert cell["cached_value"] == 10


class TestComputeCompressionStats:
    """Compute compression ratio from patterns."""

    def test_basic_compression(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            compute_compression_stats,
        )

        # 3 cells → 1 unique pattern → compression ratio 3.0
        patterns = {
            "=A1*B1": [
                {"cell_ref": "C5"}, {"cell_ref": "C6"}, {"cell_ref": "C7"},
            ],
        }
        stats = compute_compression_stats(patterns)
        assert stats["total_cells"] == 3
        assert stats["unique_patterns"] == 1
        assert stats["compression_ratio"] == 3.0

    def test_no_compression(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            compute_compression_stats,
        )

        patterns = {
            "=A1*B1": [{"cell_ref": "C5"}],
            "=A1+B1": [{"cell_ref": "D5"}],
        }
        stats = compute_compression_stats(patterns)
        assert stats["total_cells"] == 2
        assert stats["unique_patterns"] == 2
        assert stats["compression_ratio"] == 1.0

    def test_empty_patterns(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            compute_compression_stats,
        )

        stats = compute_compression_stats({})
        assert stats["total_cells"] == 0
        assert stats["unique_patterns"] == 0
        assert stats["compression_ratio"] == 0.0

    def test_mixed_groups(self):
        from scripts.data.doc_intelligence.pattern_detector import (
            compute_compression_stats,
        )

        patterns = {
            "=A1*B1": [{"cell_ref": f"C{i}"} for i in range(1, 11)],
            "=SQRT(A1)": [{"cell_ref": "D1"}, {"cell_ref": "D2"}],
        }
        stats = compute_compression_stats(patterns)
        assert stats["total_cells"] == 12
        assert stats["unique_patterns"] == 2
        assert stats["compression_ratio"] == 6.0


class TestPerformance:
    """Pattern detection handles large datasets efficiently."""

    def test_10k_formulas_under_2s(self):
        import time

        from scripts.data.doc_intelligence.pattern_detector import (
            detect_row_patterns,
        )

        formulas = []
        for i in range(1, 10001):
            # 100 unique patterns, each repeated 100 times
            pattern_idx = i % 100
            row = i
            formulas.append({
                "cell_ref": f"C{row}",
                "sheet": "S1",
                "formula": f"=A{row}*B{row}+{pattern_idx}",
                "cached_value": float(i),
                "references": [f"A{row}", f"B{row}"],
            })
        start = time.time()
        patterns = detect_row_patterns(formulas)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"10K formulas took {elapsed:.2f}s"
        assert len(patterns) == 100
