"""Closure checker rules on trimmed public-case fixtures."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

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


def test_historical_decision_preserves_rules_3_and_6():
    result = result_for(9103)
    assert rule(result, 3)["verdict"] == "PASS"
    assert rule(result, 6)["verdict"] == "PASS"


@pytest.mark.parametrize("text", [
    "Maintainer decision recorded.",
    "MAINTAINER DECISION recorded.",
    "Retired after assessment.",
    "Passed date recorded.",
])
def test_existing_decision_terms_remain_accepted(text):
    assert checker.has_decision_text(text)


def test_unrecognised_decision_text_is_rejected():
    assert not checker.has_decision_text("No resolving decision recorded.")


def test_import_record_created_closed_fails_rule_9():
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


def test_timeline_classifies_only_from_closed_event(monkeypatch):
    timeline = [
        {"event": "closed", "actor": {"login": "actor"}},
        {"event": "cross-referenced", "source": {"issue": {"pull_request": {"url": "https://api.example/repos/o/r/pulls/7"}}}},
    ]
    assert checker._closed_by_timeline(timeline) == ("comment", "actor")
    timeline = [
        {"event": "connected", "source": {"issue": {"pull_request": {"url": "https://api.example/repos/o/r/pulls/7"}}}},
        {"event": "closed", "actor": {"login": "actor"}, "commit_id": "abc1234"},
    ]
    assert checker._closed_by_timeline([{"event": "closed", "commit_id": "abc1234"}])[0] == "commit"
    assert checker._closed_by_timeline(timeline) == ("commit", "actor")


class FakeReader:
    def __init__(self, payload):
        self.payload = payload
        self.paginated_routes = []
        self.api_routes = []

    def try_api(self, route):
        self.api_routes.append(route)
        return self.payload.get(route)

    def paginated_api(self, route):
        self.paginated_routes.append(route)
        return self.payload.get(route, ([], None))


def test_default_branch_sha_uses_compare_status():
    reader = FakeReader({"repos/o/r/compare/main...abc1234": {"status": "behind"}})
    assert checker._on_default_branch(reader, "o/r", "main", "abc1234") is True
    reader = FakeReader({"repos/o/r/compare/main...abc1234": {"status": "ahead"}})
    assert checker._on_default_branch(reader, "o/r", "main", "abc1234") is False


def test_commit_closer_requires_merged_pull_request_on_default_branch():
    reader = FakeReader({
        "repos/o/r/commits/abc1234/pulls": [
            {"merged_at": "2026-01-01T00:00:00Z", "base": {"ref": "main"}},
        ],
    })
    assert checker._commit_closes_via_default_merged_pr(reader, "o/r", "abc1234", "main") is True
    reader = FakeReader({
        "repos/o/r/commits/abc1234/pulls": [
            {"merged_at": None, "base": {"ref": "main"}},
            {"merged_at": "2026-01-01T00:00:00Z", "base": {"ref": "feature"}},
        ],
    })
    assert checker._commit_closes_via_default_merged_pr(reader, "o/r", "abc1234", "main") is False


def test_paginated_search_fails_when_total_exceeds_items(monkeypatch, tmp_path):
    def fake_paginated(self, route):
        return ([{"number": 1}], 2)

    monkeypatch.setattr(checker.GitHubReader, "paginated_api", fake_paginated)
    with pytest.raises(RuntimeError, match="search returned 1 of 2 issues"):
        checker.collect_live("org/repo", tmp_path, closed_from="2026-01-01", closed_to="2026-01-02")


def test_paginated_search_decodes_concatenated_object_pages(monkeypatch, tmp_path):
    page1 = {"total_count": 101, "items": [{"number": number} for number in range(1, 101)]}
    page2 = {"total_count": 101, "items": [{"number": 101}]}

    def fake_run(argv, **kwargs):
        assert "--paginate" in argv
        return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(page1) + json.dumps(page2), stderr="")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    reader = checker.GitHubReader(tmp_path)
    items, total_count = reader.paginated_api("search/issues?q=repo%3Ao%2Fr%20is%3Aclosed&per_page=100")
    assert total_count == 101
    assert [item["number"] for item in items] == list(range(1, 102))


def test_review_record_uses_approved_reviews_only():
    reader = FakeReader({
        "repos/o/r/pulls/5/reviews?per_page=100": [
            {"state": "APPROVED", "commit_id": "abc1234567", "user": {"login": "reviewer"}},
            {"state": "CHANGES_REQUESTED", "commit_id": "bad9999999", "user": {"login": "reviewer"}},
        ],
    })
    assert checker._review_record({}, reader, "o/r", 5) == ("abc1234567", "reviewer")


def test_review_record_fallback_reads_conversation_comments():
    reader = FakeReader({
        "repos/o/r/pulls/5/reviews?per_page=100": [
            {"state": "CHANGES_REQUESTED", "commit_id": "bad9999999", "user": {"login": "reviewer"}},
        ],
        "repos/o/r/issues/5/comments?per_page=100": (
            [{"body": "reviewed head: abc1234", "user": {"login": "reviewer"}}],
            None,
        ),
    })
    assert checker._review_record({}, reader, "o/r", 5) == ("abc1234", "reviewer")
    assert reader.paginated_routes == ["repos/o/r/issues/5/comments?per_page=100"]


def test_review_head_accepts_seven_character_prefix_and_rejects_shorter():
    result = checker.evaluate_issue({
        "repository": "fixture",
        "number": 9203,
        "state_reason": "COMPLETED",
        "created_at": "2026-07-27T12:00:00Z",
        "closed_at": "2026-07-27T12:03:00Z",
        "closed_by": "actor",
        "closer_type": "merged_pr",
        "body": "",
        "comments": [{
            "closing_evidence": True,
            "body": "Merged PR #5 at abcdef1234. Path scripts/a.py. Tests: pytest - 1 passed.",
        }],
        "pull_requests": [{"number": 5, "merged": True, "head_sha": "abcdef123456", "review_head_sha": "abcdef1", "reviewer": "reviewer"}],
        "default_branch_shas": ["abcdef1234"],
        "paths_at_refs": {"scripts/a.py": True},
        "successor_states": {},
        "body_edited_after_close": False,
    })
    assert rule(result, 2)["verdict"] == "PASS"
    result = checker.evaluate_issue({
        "repository": "fixture",
        "number": 9204,
        "state_reason": "COMPLETED",
        "created_at": "2026-07-27T12:00:00Z",
        "closed_at": "2026-07-27T12:03:00Z",
        "closed_by": "actor",
        "closer_type": "merged_pr",
        "body": "",
        "comments": [{
            "closing_evidence": True,
            "body": "Merged PR #5 at abcdef1234. Path scripts/a.py. Tests: pytest - 1 passed.",
        }],
        "pull_requests": [{"number": 5, "merged": True, "head_sha": "abcdef123456", "review_head_sha": "abcdef", "reviewer": "reviewer"}],
        "default_branch_shas": ["abcdef1234"],
        "paths_at_refs": {"scripts/a.py": True},
        "successor_states": {},
        "body_edited_after_close": False,
    })
    assert rule(result, 2)["verdict"] == "FAIL"


@pytest.mark.parametrize("reviewed, merged, verdict", [
    ("ABCDEF1", "abcdef123456", "PASS"),
    ("abcdef1", "ABCDEF123456", "PASS"),
    ("ABCDEF123456", "abcdef123456", "PASS"),
    ("ABCDEF", "abcdef123456", "FAIL"),
    ("ABCDEF2", "abcdef123456", "FAIL"),
])
def test_review_head_case_does_not_change_prefix_validation(reviewed, merged, verdict):
    result = checker.check_review_head({"pull_requests": [{
        "merged": True, "reviewer": "reviewer",
        "review_head_sha": reviewed, "head_sha": merged,
    }]})
    assert result.verdict == verdict


def test_graphql_repository_argument_is_literal_and_read_only(monkeypatch, tmp_path):
    queries = []

    def graphql(self, query):
        queries.append(query)
        return {"data": {"repository": {"issue": {
            "lastEditedAt": None, "userContentEdits": {"nodes": []},
        }}}}

    monkeypatch.setattr(checker.GitHubReader, "graphql", graphql)
    reader = checker.GitHubReader(tmp_path)
    assert checker._body_edit_status({}, reader, "o/r", 5, "2026-01-01T00:00:00Z") is False
    assert 'repository(owner:"o", name:"r")' in queries[0]  # wording-allow: GitHub API field
    assert "mutation" not in queries[0].lower()
    source = (ROOT / "scripts/governance/check_issue_closures.py").read_text(encoding="utf-8")
    assert "repository(owner:" in source  # wording-allow: GitHub API field


def test_cli_help_accepts_general_repository_slugs(capsys):
    with pytest.raises(SystemExit) as exc:
        checker.main(["--help"])
    assert exc.value.code == 0
    assert "Repository slug NAME/REPO" in capsys.readouterr().out


def test_public_wording_is_neutral_for_checker_procedure_and_fixtures():
    paths = [
        ROOT / "docs/governance/issue-closing-procedure.md",
        ROOT / "scripts/governance/check_issue_closures.py",
        ROOT / "tests/governance/fixtures/issue-closure-cases.json",
    ]
    banned_terms = ("owner", "la" + "ne")
    banned = re.compile(r"\b(?:" + "|".join(banned_terms) + r")\b", re.I)
    offenders = []
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "wording-allow:" not in line and banned.search(line):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}:{number}")
    assert offenders == []


def test_reader_uses_get_pagination_and_read_only_graphql(monkeypatch, tmp_path):
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if "--paginate" in argv:
            return subprocess.CompletedProcess(argv, 0, stdout='[{"id":1}]\n', stderr="")
        return subprocess.CompletedProcess(argv, 0, stdout='{"ok":true}', stderr="")

    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    reader = checker.GitHubReader(tmp_path)
    reader.api("repos/o/r/issues/1")
    reader.paginated_api("repos/o/r/issues/1/comments?per_page=100")
    reader.graphql("query { viewer { login } }")
    rest_calls = [argv for argv in calls if argv[:3] == ["gh", "api", "--method"]]
    assert rest_calls
    assert all(argv[2:4] == ["--method", "GET"] for argv in rest_calls)
    assert all("GET" in argv for argv in rest_calls)
    assert all(flag not in argv for argv in rest_calls for flag in ("-f", "-F", "--input", "--field", "--raw-field", "-X"))
    graphql_calls = [argv for argv in calls if argv[:3] == ["gh", "api", "graphql"]]
    assert graphql_calls and "mutation" not in " ".join(" ".join(argv) for argv in graphql_calls).lower()
    assert all(flag not in argv for argv in graphql_calls for flag in ("-f", "-F", "--input"))


def test_default_cache_dir_is_temporary(monkeypatch, tmp_path):
    created = []

    def fake_mkdtemp(prefix):
        created.append(prefix)
        return str(tmp_path / "cache")

    monkeypatch.setattr(checker.tempfile, "mkdtemp", fake_mkdtemp)
    reader = checker.GitHubReader()
    assert created == ["closure-check-cache-"]
    assert reader.cache_dir.name == "cache"


def test_report_writers_emit_csv_markdown_and_auditor_agreement(tmp_path):
    items = issues()
    evaluations = [checker.evaluate_issue(item, items) for item in items[:5]]
    directory = tmp_path
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


def test_cli_fixture_mode_is_read_only(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("network or process call attempted")

    monkeypatch.setattr(checker.subprocess, "run", forbidden)
    directory = tmp_path
    try:
        csv_path = directory / "closures.csv"
        md_path = Path(directory) / "closures.md"
        code = checker.main(["--fixture", str(FIXTURE), "--csv", str(csv_path), "--markdown", str(md_path)])
        assert code == 1
        assert csv_path.exists()
        assert md_path.exists()
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_cli_accepts_auditor_csv(monkeypatch, tmp_path):
    monkeypatch.setattr(checker.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network or process call attempted")))
    directory = tmp_path
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


@pytest.mark.parametrize("reference, merged, state, on_default, verdict", [
    ("#7", False, "open", True, "FAIL"),
    ("#7", False, "closed", True, "FAIL"),
    ("PR #7", False, "open", True, "FAIL"),
    ("PR #7", False, "closed", True, "FAIL"),
    ("PR #7", True, "closed", False, "FAIL"),
    ("PR #7", True, "closed", True, "PASS"),
])
def test_rule_3_requires_merged_pr_on_default_branch(reference, merged, state, on_default, verdict):
    item = {
        "comments": [{"closing_evidence": True, "body": f"{reference}; scripts/a.py; pytest: 1 passed"}],
        "pull_requests": [{"number": 7, "merged": merged, "state": state, "merge_commit_sha": "abcdef1"}],
        "successor_states": {"7": {"state": state, "state_reason": "completed"}},
        "default_branch_shas": ["abcdef1"] if on_default else [],
        "paths_at_refs": {"scripts/a.py": True},
    }
    assert checker.check_evidence_reference(item).verdict == verdict


@pytest.mark.parametrize("reference, verdict", [
    ("#2026", "PASS"),
    ("PR #2026", "PASS"),
    ("PR 2026", "PASS"),
    ("pr 2026", "PASS"),
    ("pull request #2026", "PASS"),
    ("https://github.com/o/r/pull/2026", "PASS"),
    ("o/r#2026", "PASS"),
    ("(PR #2026)", "PASS"),
    ("Evidence: #2026.", "PASS"),
    ("Apr 2026", "FAIL"),
    ("Sept 2026", "FAIL"),
    ("January 2026", "FAIL"),
    ("v2026", "FAIL"),
    ("abc2026", "FAIL"),
    ("2026", "FAIL"),
    ("Apr 3", "FAIL"),
    ("expr 12", "FAIL"),
    ("xPR 2026", "FAIL"),
    ("_PR 2026", "FAIL"),
    ("word#2026", "FAIL"),
    ("#2026suffix", "FAIL"),
    ("PR 2026suffix", "FAIL"),
    ("PR #2026_suffix", "FAIL"),
    ("o/r#2026suffix", "FAIL"),
    ("https://github.com/o/r/pull/2026suffix", "FAIL"),
])
def test_rule_3_reference_markers_and_token_boundaries(reference, verdict):
    item = {
        "repository_slug": "o/r",
        "comments": [{"closing_evidence": True, "body": f"{reference}; scripts/a.py; 1 passed"}],
        "pull_requests": [
            {"number": number, "merged": True, "merge_commit_sha": "abcdef1"}
            for number in (3, 12, 2026)
        ],
        "default_branch_shas": ["abcdef1"],
        "paths_at_refs": {"scripts/a.py": True},
    }
    assert checker.check_evidence_reference(item).verdict == verdict


@pytest.mark.parametrize("reference, accepted", [
    ("PR #2026", True),
    ("PR 2026", True),
    ("pull request #2026", True),
    ("https://github.com/o/r/pull/2026", True),
    ("o/r#2026", True),
    ("Apr 2026", False),
    ("word#2026", False),
    ("PR #2026suffix", False),
])
def test_live_collection_uses_only_explicit_reference_tokens(monkeypatch, reference, accepted):
    reader = FakeReader({
        "repos/o/r/issues/1/comments?per_page=100": ([{
            "body": f"{reference}; scripts/a.py; 1 passed",
        }], None),
        "repos/o/r/issues/2026": {"number": 2026, "pull_request": {"url": "https://api.github.com/repos/o/r/pulls/2026"}},
        "repos/o/r/pulls/2026": {
            "merged_at": "2026-01-01T00:00:00Z", "merge_commit_sha": "abcdef1",
        },
        "repos/o/r/compare/main...abcdef1": {"status": "behind"},
        "repos/o/r/contents/scripts/a.py?ref=abcdef1": {"type": "file"},
    })
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    item = checker._neutral_issue({"number": 1}, reader, "o/r")
    assert ("repos/o/r/pulls/2026" in reader.api_routes) is accepted
    assert item["default_branch_shas"] == (["abcdef1"] if accepted else [])
    assert checker.check_evidence_reference(item).verdict == ("PASS" if accepted else "FAIL")


def test_reopened_successor_remains_unresolved(monkeypatch):
    fixture = json.loads((FIXTURE.parent / "issue-closure-references.json").read_text())
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    reader = FakeReader(fixture["reopened"]["responses"])
    assert fixture["reopened"]["timeline"][-1]["event"] == "reopened"
    item = checker._neutral_issue({
        "number": 1, "state_reason": "NOT_PLANNED",
        "body": "- [ ] Deferred work #7",
    }, reader, "o/r")
    assert item["successor_states"]["7"]["state_reason"] == "REOPENED"
    result = checker.evaluate_issue(item)
    assert all(rule(result, number)["verdict"] == "FAIL" for number in (5, 6, 7))


@pytest.mark.parametrize("reference", [
    "o/other#7",
    "https://github.com/o/other/pull/7",
    "https://api.github.com/repos/o/other/pulls/7",
])
def test_cross_repository_pr_is_read_in_its_repository(monkeypatch, reference):
    fixture = json.loads((FIXTURE.parent / "issue-closure-references.json").read_text())
    reader = FakeReader(fixture["cross_repository"]["responses"])
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    raw = {"number": 1, "body": reference, "closed_at": "2026-01-01T00:00:00Z"}
    result = checker._neutral_issue(raw, reader, "o/r")
    assert "repos/o/other/pulls/7" in reader.api_routes
    assert "repos/o/r/pulls/7" not in reader.api_routes
    assert result["pull_requests"] == []
    assert result["default_branch_shas"] == []
    assert result["foreign_pull_requests"][0]["repository"] == "o/other"
    assert result["foreign_pull_requests"][0]["merged"] is False


def test_cross_repository_timeline_pr_cannot_supply_local_evidence(monkeypatch):
    fixture = json.loads((FIXTURE.parent / "issue-closure-references.json").read_text())
    reader = FakeReader(fixture["cross_repository"]["responses"])
    reader.payload["repos/o/r/issues/1/timeline?per_page=100"] = ([{
        "event": "cross-referenced", "source": {"issue": {"pull_request": {
            "url": "https://api.github.com/repos/o/other/pulls/7",
        }}},
    }], None)
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    result = checker._neutral_issue({"number": 1, "body": "scripts/a.py"}, reader, "o/r")
    assert "repos/o/other/pulls/7" in reader.api_routes
    assert "repos/o/r/pulls/7" not in reader.api_routes
    assert result["pull_requests"] == []
    assert result["default_branch_shas"] == []
    assert checker.check_review_head(result).verdict == checker.NOT_EVALUATED
    assert checker.check_evidence_reference(result).verdict == "FAIL"


def test_qualified_successor_does_not_use_local_issue_number(monkeypatch):
    reader = FakeReader({
        "repos/o/r/issues/7": {"state": "open"},
        "repos/o/other/issues/7": {"state": "closed", "state_reason": "not_planned"},
    })
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    result = checker._neutral_issue({"number": 1, "body": "- [ ] Deferred work o/other#7"}, reader, "o/r")
    assert "repos/o/other/issues/7" in reader.api_routes
    assert "repos/o/r/issues/7" not in reader.api_routes
    assert checker.check_body_checkboxes(result).verdict == "FAIL"
    assert checker.check_hedges(result).verdict == "FAIL"


def test_final_closure_does_not_inherit_commit_before_reopening(monkeypatch):
    timeline = [
        {"event": "closed", "commit_id": "abcdef1"},
        {"event": "reopened"},
        {"event": "closed", "actor": {"login": "actor"}},
    ]
    assert checker._closed_by_timeline(timeline) == ("comment", "actor")
    reader = FakeReader({
        "repos/o/r/issues/1/events?per_page=100": (timeline, None),
        "repos/o/r/issues/1/timeline?per_page=100": (timeline, None),
    })
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    assert checker._neutral_issue({"number": 1}, reader, "o/r")["closer_type"] == "comment"


@pytest.mark.parametrize("text", [
    "nested/src/a.py", "https://example.invalid/src/a.py", "other/tests/a.py",
])
def test_path_matching_does_not_extract_nested_or_url_tails(text):
    assert checker.PATH_REF.findall(text) == []


def test_bulk_window_is_ten_minutes_including_current_closure():
    item = {"closed_by": "actor", "closed_at": "2026-01-01T12:10:00Z"}
    peers = [dict(item, closed_at=f"2026-01-01T12:{minute:02d}:00Z") for minute in (1, 3, 5, 12, 14)]
    assert checker.check_bulk(item, peers + [item]).verdict == "PASS"
    peers = [dict(item, closed_at=f"2026-01-01T12:{minute:02d}:00Z") for minute in (0, 1, 2, 3, 4)]
    assert checker.check_bulk(item, peers + [item]).verdict == "FAIL"
    # Every issue in the qualifying interval gets the same bulk finding.
    assert all(checker.check_bulk(peer, peers + [item]).verdict == "FAIL" for peer in peers)


def test_auditor_agreement_only_counts_issues_with_auditor_rows(tmp_path):
    evaluations = [{"repository": "fixture", "number": number, "verdict": "PASS"} for number in (1, 2)]
    target = tmp_path / "report.md"
    checker.write_markdown(target, evaluations, {1: "DONE"})
    assert "Auditor agreement: 1/1 (100.0%)" in target.read_text()


@pytest.mark.parametrize("reference", ["o/r#7", "https://github.com/o/r/pull/7"])
def test_rule_3_accepts_qualified_local_merged_pr(reference):
    item = {
        "repository_slug": "o/r",
        "comments": [{"closing_evidence": True, "body": f"{reference}; scripts/a.py; pytest: 1 passed"}],
        "pull_requests": [{"number": 7, "merged": True, "merge_commit_sha": "abcdef1"}],
        "default_branch_shas": ["abcdef1"],
        "paths_at_refs": {"scripts/a.py": True},
    }
    assert checker.check_evidence_reference(item).verdict == "PASS"


@pytest.mark.parametrize("verified", [False, True])
def test_rule_3_completed_issue_needs_its_own_evidence(monkeypatch, verified):
    reader = FakeReader({
        "repos/o/r/issues/1/comments?per_page=100": ([{"body": "#7; scripts/a.py; pytest: 1 passed"}], None),
        "repos/o/r/issues/7": {"number": 7, "state": "closed", "state_reason": "completed"},
        "repos/o/r/issues/7/comments?per_page=100": ([{"body": "abcdef1; scripts/a.py; pytest: 1 passed"}], None),
        "repos/o/r/compare/main...abcdef1": {"status": "behind" if verified else "ahead"},
        "repos/o/r/contents/scripts/a.py?ref=abcdef1": {"type": "file"},
    })
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    result = checker._neutral_issue({"number": 1}, reader, "o/r")
    assert checker.check_evidence_reference(result).verdict == ("PASS" if verified else "FAIL")


def test_unmerged_pr_cannot_impersonate_completed_issue_evidence():
    own_evidence = {
        "comments": [{"closing_evidence": True, "body": "abcdef1; scripts/a.py; pytest: 1 passed"}],
        "default_branch_shas": ["abcdef1"], "paths_at_refs": {"scripts/a.py": True},
    }
    item = {
        "comments": [{"closing_evidence": True, "body": "#7; scripts/a.py; pytest: 1 passed"}],
        "successor_states": {"7": {"state": "closed", "state_reason": "completed", "is_pull_request": True, "evidence": own_evidence}},
        "paths_at_refs": {"scripts/a.py": True},
    }
    assert checker.check_evidence_reference(item).verdict == "FAIL"


def test_unmerged_live_pr_cannot_supply_default_branch_sha(monkeypatch):
    reader = FakeReader({
        "repos/o/r/issues/1/comments?per_page=100": ([{"body": "PR #7; scripts/a.py; pytest: 1 passed"}], None),
        "repos/o/r/pulls/7": {"merged_at": None, "merge_commit_sha": "abcdef1"},
        "repos/o/r/compare/main...abcdef1": {"status": "behind"},
        "repos/o/r/contents/scripts/a.py?ref=abcdef1": {"type": "file"},
    })
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    result = checker._neutral_issue({"number": 1}, reader, "o/r")
    assert result["default_branch_shas"] == []
    assert checker.check_evidence_reference(result).verdict == "FAIL"


def test_completed_issue_reference_cycle_is_bounded(monkeypatch):
    raw = {"number": 1, "state": "closed", "state_reason": "completed", "body": "#1; scripts/a.py"}
    reader = FakeReader({"repos/o/r/issues/1": raw})
    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: False)
    result = checker._neutral_issue(raw, reader, "o/r")
    assert reader.api_routes.count("repos/o/r/issues/1") == 2
    assert checker.check_evidence_reference(result).verdict == "FAIL"
