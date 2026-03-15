# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""TDD tests for extract_engineering_constants.py."""

import sys
from pathlib import Path

import pytest

_repo_root = str(Path(__file__).resolve().parents[4])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.extract_engineering_constants import (
    extract_constants_from_table,
    extract_constants_from_text,
    extract_all_constants,
)


# ---------------------------------------------------------------------------
# extract_constants_from_table
# ---------------------------------------------------------------------------

def test_extract_constants_from_table():
    table = {
        "columns": ["Parameter", "Value", "Unit"],
        "rows": [
            ["Yield strength", "450", "MPa"],
            ["Young's modulus", "207000", "MPa"],
            ["Poisson's ratio", "0.3", "-"],
        ],
    }
    constants = extract_constants_from_table(table)
    assert len(constants) == 3
    assert constants[0]["name"] == "Yield strength"
    assert constants[0]["value"] == 450.0
    assert constants[0]["unit"] == "MPa"


def test_extract_constants_empty():
    assert extract_constants_from_table({"columns": [], "rows": []}) == []
    assert extract_constants_from_text("") == []


def test_extract_constants_no_numeric():
    table = {"columns": ["Name", "Description"], "rows": [["Steel", "Carbon steel"]]}
    assert extract_constants_from_table(table) == []


def test_table_value_column_variants():
    """Columns named 'Value', 'val', 'magnitude' etc should all be detected."""
    table = {
        "columns": ["Property", "Magnitude", "Units"],
        "rows": [["Density", "7850", "kg/m3"]],
    }
    constants = extract_constants_from_table(table)
    assert len(constants) == 1
    assert constants[0]["value"] == 7850.0
    assert constants[0]["unit"] == "kg/m3"


def test_table_no_unit_column():
    """Table without a unit column should still parse name+value."""
    table = {
        "columns": ["Parameter", "Value"],
        "rows": [["Safety factor", "1.5"]],
    }
    constants = extract_constants_from_table(table)
    assert len(constants) == 1
    assert constants[0]["value"] == 1.5
    assert constants[0]["unit"] is None


def test_table_non_numeric_value_skipped():
    """Rows where the value cell is not a number should be skipped."""
    table = {
        "columns": ["Parameter", "Value", "Unit"],
        "rows": [
            ["Material type", "Carbon steel", "-"],
            ["Yield strength", "450", "MPa"],
        ],
    }
    constants = extract_constants_from_table(table)
    assert len(constants) == 1
    assert constants[0]["name"] == "Yield strength"


def test_table_dash_unit_normalised_to_none():
    """A unit of '-' or 'dimensionless' should be returned as None."""
    table = {
        "columns": ["Parameter", "Value", "Unit"],
        "rows": [["Poisson's ratio", "0.3", "-"]],
    }
    constants = extract_constants_from_table(table)
    assert constants[0]["unit"] is None


def test_table_source_column():
    """Optional 'Source' / 'Reference' column should be captured."""
    table = {
        "columns": ["Parameter", "Value", "Unit", "Source"],
        "rows": [["Yield strength", "450", "MPa", "API 5L"]],
    }
    constants = extract_constants_from_table(table)
    assert constants[0]["source"] == "API 5L"


# ---------------------------------------------------------------------------
# extract_constants_from_text
# ---------------------------------------------------------------------------

def test_extract_constants_from_text():
    text = "The yield strength f_y = 450 MPa and modulus E = 207 GPa."
    constants = extract_constants_from_text(text)
    assert len(constants) >= 2


def test_text_symbol_equals_number_unit():
    text = "E = 207 GPa"
    constants = extract_constants_from_text(text)
    assert len(constants) == 1
    assert constants[0]["value"] == 207.0
    assert constants[0]["unit"] == "GPa"


def test_text_symbol_only_no_unit():
    text = "Safety factor γ = 1.35"
    constants = extract_constants_from_text(text)
    assert len(constants) == 1
    assert constants[0]["value"] == 1.35
    assert constants[0]["unit"] is None


def test_text_no_constants():
    text = "This section describes general requirements for pipeline design."
    constants = extract_constants_from_text(text)
    assert constants == []


def test_text_scientific_notation():
    text = "Fracture toughness K_IC = 1.5e2 MPa·m^0.5"
    constants = extract_constants_from_text(text)
    assert len(constants) >= 1
    assert abs(constants[0]["value"] - 150.0) < 1e-6


def test_text_multiple_matches():
    text = (
        "Assume f_y = 355 MPa, E_s = 200 GPa, "
        "and safety factor SF = 2.0 for design checks."
    )
    constants = extract_constants_from_text(text)
    assert len(constants) >= 3


# ---------------------------------------------------------------------------
# extract_all_constants
# ---------------------------------------------------------------------------

def test_extract_all_constants_from_manifest():
    manifest = {
        "sections": [
            {
                "heading": "Material Properties",
                "text": "Yield strength f_y = 450 MPa",
                "tables": [
                    {
                        "columns": ["Parameter", "Value", "Unit"],
                        "rows": [["Young's modulus", "207000", "MPa"]],
                    }
                ],
            }
        ]
    }
    constants = extract_all_constants(manifest)
    names = [c["name"] for c in constants]
    assert any("f_y" in n or "yield" in n.lower() for n in names)
    assert any("Young" in n or "modulus" in n.lower() for n in names)


def test_extract_all_constants_deduplication():
    """Same name+value pair appearing in text and table should not duplicate."""
    manifest = {
        "sections": [
            {
                "text": "E = 207000 MPa",
                "tables": [
                    {
                        "columns": ["Parameter", "Value", "Unit"],
                        "rows": [["E", "207000", "MPa"]],
                    }
                ],
            }
        ]
    }
    constants = extract_all_constants(manifest)
    e_constants = [c for c in constants if c["name"] == "E" and c["value"] == 207000.0]
    assert len(e_constants) == 1


def test_extract_all_constants_empty_manifest():
    assert extract_all_constants({}) == []
    assert extract_all_constants({"sections": []}) == []


def test_extract_all_constants_no_tables_no_text():
    manifest = {"sections": [{"heading": "Intro"}]}
    constants = extract_all_constants(manifest)
    assert constants == []
