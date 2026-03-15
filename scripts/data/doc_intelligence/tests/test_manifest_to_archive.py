# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Tests for manifest_to_archive.py — TDD first pass."""

import sys
from pathlib import Path

# Allow importing the module from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from manifest_to_archive import (
    extract_equations,
    extract_inputs_outputs,
    manifest_to_archive,
)


# ---------------------------------------------------------------------------
# extract_equations
# ---------------------------------------------------------------------------


def test_extract_equations_from_section_text():
    text = (
        "The wall thickness is calculated per DNV-ST-F101 Eq. 5.16:\n"
        "t_min = (P_d * D) / (2 * f_y * alpha_U)\n"
        "where P_d is design pressure and D is outer diameter."
    )
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert equations[0]["name"] == "Eq. 5.16"
    assert "P_d" in equations[0]["formula"]
    assert equations[0]["standard"] == "DNV-ST-F101"


def test_extract_equations_empty_text():
    equations = extract_equations("")
    assert equations == []


def test_extract_equations_equation_keyword():
    text = (
        "See Equation (3.2) for the combined load:\n"
        "F_total = F_axial + F_bending\n"
    )
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert "3.2" in equations[0]["name"]


def test_extract_equations_eqn_abbreviation():
    text = "Per API RP 2A Eqn. A-1:\nstress = force / area\n"
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert "A-1" in equations[0]["name"]
    assert equations[0]["standard"] == "API RP 2A"


def test_extract_equations_eq_no_dot():
    text = "From ISO 19901-1 eq 12:\npressure = force / area\n"
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert "12" in equations[0]["name"]
    assert equations[0]["standard"] == "ISO 19901-1"


def test_extract_equations_no_formula_line():
    # Equation reference but no formula on the next line — should still return entry
    text = "This follows from Eq. 7.3 in the standard.\nSee table 1."
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert equations[0]["name"] == "Eq. 7.3"
    assert equations[0]["formula"] == ""


def test_extract_equations_multiple():
    text = (
        "Per DNV-ST-F101 Eq. 5.16:\n"
        "t_min = P_d * D / (2 * f_y)\n"
        "And also Eq. 5.17:\n"
        "t_corr = t_min + t_fab\n"
    )
    equations = extract_equations(text)
    assert len(equations) >= 2


def test_extract_equations_description_populated():
    text = (
        "The burst pressure per Eq. 8.1:\n"
        "P_b = 2 * t * SMYS / D\n"
        "This equation gives the burst pressure of the pipe."
    )
    equations = extract_equations(text)
    assert len(equations) >= 1
    assert equations[0]["description"] != ""


# ---------------------------------------------------------------------------
# extract_inputs_outputs
# ---------------------------------------------------------------------------


def test_extract_inputs_outputs_basic():
    text = (
        "where P_d is the design pressure (MPa)\n"
        "where D is the outer diameter (mm)\n"
    )
    inputs, outputs = extract_inputs_outputs(text)
    assert len(inputs) >= 2
    symbols = [i["symbol"] for i in inputs]
    assert "P_d" in symbols
    assert "D" in symbols


def test_extract_inputs_outputs_units_captured():
    text = "where t_min is the minimum wall thickness (mm)\n"
    inputs, outputs = extract_inputs_outputs(text)
    assert len(inputs) >= 1
    t = next(i for i in inputs if i["symbol"] == "t_min")
    assert t["unit"] == "mm"


def test_extract_inputs_outputs_empty():
    inputs, outputs = extract_inputs_outputs("")
    assert inputs == []
    assert outputs == []


def test_extract_inputs_outputs_no_unit():
    text = "where alpha is the material factor\n"
    inputs, outputs = extract_inputs_outputs(text)
    assert len(inputs) >= 1
    a = next(i for i in inputs if i["symbol"] == "alpha")
    assert a["unit"] == ""


def test_extract_inputs_outputs_returns_tuple():
    result = extract_inputs_outputs("some text")
    assert isinstance(result, tuple)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# manifest_to_archive — full roundtrip
# ---------------------------------------------------------------------------


def test_manifest_to_archive_full_roundtrip():
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "doc_ref": "DNV-ST-F101",
        "metadata": {"filename": "dnv-st-f101.pdf", "format": "pdf", "size_bytes": 500000},
        "sections": [
            {
                "heading": "Wall Thickness Design",
                "level": 2,
                "text": (
                    "The minimum wall thickness per DNV-ST-F101 Eq. 5.16:\n"
                    "t_min = (P_d * D) / (2 * f_y * alpha_U)\n"
                    "where P_d is the design pressure (MPa)\n"
                    "where D is the outer diameter (mm)"
                ),
                "source": {"document": "dnv-st-f101.pdf", "page": 42},
            }
        ],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {"sections": 1, "tables": 0, "figure_refs": 0},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "pipeline", "wall_thickness")
    assert archive["category"] == "pipeline"
    assert archive["subcategory"] == "wall_thickness"
    assert archive["source_type"] == "pdf"
    assert archive["legal_scan_passed"] is False
    assert len(archive["equations"]) >= 1
    assert len(archive["inputs"]) >= 1
    assert "DNV-ST-F101" in archive["references"]


def test_manifest_to_archive_required_keys():
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "metadata": {"filename": "test.pdf", "format": "pdf", "size_bytes": 1000},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "structural", "beam_design")
    required_keys = [
        "source_type",
        "source_description",
        "extracted_date",
        "legal_scan_passed",
        "category",
        "subcategory",
        "equations",
        "inputs",
        "outputs",
        "worked_examples",
        "assumptions",
        "references",
        "notes",
    ]
    for key in required_keys:
        assert key in archive, f"Missing required key: {key}"


def test_manifest_to_archive_source_description_uses_filename():
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "metadata": {"filename": "api-rp-2a.pdf", "format": "pdf", "size_bytes": 200000},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "structural", "jacket_design")
    assert "api-rp-2a.pdf" in archive["source_description"]


def test_manifest_to_archive_empty_sections_returns_empty_lists():
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "metadata": {"filename": "empty.pdf", "format": "pdf", "size_bytes": 100},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "test", "test")
    assert archive["equations"] == []
    assert archive["inputs"] == []
    assert archive["outputs"] == []
    assert archive["worked_examples"] == []
    assert archive["assumptions"] == []


def test_manifest_to_archive_references_deduplicated():
    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "metadata": {"filename": "test.pdf", "format": "pdf", "size_bytes": 1000},
        "sections": [
            {
                "heading": "Section 1",
                "level": 1,
                "text": "Per DNV-ST-F101 Eq. 1.1:\na = b\nPer DNV-ST-F101 Eq. 1.2:\nc = d",
                "source": {"document": "test.pdf", "page": 1},
            }
        ],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "test", "test")
    # References list should not contain duplicates
    refs = archive["references"]
    assert len(refs) == len(set(refs))


def test_manifest_to_archive_extracted_date_format():
    import re

    manifest = {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "engineering-standards",
        "metadata": {"filename": "test.pdf", "format": "pdf", "size_bytes": 1000},
        "sections": [],
        "tables": [],
        "figure_refs": [],
        "extraction_stats": {},
        "errors": [],
    }
    archive = manifest_to_archive(manifest, "test", "test")
    assert re.match(r"\d{4}-\d{2}-\d{2}", archive["extracted_date"])
