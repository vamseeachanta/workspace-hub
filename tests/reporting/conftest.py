"""Shared fixtures and imports for calculation report tests."""
import importlib.util
import os
import sys

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the hyphenated module via importlib
_script_dir = os.path.join(REPO_ROOT, "scripts", "reporting")
sys.path.insert(0, _script_dir)

_spec = importlib.util.spec_from_file_location(
    "generate_calc_report",
    os.path.join(_script_dir, "generate-calc-report.py"),
)
generate_calc_report = importlib.util.module_from_spec(_spec)
sys.modules["generate_calc_report"] = generate_calc_report
_spec.loader.exec_module(generate_calc_report)

EXAMPLE_GIRTH = os.path.join(
    REPO_ROOT, "examples", "reporting", "fatigue-pipeline-girth-weld.yaml"
)
EXAMPLE_SCR = os.path.join(
    REPO_ROOT, "examples", "reporting", "fatigue-scr-touchdown.yaml"
)


@pytest.fixture
def girth_weld_data():
    with open(EXAMPLE_GIRTH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def scr_data():
    with open(EXAMPLE_SCR) as f:
        return yaml.safe_load(f)


@pytest.fixture
def minimal_valid():
    """Minimal valid calculation YAML data."""
    return {
        "metadata": {
            "title": "Test Calc",
            "doc_id": "CALC-TEST",
            "revision": 1,
            "date": "2026-01-01",
            "author": "Test Author",
            "status": "draft",
        },
        "inputs": [
            {"name": "Load", "symbol": "P", "value": 100, "unit": "kN"},
        ],
        "methodology": {
            "description": "Simple load check.",
            "standard": "EN 1993-1-1",
            "equations": [
                {
                    "id": 1,
                    "name": "Unity Check",
                    "latex": "UC = \\frac{P}{P_{Rd}}",
                    "description": "Ratio of applied to resistance.",
                },
            ],
        },
        "outputs": [
            {"name": "Unity Check", "symbol": "UC", "value": 0.65, "unit": "-"},
        ],
        "assumptions": ["Material is linear elastic"],
        "references": ["EN 1993-1-1:2005"],
    }
