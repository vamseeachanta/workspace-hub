"""Closure checker rules on trimmed public-case fixtures."""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import sys
import uuid


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))

import check_issue_closures as checker


FIXTURE = ROOT / "tests/governance/fixtures/issue-closure-cases.json"


def issues():
    return checker.load_fixture(FIXTURE)


def result_for(number):
    items = issues()
    item = next(issue for issue in items if issue["number"] == number)
    return checker.evaluate_issue(item, items)


def scratch_dir():
    base = Path(os.environ.get("TMPDIR") or os.environ.get("TMP") or ".")
    path = base / f"closure-check-{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


def rule(result, number):
    return next(item for item in result["rules"] if item["rule"] == number)


def test_commit_message_closure_fails_rules_1_and_9():
    result = result_for(1602)
    assert result["verdict"] == "FAIL"
    assert rule(result, 1)["verdict"] == "FAIL"
    assert rule(result, 1)["reason"] == "closer is commit-only or absent"


def test_unmerged_or_changed_review_head_fails_rule_2_but_routes_partial_work():
    result = result_for(2062)
    assert rule(result, 2)["verdict"] == "FAIL"
    assert rule(result, 5)["verdict"] == "PASS"
    assert rule(result, 7)["verdict"] == "PASS"


def test_not_planned_without_successor_fails_rule_6_and_warns_missing_tests():
    result = result_for(1652)
    assert rule(result, 4)["verdict"] == "WARN"
    assert rule(result, 6)["verdict"] == "FAIL"


def test_import_record_created_closed_fails_rule_10():
    result = result_for(214)
    assert rule(result, 9)["verdict"] == "FAIL"


def test_well_evidenced_merged_pr_passes_all_rules():
    result = result_for(1983)
    assert result["verdict"] == "PASS"
    assert {item["verdict"] for item in result["rules"]} == {"PASS"}


def test_bulk_unticked_hedged_and_post_close_edit_findings_are_reported():
    result = result_for(9001)
    assert rule(result, 5)["verdict"] == "FAIL"
    assert rule(result, 7)["verdict"] == "FAIL"
    assert rule(result, 8)["verdict"] == "FAIL"
    assert rule(result, 10)["verdict"] == "WARN"


def test_report_writers_emit_csv_and_markdown():
    items = issues()
    evaluations = [checker.evaluate_issue(item, items) for item in items[:5]]
    directory = scratch_dir()
    try:
        csv_path = directory / "closures.csv"
        md_path = Path(directory) / "closures.md"
        checker.write_csv(csv_path, evaluations, {1983: "DONE"})
        checker.write_markdown(md_path, evaluations, {1983: "DONE"})
        rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
        assert rows[0]["rule"] == "1"
        assert "Issue Closure Check Summary" in md_path.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_cli_fixture_mode_is_read_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network or process call attempted")

    monkeypatch.setattr(checker.subprocess, "run", forbidden)
    directory = scratch_dir()
    try:
        csv_path = directory / "closures.csv"
        md_path = Path(directory) / "closures.md"
        code = checker.main(["--fixture", str(FIXTURE), "--csv", str(csv_path), "--markdown", str(md_path)])
        assert code == 1
        assert csv_path.exists()
        assert md_path.exists()
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_fixture_json_has_no_raw_issue_text_fields():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "title" not in json.dumps(raw).lower()
