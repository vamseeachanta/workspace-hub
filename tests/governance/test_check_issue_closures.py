"""Closure checker rules on trimmed public-case fixtures."""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import pytest


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


def test_commit_message_closure_fails_rule_1():
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


def test_lowercase_rest_state_reason_is_normalized():
    result = result_for(9101)
    assert rule(result, 4)["verdict"] == "WARN"
    assert rule(result, 6)["verdict"] == "PASS"


def test_duplicate_successor_closed_completed_passes_rule_6():
    result = result_for(9102)
    assert rule(result, 6)["verdict"] == "PASS"


def test_import_record_created_closed_fails_rule_9():
    result = result_for(214)
    assert rule(result, 9)["verdict"] == "FAIL"


def test_well_evidenced_merged_pr_passes_all_rules():
    result = result_for(1983)
    assert result["verdict"] == "PASS"
    assert {item["verdict"] for item in result["rules"]} == {"PASS"}


def test_each_cited_path_must_exist_for_rule_3():
    result = checker.evaluate_issue({
        "repository": "fixture",
        "number": 9201,
        "state_reason": "COMPLETED",
        "created_at": "2026-07-27T12:00:00Z",
        "closed_at": "2026-07-27T12:03:00Z",
        "closed_by": "actor",
        "closer_type": "comment",
        "body": "",
        "comments": [{
            "closing_evidence": True,
            "body": "Evidence read at abcdef1. Paths scripts/a.py and tests/b.py. Tests: pytest - 1 passed.",
        }],
        "pull_requests": [],
        "default_branch_shas": ["abcdef1"],
        "paths_at_refs": {"scripts/a.py": True, "tests/b.py": False},
        "successor_states": {},
        "body_edited_after_close": False,
    })
    assert rule(result, 3)["verdict"] == "FAIL"


def test_review_and_body_edit_unavailable_are_not_evaluated():
    result = checker.evaluate_issue({
        "repository": "fixture",
        "number": 9202,
        "state_reason": "COMPLETED",
        "created_at": "2026-07-27T12:00:00Z",
        "closed_at": "2026-07-27T12:03:00Z",
        "closed_by": "actor",
        "closer_type": "merged_pr",
        "body": "",
        "comments": [{
            "closing_evidence": True,
            "body": "Merged PR #5 at abcdef1. Path scripts/a.py. Tests: pytest - 1 passed.",
        }],
        "pull_requests": [{"number": 5, "merged": True, "head_sha": "abcdef1", "review_head_sha": None}],
        "default_branch_shas": ["abcdef1"],
        "paths_at_refs": {"scripts/a.py": True},
        "successor_states": {},
        "body_edited_after_close": None,
    })
    assert rule(result, 2)["verdict"] == checker.NOT_EVALUATED
    assert rule(result, 10)["verdict"] == checker.NOT_EVALUATED
    assert result["verdict"] == "WARN"


def test_timeline_classifies_merged_pr_and_commit_closers(monkeypatch):
    timeline = [{"event": "closed", "actor": {"login": "actor"}, "source": {"issue": {"pull_request": {"url": "https://api.example/repos/o/r/pulls/7"}}}}]
    assert checker._closed_by_timeline(timeline, None) == ("merged_pr", "actor")
    assert checker._closed_by_timeline([{"event": "closed", "commit_id": "abc1234"}], "abc1234")[0] == "commit"


class FakeReader:
    def __init__(self, payload):
        self.payload = payload

    def try_api(self, route):
        return self.payload.get(route)


def test_default_branch_sha_uses_compare_status():
    reader = FakeReader({"repos/o/r/compare/main...abc1234": {"status": "behind"}})
    assert checker._on_default_branch(reader, "o/r", "main", "abc1234") is True
    reader = FakeReader({"repos/o/r/compare/main...abc1234": {"status": "ahead"}})
    assert checker._on_default_branch(reader, "o/r", "main", "abc1234") is False


def test_paginated_search_fails_when_total_exceeds_items(monkeypatch):
    def fake_paginated(self, route):
        return ([{"number": 1}], 2)

    monkeypatch.setattr(checker.GitHubReader, "paginated_api", fake_paginated)
    with pytest.raises(RuntimeError, match="search returned 1 of 2 issues"):
        checker.collect_live("owner/repo", scratch_dir(), closed_from="2026-01-01", closed_to="2026-01-02")


def test_reader_uses_get_pagination_and_read_only_graphql(monkeypatch):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if "--paginate" in argv:
            return subprocess.CompletedProcess(argv, 0, stdout='[{"id":1}]\n', stderr="")
        return subprocess.CompletedProcess(argv, 0, stdout='{"ok":true}', stderr="")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    reader = checker.GitHubReader(scratch_dir())
    reader.api("repos/o/r/issues/1")
    reader.paginated_api("repos/o/r/issues/1/comments?per_page=100")
    reader.graphql("query { viewer { login } }")
    rest_calls = [argv for argv in calls if argv[:3] == ["gh", "api", "--method"]]
    assert rest_calls
    assert all("GET" in argv for argv in rest_calls)
    assert all(flag not in argv for argv in rest_calls for flag in ("-f", "-F", "--input"))
    graphql_calls = [argv for argv in calls if argv[:3] == ["gh", "api", "graphql"]]
    assert graphql_calls and "mutation" not in " ".join(" ".join(argv) for argv in graphql_calls).lower()
    assert all(flag not in argv for argv in graphql_calls for flag in ("-f", "-F", "--input"))


def test_default_cache_dir_is_temporary(monkeypatch):
    created = []

    def fake_mkdtemp(prefix):
        created.append(prefix)
        return str(Path(os.environ.get("TMPDIR") or os.environ.get("TMP") or ".") / "cache")

    monkeypatch.setattr(checker.tempfile, "mkdtemp", fake_mkdtemp)
    reader = checker.GitHubReader()
    assert created == ["closure-check-cache-"]
    assert reader.cache_dir.name == "cache"


def test_report_writers_emit_csv_markdown_and_auditor_agreement():
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
        text = md_path.read_text(encoding="utf-8")
        assert "Issue Closure Check Summary" in text
        assert "Auditor agreement" in text
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


def test_cli_accepts_auditor_csv(monkeypatch):
    monkeypatch.setattr(checker.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network or process call attempted")))
    directory = scratch_dir()
    try:
        auditor = directory / "auditor.csv"
        auditor.write_text("number,auditor_class\n1983,DONE\n", encoding="utf-8", newline="\n")
        csv_path = directory / "closures.csv"
        md_path = directory / "closures.md"
        checker.main(["--fixture", str(FIXTURE), "--auditor", str(auditor), "--csv", str(csv_path), "--markdown", str(md_path)])
        assert "Auditor agreement" in md_path.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_fixture_json_has_no_raw_issue_text_fields():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "title" not in json.dumps(raw).lower()
