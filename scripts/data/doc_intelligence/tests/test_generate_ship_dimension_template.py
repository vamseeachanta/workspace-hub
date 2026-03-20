# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Tests for generate-ship-dimension-template.py — TDD first pass."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate_ship_dimension_template import (
    build_dimension_entries,
    build_template_document,
)

# --- Fixtures ---

SAMPLE_PLANS = [
    {
        "filename": "ac3.pdf",
        "stem": "ac3",
        "hull_code": "ac",
        "hull_number": 3,
        "vessel_type": "Collier",
        "pages": 4,
        "has_text": False,
        "sections": 0,
        "tables": 0,
    },
    {
        "filename": "bb61.pdf",
        "stem": "bb61",
        "hull_code": "bb",
        "hull_number": 61,
        "vessel_type": "Battleship",
        "pages": 12,
        "has_text": False,
        "sections": 0,
        "tables": 0,
    },
    {
        "filename": "dd445.pdf",
        "stem": "dd445",
        "hull_code": "dd",
        "hull_number": 445,
        "vessel_type": "Destroyer",
        "pages": 8,
        "has_text": False,
        "sections": 0,
        "tables": 0,
    },
]

DIMENSION_KEYS = [
    "length_overall_ft",
    "beam_ft",
    "draft_ft",
    "depth_ft",
    "displacement_lt",
    "speed_kts",
]


def test_generates_template_from_plans_index():
    """Given a plans index with 3 entries, generates correct vessel entries."""
    entries = build_dimension_entries(SAMPLE_PLANS)
    assert len(entries) == 3
    stems = [e["stem"] for e in entries]
    assert stems == ["ac3", "bb61", "dd445"]
    for entry in entries:
        assert entry["dimensions"] is not None
        for key in DIMENSION_KEYS:
            assert entry["dimensions"][key] is None


def test_skips_plans_with_text():
    """Plans with has_text: true are skipped."""
    plans = [
        {**SAMPLE_PLANS[0], "has_text": True},
        SAMPLE_PLANS[1],
    ]
    entries = build_dimension_entries(plans)
    assert len(entries) == 1
    assert entries[0]["stem"] == "bb61"


def test_output_schema():
    """Each entry has the required fields with correct types."""
    entries = build_dimension_entries(SAMPLE_PLANS[:1])
    entry = entries[0]

    assert entry["stem"] == "ac3"
    assert entry["hull_code"] == "ac"
    assert entry["hull_number"] == 3
    assert entry["vessel_type"] == "Collier"
    assert entry["source_plan"] == "ac3.pdf"
    assert entry["entry_status"] == "pending"

    dims = entry["dimensions"]
    for key in DIMENSION_KEYS:
        assert key in dims
        assert dims[key] is None


def test_empty_plans_index():
    """Empty input produces valid template with empty entries list."""
    doc = build_template_document([])
    assert doc["version"] == "1.0.0"
    assert doc["total_entries"] == 0
    assert doc["entries"] == []
    assert "description" in doc
    assert "generated_at" in doc
