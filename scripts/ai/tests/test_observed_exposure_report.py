"""TDD tests for observed_exposure_report.py."""
import csv
import io
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import observed_exposure_report as oer

HUMAN_GATE_STAGES = oer.HUMAN_GATE_STAGES
aggregate_by_category = oer.aggregate_by_category
classify_stages = oer.classify_stages
format_table = oer.format_table
load_stage_evidence = oer.load_stage_evidence
scan_wrk_files = oer.scan_wrk_files


def _write_wrk_md(path: Path, wrk_id: str, category: str = "engineering") -> None:
    """Helper: write a minimal WRK .md file with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(f"""\
        ---
        id: {wrk_id}
        title: "Test item"
        status: pending
        category: {category}
        ---

        ## Mission
        Test
    """))


def _write_stage_evidence(
    assets_dir: Path, wrk_id: str, stages: list[dict]
) -> None:
    """Helper: write a stage-evidence.yaml for a WRK."""
    import yaml

    evidence_dir = assets_dir / wrk_id / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    data = {"wrk_id": wrk_id, "stages": stages}
    (evidence_dir / "stage-evidence.yaml").write_text(yaml.dump(data))


def _make_stage(order: int, status: str = "done") -> dict:
    """Helper: build a single stage dict."""
    return {"order": order, "stage": f"Stage {order}", "status": status}


# --- Test 1: empty queue ---


def test_empty_queue(tmp_path):
    """No WRK files → empty list from scan."""
    queue_root = tmp_path / "queue"
    (queue_root / "pending").mkdir(parents=True)
    (queue_root / "working").mkdir(parents=True)
    result = scan_wrk_files(queue_root)
    assert result == []


# --- Test 2: single WRK with all stages done ---


def test_single_wrk_all_stages_done(tmp_path):
    """20 stages done → correct AI/human split."""
    queue_root = tmp_path / "queue"
    _write_wrk_md(queue_root / "working" / "WRK-100.md", "WRK-100", "engineering")

    all_stages = [_make_stage(i) for i in range(1, 21)]
    _write_stage_evidence(queue_root / "assets", "WRK-100", all_stages)

    wrk_list = scan_wrk_files(queue_root)
    assert len(wrk_list) == 1
    assert wrk_list[0]["id"] == "WRK-100"
    assert wrk_list[0]["category"] == "engineering"

    evidence = load_stage_evidence("WRK-100", queue_root)
    total, ai, human = classify_stages(evidence)
    assert total == 20
    assert human == 4  # stages 1, 5, 7, 17
    assert ai == 16


# --- Test 3: mixed categories aggregate correctly ---


def test_mixed_categories(tmp_path):
    """Multiple WRKs in different categories aggregate independently."""
    queue_root = tmp_path / "queue"

    # Engineering WRK: 10 stages done
    _write_wrk_md(queue_root / "pending" / "WRK-200.md", "WRK-200", "engineering")
    stages_200 = [_make_stage(i) for i in range(1, 11)]
    _write_stage_evidence(queue_root / "assets", "WRK-200", stages_200)

    # Career WRK: 5 stages done
    _write_wrk_md(queue_root / "working" / "WRK-201.md", "WRK-201", "career")
    stages_201 = [_make_stage(i) for i in range(1, 6)]
    _write_stage_evidence(queue_root / "assets", "WRK-201", stages_201)

    wrk_list = scan_wrk_files(queue_root)
    assert len(wrk_list) == 2

    # Build full data
    for wrk in wrk_list:
        evidence = load_stage_evidence(wrk["id"], queue_root)
        total, ai, human = classify_stages(evidence)
        wrk["total"] = total
        wrk["ai"] = ai
        wrk["human"] = human

    agg = aggregate_by_category(wrk_list)
    assert "engineering" in agg
    assert "career" in agg
    assert agg["engineering"]["wrk_count"] == 1
    assert agg["career"]["wrk_count"] == 1
    # Engineering: stages 1-10 → human gates hit: 1, 5, 7 (stage 17 not reached)
    assert agg["engineering"]["human_stages"] == 3
    assert agg["engineering"]["ai_stages"] == 7
    # Career: stages 1-5 → human gates hit: 1, 5
    assert agg["career"]["human_stages"] == 2
    assert agg["career"]["ai_stages"] == 3


# --- Test 4: partial stages (some pending/skipped) ---


def test_partial_stages(tmp_path):
    """WRK with mix of done/pending/n-a stages → only done counted."""
    queue_root = tmp_path / "queue"
    _write_wrk_md(queue_root / "working" / "WRK-300.md", "WRK-300", "engineering")

    stages = [
        _make_stage(1, "done"),
        _make_stage(2, "done"),
        _make_stage(3, "pending"),
        _make_stage(4, "done"),
        _make_stage(5, "n/a"),
    ]
    _write_stage_evidence(queue_root / "assets", "WRK-300", stages)

    evidence = load_stage_evidence("WRK-300", queue_root)
    total, ai, human = classify_stages(evidence)
    assert total == 3  # only done stages
    assert human == 1  # stage 1
    assert ai == 2  # stages 2, 4


# --- Test 5: missing stage-evidence.yaml → skip gracefully ---


def test_missing_stage_evidence(tmp_path):
    """WRK exists but no stage-evidence.yaml → empty list."""
    queue_root = tmp_path / "queue"
    _write_wrk_md(queue_root / "pending" / "WRK-400.md", "WRK-400", "engineering")

    evidence = load_stage_evidence("WRK-400", queue_root)
    assert evidence == []


# --- Test 6: CSV output ---


def test_csv_output():
    """CSV mode produces parseable CSV with correct headers."""
    data = {
        "engineering": {
            "wrk_count": 2,
            "total_stages": 30,
            "ai_stages": 24,
            "human_stages": 6,
        },
    }
    output = format_table(data, csv_mode=True)
    reader = csv.reader(io.StringIO(output))
    rows = list(reader)
    assert rows[0] == [
        "Category", "WRKs", "Total Stages", "AI Stages",
        "Human Stages", "Observed Exposure %", "Theoretical Max %",
    ]
    assert rows[1][0] == "engineering"
    assert rows[1][1] == "2"
    # Observed = 24/30*100 = 80.0
    assert float(rows[1][5]) == pytest.approx(80.0)


# --- Test 7: human gate stages constant ---


def test_human_gate_stages_match_script():
    """HUMAN_GATE_STAGES matches is-human-gate.sh canonical set."""
    assert HUMAN_GATE_STAGES == {1, 5, 7, 17}


# --- Test 8: format_table markdown output ---


def test_format_table_markdown():
    """Markdown table has correct structure."""
    data = {
        "engineering": {
            "wrk_count": 1,
            "total_stages": 20,
            "ai_stages": 16,
            "human_stages": 4,
        },
    }
    output = format_table(data, csv_mode=False)
    assert "| Category" in output
    assert "engineering" in output
    assert "80.0" in output


# --- Test 9: archive WRK files discovered ---


def test_archive_wrk_files_discovered(tmp_path):
    """WRK files in archive subdirectories are found."""
    queue_root = tmp_path / "queue"
    archive_dir = queue_root / "archive" / "2026-03"
    _write_wrk_md(archive_dir / "WRK-500.md", "WRK-500", "career")

    # Also create pending dir so scan doesn't fail
    (queue_root / "pending").mkdir(parents=True)
    (queue_root / "working").mkdir(parents=True)

    wrk_list = scan_wrk_files(queue_root)
    assert len(wrk_list) == 1
    assert wrk_list[0]["id"] == "WRK-500"
    assert wrk_list[0]["category"] == "career"
