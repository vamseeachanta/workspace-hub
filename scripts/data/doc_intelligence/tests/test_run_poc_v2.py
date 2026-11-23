"""Tests for run_poc_v2 — orchestrate v2 pipeline across files."""

import os
import tempfile

import pytest
import yaml


def _synthetic_formulas_yaml():
    """Build a small formulas.yaml-style dict."""
    formulas = []
    # 10 cells with same pattern → should collapse to loop
    for r in range(5, 15):
        formulas.append({
            "cell_ref": f"C{r}",
            "sheet": "Data",
            "formula": f"=A{r}*B{r}",
            "cached_value": float(r * 10),
            "cache_status": "cached_ok",
            "references": [f"A{r}", f"B{r}"],
        })
    # 3 cells with different pattern
    for r in range(5, 8):
        formulas.append({
            "cell_ref": f"D{r}",
            "sheet": "Data",
            "formula": f"=SQRT(A{r})",
            "cached_value": float(r) ** 0.5,
            "cache_status": "cached_ok",
            "references": [f"A{r}"],
        })
    # 1 constant
    formulas.append({
        "cell_ref": "E47",
        "sheet": "Data",
        "formula": "=40/3.28084*3",
        "cached_value": 36.576,
        "cache_status": "cached_ok",
        "references": [],
    })
    return {
        "formulas": formulas,
        "named_ranges": [],
        "input_cells": [],
        "output_cells": [],
        "calculation_chain": [],
        "vba_modules": [],
        "cache_quality": {
            "total_formulas": len(formulas),
            "cached_ok": len(formulas),
            "cached_missing": 0,
            "quality_pct": 100.0,
        },
    }


class TestProcessSingleFile:
    """Test processing a single formulas.yaml through the pipeline."""

    def test_process_produces_all_outputs(self):
        from scripts.data.doc_intelligence.run_poc_v2 import (
            process_single_file,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write synthetic formulas.yaml
            formulas_path = os.path.join(tmpdir, "formulas.yaml")
            with open(formulas_path, "w") as f:
                yaml.dump(_synthetic_formulas_yaml(), f)

            out_dir = os.path.join(tmpdir, "output")
            result = process_single_file(
                formulas_path=formulas_path,
                output_dir=out_dir,
                stem="test-workbook",
                domain="test",
            )

            assert result["status"] == "success"
            assert os.path.exists(
                os.path.join(out_dir, "patterns.yaml")
            )
            assert os.path.exists(
                os.path.join(out_dir, "calculations.py")
            )
            assert os.path.exists(
                os.path.join(out_dir, "test_calculations.py")
            )
            assert os.path.exists(
                os.path.join(out_dir, "calc-report.yaml")
            )

    def test_calculations_py_is_valid_python(self):
        import ast

        from scripts.data.doc_intelligence.run_poc_v2 import (
            process_single_file,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            formulas_path = os.path.join(tmpdir, "formulas.yaml")
            with open(formulas_path, "w") as f:
                yaml.dump(_synthetic_formulas_yaml(), f)

            out_dir = os.path.join(tmpdir, "output")
            process_single_file(
                formulas_path=formulas_path,
                output_dir=out_dir,
                stem="test-wb",
                domain="test",
            )

            calc_path = os.path.join(out_dir, "calculations.py")
            with open(calc_path) as f:
                code = f.read()
            ast.parse(code)

    def test_patterns_yaml_has_compression_stats(self):
        from scripts.data.doc_intelligence.run_poc_v2 import (
            process_single_file,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            formulas_path = os.path.join(tmpdir, "formulas.yaml")
            with open(formulas_path, "w") as f:
                yaml.dump(_synthetic_formulas_yaml(), f)

            out_dir = os.path.join(tmpdir, "output")
            process_single_file(
                formulas_path=formulas_path,
                output_dir=out_dir,
                stem="test-wb",
                domain="test",
            )

            with open(os.path.join(out_dir, "patterns.yaml")) as f:
                pat_data = yaml.safe_load(f)

            assert "compression_stats" in pat_data
            assert pat_data["compression_stats"]["unique_patterns"] == 3
            assert pat_data["compression_stats"]["total_cells"] == 14

    def test_empty_formulas_file(self):
        from scripts.data.doc_intelligence.run_poc_v2 import (
            process_single_file,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            formulas_path = os.path.join(tmpdir, "formulas.yaml")
            with open(formulas_path, "w") as f:
                yaml.dump({"formulas": []}, f)

            out_dir = os.path.join(tmpdir, "output")
            result = process_single_file(
                formulas_path=formulas_path,
                output_dir=out_dir,
                stem="empty-wb",
                domain="test",
            )
            assert result["status"] == "success"
            assert result["unique_patterns"] == 0


class TestCompressionReport:
    """Test compression report generation across files."""

    def test_generate_compression_report(self):
        from scripts.data.doc_intelligence.run_poc_v2 import (
            generate_compression_report,
        )

        results = [
            {"stem": "wb1", "status": "success",
             "total_cells": 100, "unique_patterns": 10,
             "compression_ratio": 10.0, "functions": 10, "loops": 5},
            {"stem": "wb2", "status": "success",
             "total_cells": 50, "unique_patterns": 25,
             "compression_ratio": 2.0, "functions": 25, "loops": 3},
        ]
        report = generate_compression_report(results)
        assert report["total_files"] == 2
        assert report["total_cells"] == 150
        assert report["total_unique_patterns"] == 35
