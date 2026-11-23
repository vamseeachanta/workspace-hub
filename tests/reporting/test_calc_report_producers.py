"""Producer tests for calculation-report metadata claims."""

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_archive_converter_omits_author_metadata():
    module = _load_module(
        "archive_to_calc_report",
        "scripts/data/doc_intelligence/archive_to_calc_report.py",
    )
    report = module.convert_archive_to_calc_report({
        "subcategory": "synthetic-example",
        "category": "synthetic",
        "extracted_date": "2026-01-01",
        "inputs": [{"name": "Load", "symbol": "P", "unit": "kN", "test_value": 1}],
        "equations": [{"name": "Unity", "excel_formula": "=A1", "description": "Synthetic"}],
        "outputs": [{"name": "Unity", "symbol": "UC", "unit": "-", "test_expected": 1}],
        "assumptions": ["Synthetic assumption"],
        "references": ["Synthetic reference"],
    })

    assert "author" not in report["metadata"]


def test_pattern_report_converter_omits_author_metadata():
    module = _load_module(
        "calc_report_from_patterns",
        "scripts/data/doc_intelligence/calc_report_from_patterns.py",
    )
    report = module.generate_calc_report_yaml(
        stem="synthetic-example",
        patterns={"=A1": [{"sheet": "S1"}]},
        classification={"inputs": ["A1"], "outputs": ["B1"], "chain": []},
        formulas={"formulas": []},
        domain="synthetic",
        stats={"total_cells": 1, "unique_patterns": 1, "compression_ratio": 1},
    )

    assert "author" not in report["metadata"]
