# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Tests for parse_standard_reference.py — TDD first pass."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parse_standard_reference import parse_reference, extract_all_references


# --- parse_reference: DNV ---

def test_parse_dnv_rp_with_section():
    ref = parse_reference("DNV-RP-C205 Section 4.3.2")
    assert ref["body"] == "DNV"
    assert ref["code"] == "RP-C205"
    assert ref["section"] == "4.3.2"


def test_parse_dnv_st():
    ref = parse_reference("DNV-ST-F101")
    assert ref["body"] == "DNV"
    assert ref["code"] == "ST-F101"


def test_parse_dnv_os():
    ref = parse_reference("DNV-OS-F101")
    assert ref["body"] == "DNV"
    assert ref["code"] == "OS-F101"


def test_parse_dnv_no_section_returns_none():
    ref = parse_reference("DNV-RP-C205")
    assert ref["section"] is None


# --- parse_reference: API ---

def test_parse_api_reference():
    ref = parse_reference("API RP 2A-WSD 22nd Ed.")
    assert ref["body"] == "API"
    assert ref["code"] == "RP 2A-WSD"
    assert ref["edition"] == "22nd"


def test_parse_api_rp_no_edition():
    ref = parse_reference("API RP 2GEO")
    assert ref["body"] == "API"
    assert ref["code"] == "RP 2GEO"
    assert ref["edition"] is None


# --- parse_reference: ISO ---

def test_parse_iso_reference():
    ref = parse_reference("ISO 19901-1:2015")
    assert ref["body"] == "ISO"
    assert ref["code"] == "19901-1"
    assert ref["year"] == 2015


def test_parse_iso_no_part():
    ref = parse_reference("ISO 19906:2019")
    assert ref["body"] == "ISO"
    assert ref["code"] == "19906"
    assert ref["year"] == 2019


def test_parse_iso_no_year():
    ref = parse_reference("ISO 19901-1")
    assert ref["body"] == "ISO"
    assert ref["code"] == "19901-1"
    assert ref["year"] is None


# --- parse_reference: ASME ---

def test_parse_asme_reference():
    ref = parse_reference("ASME B31G")
    assert ref["body"] == "ASME"
    assert ref["code"] == "B31G"


# --- parse_reference: NORSOK ---

def test_parse_norsok_reference():
    ref = parse_reference("NORSOK N-003")
    assert ref["body"] == "NORSOK"
    assert ref["code"] == "N-003"


# --- parse_reference: IEC ---

def test_parse_iec_reference():
    ref = parse_reference("IEC 61400-3")
    assert ref["body"] == "IEC"
    assert ref["code"] == "61400-3"


# --- parse_reference: ABS ---

def test_parse_abs_reference():
    ref = parse_reference("ABS Rules for Building and Classing")
    assert ref["body"] == "ABS"
    assert ref["code"] == "Rules for Building and Classing"


# --- parse_reference: BV ---

def test_parse_bv_reference():
    ref = parse_reference("BV NR 445")
    assert ref["body"] == "BV"
    assert ref["code"] == "NR 445"


# --- parse_reference: LR ---

def test_parse_lr_reference():
    ref = parse_reference("LR Rules")
    assert ref["body"] == "LR"
    assert ref["code"] == "Rules"


# --- parse_reference: unknown ---

def test_parse_unknown_returns_none():
    result = parse_reference("some random text")
    assert result is None


# --- parse_reference: output shape ---

def test_parse_reference_returns_all_keys():
    ref = parse_reference("DNV-RP-C205")
    assert "body" in ref
    assert "code" in ref
    assert "section" in ref
    assert "edition" in ref
    assert "year" in ref
    assert "title" in ref


# --- extract_all_references ---

def test_extract_multiple_from_text():
    text = "Per DNV-ST-F101 and API RP 2A, the design shall comply with ISO 19901-1:2015."
    refs = extract_all_references(text)
    assert len(refs) >= 3
    bodies = [r["body"] for r in refs]
    assert "DNV" in bodies
    assert "API" in bodies
    assert "ISO" in bodies


def test_extract_returns_empty_for_no_references():
    text = "This is a paragraph with no standard references."
    refs = extract_all_references(text)
    assert refs == []


def test_extract_single_reference():
    text = "The pipeline shall be designed per NORSOK N-003."
    refs = extract_all_references(text)
    assert len(refs) >= 1
    assert any(r["body"] == "NORSOK" for r in refs)


def test_extract_preserves_section():
    text = "See DNV-RP-C205 Section 4.3.2 for details."
    refs = extract_all_references(text)
    dnv_refs = [r for r in refs if r["body"] == "DNV"]
    assert len(dnv_refs) == 1
    assert dnv_refs[0]["section"] == "4.3.2"


def test_extract_deduplicates_identical():
    text = "DNV-RP-C205 and DNV-RP-C205 appear twice."
    refs = extract_all_references(text)
    dnv_refs = [r for r in refs if r["code"] == "RP-C205"]
    # Should not return exact duplicates (same body+code+section)
    assert len(dnv_refs) == 1
