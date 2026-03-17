"""TDD tests for O*NET task tagging (WRK-5003)."""
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
import tag_onet
import observed_exposure_report as oer


# --- O*NET code format validation ---


@pytest.mark.parametrize("code,valid", [
    ("15-1251.00", True),
    ("43-9021.00", True),
    ("11-1021.00", True),
    ("15-1251", False),         # missing decimal portion
    ("151251.00", False),       # missing hyphen
    ("15-125.00", False),       # too few digits after hyphen
    ("XX-1251.00", False),      # non-numeric
    ("", False),
])
def test_onet_code_format_validation(code, valid):
    """O*NET codes must match XX-XXXX.XX pattern."""
    assert tag_onet.is_valid_onet_code(code) is valid


# --- Lookup table sanity ---


def test_lookup_table_codes_are_valid():
    """Every code in the built-in lookup table passes format validation."""
    for code in tag_onet.ONET_LOOKUP:
        assert tag_onet.is_valid_onet_code(code), f"Invalid code in lookup: {code}"


def test_lookup_table_has_minimum_entries():
    """Lookup table has at least 10 relevant O*NET categories."""
    assert len(tag_onet.ONET_LOOKUP) >= 10


# --- Tag suggestion from title/mission ---


def test_tag_suggests_software_dev_for_coding_wrk():
    """A WRK about writing Python code should suggest software dev codes."""
    suggestions = tag_onet.suggest_onet_codes(
        title="Add pytest fixtures for CP module",
        mission="Write unit tests for cathodic protection calculations",
    )
    assert len(suggestions) <= 3
    assert len(suggestions) >= 1
    # Should include a software/CS code (15-xxxx family)
    codes = [s["code"] for s in suggestions]
    assert any(c.startswith("15-") for c in codes)


def test_tag_suggests_data_analysis_for_data_wrk():
    """A WRK about data analysis should suggest data/stats codes."""
    suggestions = tag_onet.suggest_onet_codes(
        title="Build EIA drilling economics aggregator",
        mission="Aggregate and analyze drilling cost data from EIA datasets",
    )
    assert len(suggestions) >= 1
    codes = [s["code"] for s in suggestions]
    # Data analysts (15-2051) or statisticians or similar
    assert any(c.startswith("15-") or c.startswith("13-") for c in codes)


def test_tag_returns_empty_for_empty_input():
    """Empty title and mission returns empty suggestions."""
    suggestions = tag_onet.suggest_onet_codes(title="", mission="")
    assert suggestions == []


# --- Suggestion structure ---


def test_suggestion_structure():
    """Each suggestion has code, label, and score fields."""
    suggestions = tag_onet.suggest_onet_codes(
        title="Fix CI pipeline configuration",
        mission="Update GitHub Actions workflow for automated testing",
    )
    for s in suggestions:
        assert "code" in s
        assert "label" in s
        assert "score" in s
        assert tag_onet.is_valid_onet_code(s["code"])
        assert isinstance(s["label"], str)
        assert isinstance(s["score"], (int, float))


# --- WRK file reading ---


def _write_wrk_md(
    path: Path, wrk_id: str, category: str = "engineering",
    onet_category: str | None = None,
) -> None:
    """Helper: write a WRK .md with optional onet_category."""
    path.parent.mkdir(parents=True, exist_ok=True)
    onet_line = f'onet_category: "{onet_category}"\n' if onet_category else ""
    content = (
        f"---\n"
        f"id: {wrk_id}\n"
        f'title: "Test item"\n'
        f"status: pending\n"
        f"category: {category}\n"
        f"{onet_line}"
        f"---\n\n"
        f"## Mission\nTest\n"
    )
    path.write_text(content)


def test_read_wrk_extracts_onet_category(tmp_path):
    """tag_onet.read_wrk_frontmatter extracts onet_category field."""
    wrk_path = tmp_path / "WRK-5003.md"
    _write_wrk_md(wrk_path, "WRK-5003", onet_category="15-1251.00 — Computer Programmers")
    fm = tag_onet.read_wrk_frontmatter(wrk_path)
    assert fm["onet_category"] == "15-1251.00 — Computer Programmers"


# --- observed_exposure_report groups by onet ---


def _write_stage_evidence(assets_dir: Path, wrk_id: str, stages: list[dict]):
    evidence_dir = assets_dir / wrk_id / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    data = {"wrk_id": wrk_id, "stages": stages}
    (evidence_dir / "stage-evidence.yaml").write_text(yaml.dump(data))


def _make_stage(order: int, status: str = "done") -> dict:
    return {"order": order, "stage": f"Stage {order}", "status": status}


def test_report_groups_by_onet_category(tmp_path):
    """When onet_category is present, aggregate_by_onet groups by it."""
    queue_root = tmp_path / "queue"

    _write_wrk_md(
        queue_root / "pending" / "WRK-600.md", "WRK-600",
        category="engineering",
        onet_category="15-1251.00 — Computer Programmers",
    )
    _write_stage_evidence(
        queue_root / "assets", "WRK-600",
        [_make_stage(i) for i in range(1, 6)],
    )

    _write_wrk_md(
        queue_root / "pending" / "WRK-601.md", "WRK-601",
        category="data",
        onet_category="15-2051.00 — Data Scientists",
    )
    _write_stage_evidence(
        queue_root / "assets", "WRK-601",
        [_make_stage(i) for i in range(1, 4)],
    )

    (queue_root / "working").mkdir(parents=True, exist_ok=True)

    wrk_list = oer.scan_wrk_files(queue_root)
    for wrk in wrk_list:
        evidence = oer.load_stage_evidence(wrk["id"], queue_root)
        total, ai, human = oer.classify_stages(evidence)
        wrk["total"] = total
        wrk["ai"] = ai
        wrk["human"] = human

    agg = oer.aggregate_by_onet(wrk_list)
    assert "15-1251.00 — Computer Programmers" in agg
    assert "15-2051.00 — Data Scientists" in agg
    assert agg["15-1251.00 — Computer Programmers"]["wrk_count"] == 1
    assert agg["15-2051.00 — Data Scientists"]["wrk_count"] == 1


def test_report_onet_skips_items_without_onet(tmp_path):
    """Items without onet_category are grouped under 'untagged'."""
    queue_root = tmp_path / "queue"

    _write_wrk_md(
        queue_root / "pending" / "WRK-700.md", "WRK-700",
        category="engineering",
    )
    _write_stage_evidence(
        queue_root / "assets", "WRK-700",
        [_make_stage(1, "done")],
    )
    (queue_root / "working").mkdir(parents=True, exist_ok=True)

    wrk_list = oer.scan_wrk_files(queue_root)
    for wrk in wrk_list:
        evidence = oer.load_stage_evidence(wrk["id"], queue_root)
        total, ai, human = oer.classify_stages(evidence)
        wrk["total"] = total
        wrk["ai"] = ai
        wrk["human"] = human

    agg = oer.aggregate_by_onet(wrk_list)
    assert "untagged" in agg
