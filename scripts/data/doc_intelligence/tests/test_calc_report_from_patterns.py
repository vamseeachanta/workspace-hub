"""Tests for calc_report_from_patterns — YAML calc report from patterns."""

import pytest


def _synthetic_patterns():
    return {
        "=A1*B1": [
            {"cell_ref": f"C{r}", "sheet": "S1",
             "formula": f"=A{r}*B{r}", "cached_value": float(r * 10),
             "references": [f"A{r}", f"B{r}"]}
            for r in range(5, 13)
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
        "outputs": ["C12", "D5"],
        "chain": [],
    }


class TestGenerateCalcReportYaml:
    """Generate calc-report YAML from patterns."""

    def test_has_required_metadata(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        assert "metadata" in report
        md = report["metadata"]
        assert "title" in md
        assert "doc_id" in md
        assert "status" in md

    def test_has_inputs_section(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        assert "inputs" in report
        assert isinstance(report["inputs"], list)

    def test_has_methodology_with_equations(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        assert "methodology" in report
        assert "equations" in report["methodology"]

    def test_equation_count_equals_unique_patterns(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        patterns = _synthetic_patterns()
        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=patterns,
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        equations = report["methodology"]["equations"]
        assert len(equations) == len(patterns)

    def test_has_outputs_section(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        assert "outputs" in report

    def test_has_assumptions_and_references(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        assert "assumptions" in report
        assert "references" in report

    def test_compression_stats_in_report(self):
        from scripts.data.doc_intelligence.calc_report_from_patterns import (
            generate_calc_report_yaml,
        )

        report = generate_calc_report_yaml(
            stem="conductor-calc",
            patterns=_synthetic_patterns(),
            classification=_synthetic_classification(),
            formulas={"formulas": []},
            domain="installation",
            stats={"total_cells": 9, "unique_patterns": 2,
                   "compression_ratio": 4.5},
        )
        # Compression stats should appear somewhere in the report
        yaml_str = str(report)
        assert "4.5" in yaml_str or "compression" in yaml_str.lower()
