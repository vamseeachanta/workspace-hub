"""Tests for doc-extraction skill — 3-layer extraction taxonomy.

Validates:
- Main SKILL.md structure and content types
- CP sub-skill domain heuristics
- Drilling-riser sub-skill domain heuristics
- Naval-architecture sub-skill domain heuristics
- File size constraints (400-line limit)
"""

from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "engineering" / "doc-extraction"
MAIN_SKILL = SKILL_ROOT / "SKILL.md"
CP_SKILL = SKILL_ROOT / "cp" / "SKILL.md"
RISER_SKILL = SKILL_ROOT / "drilling-riser" / "SKILL.md"
NAVAL_SKILL = SKILL_ROOT / "naval-architecture" / "SKILL.md"

MAX_LINES = 400

# --- Layer 1: content type taxonomy ---

CONTENT_TYPES = [
    "constants",
    "equations",
    "tables",
    "curves",
    "procedures",
    "requirements",
    "definitions",
    "worked_examples",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


class TestMainSkill:
    """Tests for the main doc-extraction SKILL.md."""

    def test_file_exists(self):
        assert MAIN_SKILL.is_file(), f"Missing {MAIN_SKILL}"

    def test_has_frontmatter(self):
        text = _read(MAIN_SKILL)
        assert text.startswith("---"), "SKILL.md must start with YAML frontmatter"
        # Must have closing frontmatter delimiter
        parts = text.split("---", maxsplit=2)
        assert len(parts) >= 3, "SKILL.md frontmatter not properly closed"

    def test_all_content_types_defined(self):
        text = _read(MAIN_SKILL)
        for ct in CONTENT_TYPES:
            assert ct in text, f"Content type '{ct}' not found in main SKILL.md"

    def test_content_types_have_detection_heuristics(self):
        text = _read(MAIN_SKILL).lower()
        assert "detection" in text or "heuristic" in text, (
            "Main SKILL.md must describe detection heuristics"
        )

    def test_references_sub_skills(self):
        text = _read(MAIN_SKILL)
        assert "cp" in text.lower(), "Main SKILL.md must reference CP sub-skill"
        assert "drilling-riser" in text.lower() or "drilling riser" in text.lower(), (
            "Main SKILL.md must reference drilling-riser sub-skill"
        )
        assert "naval-architecture" in text.lower() or "naval architecture" in text.lower(), (
            "Main SKILL.md must reference naval-architecture sub-skill"
        )

    def test_under_line_limit(self):
        count = _line_count(MAIN_SKILL)
        assert count <= MAX_LINES, f"Main SKILL.md is {count} lines (max {MAX_LINES})"


class TestCPSubSkill:
    """Tests for the CP domain sub-skill."""

    def test_file_exists(self):
        assert CP_SKILL.is_file(), f"Missing {CP_SKILL}"

    def test_cp_keywords_present(self):
        text = _read(CP_SKILL).lower()
        for kw in ["anode", "coating breakdown", "current density", "design life"]:
            assert kw in text, f"CP sub-skill missing keyword: '{kw}'"

    def test_references_dnv_standards(self):
        text = _read(CP_SKILL)
        assert "DNV-RP-B401" in text, "CP sub-skill must reference DNV-RP-B401"
        assert "DNV-RP-F103" in text or "F103" in text, (
            "CP sub-skill must reference DNV-RP-F103"
        )

    def test_under_line_limit(self):
        count = _line_count(CP_SKILL)
        assert count <= MAX_LINES, f"CP SKILL.md is {count} lines (max {MAX_LINES})"


class TestDrillingRiserSubSkill:
    """Tests for the drilling-riser domain sub-skill."""

    def test_file_exists(self):
        assert RISER_SKILL.is_file(), f"Missing {RISER_SKILL}"

    def test_riser_keywords_present(self):
        text = _read(RISER_SKILL).lower()
        for kw in ["viv", "bop", "kill", "choke"]:
            assert kw in text, f"Drilling-riser sub-skill missing keyword: '{kw}'"

    def test_references_standards(self):
        text = _read(RISER_SKILL)
        assert "API RP 16Q" in text or "DNV-RP-C205" in text, (
            "Drilling-riser sub-skill must reference API RP 16Q or DNV-RP-C205"
        )

    def test_under_line_limit(self):
        count = _line_count(RISER_SKILL)
        assert count <= MAX_LINES, f"Drilling-riser SKILL.md is {count} lines (max {MAX_LINES})"


class TestNavalArchitectureSubSkill:
    """Tests for the naval-architecture domain sub-skill."""

    def test_file_exists(self):
        assert NAVAL_SKILL.is_file(), f"Missing {NAVAL_SKILL}"

    def test_stability_keywords_present(self):
        text = _read(NAVAL_SKILL).lower()
        for kw in ["gm", "gz", "kb", "bm"]:
            assert kw in text, f"Naval-arch sub-skill missing stability keyword: '{kw}'"

    def test_resistance_keywords_present(self):
        text = _read(NAVAL_SKILL).lower()
        assert "holtrop" in text, "Naval-arch sub-skill missing 'holtrop'"
        assert "ittc" in text, "Naval-arch sub-skill missing 'ittc'"

    def test_hull_form_coefficients_present(self):
        text = _read(NAVAL_SKILL)
        for coeff in ["Cb", "Cp", "Cm", "Cwp"]:
            assert coeff in text, f"Naval-arch sub-skill missing hull form coefficient: '{coeff}'"

    def test_imo_stability_criteria(self):
        text = _read(NAVAL_SKILL)
        assert "IMO" in text, "Naval-arch sub-skill must reference IMO stability criteria"

    def test_scantling_keyword(self):
        text = _read(NAVAL_SKILL).lower()
        assert "scantling" in text, "Naval-arch sub-skill missing 'scantling'"

    def test_references_standards(self):
        text = _read(NAVAL_SKILL)
        assert "SOLAS" in text or "IMO" in text or "IACS" in text, (
            "Naval-arch sub-skill must reference SOLAS, IMO, or IACS"
        )

    def test_under_line_limit(self):
        count = _line_count(NAVAL_SKILL)
        assert count <= MAX_LINES, f"Naval-arch SKILL.md is {count} lines (max {MAX_LINES})"
