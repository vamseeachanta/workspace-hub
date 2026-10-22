"""Independent request arithmetic and procedure E.4 regression cases.

The API ceiling is specified in issue 4073, plan item 3. Small budgets below
are synthetic inputs: two response pages require two requests, and a third
page cannot be read with a budget of two. Procedure E.4 requires both a
command and a count; a count alone therefore fails without running a tool.
"""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/governance"))
checker = importlib.import_module("check_issue_closures")


def response(body, next_route=None):
    headers = "HTTP/2.0 200 OK\nContent-Type: application/json\n"
    if next_route:
        headers += f'Link: <https://api.github.com/{next_route}>; rel="next"\n'
    return headers + "\n" + json.dumps(body)


def test_pagination_counts_each_page_and_reuses_complete_cache(monkeypatch, tmp_path):
    """Two pages cost 1 + 1 = 2; replay of saved pages costs zero requests."""
    calls = []
    route = "repos/example/tools/issues?per_page=100"
    next_route = route + "&page=2"
    pages = {route: response([{"number": 1}], next_route),
             next_route: response([{"number": 2}])}

    def run(argv, **kwargs):
        calls.append(argv)
        assert "--paginate" not in argv
        assert "--include" in argv
        return subprocess.CompletedProcess(argv, 0, pages[argv[-1]], "")

    monkeypatch.setattr(checker.subprocess, "run", run)
    reader = checker.GitHubReader(tmp_path, budget=2)
    assert reader.paginated_api(route) == ([{"number": 1}, {"number": 2}], None)
    assert reader.calls == len(calls) == 2
    assert checker.GitHubReader(tmp_path, budget=0).paginated_api(route)[0] == [
        {"number": 1}, {"number": 2},
    ]
    assert len(calls) == 2


def test_budget_exhaustion_is_not_swallowed_or_cached_as_complete(monkeypatch, tmp_path):
    """With one request available, the second page must remain unevaluated."""
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, response([], "repos/example/tools/issues?page=2"), "")

    monkeypatch.setattr(checker.subprocess, "run", run)
    reader = checker.GitHubReader(tmp_path, budget=1)
    with pytest.raises(checker.ApiBudgetExceeded):
        reader.paginated_api("repos/example/tools/issues")
    with pytest.raises(checker.ApiBudgetExceeded):
        reader.try_api("repos/example/tools")
    assert len(calls) == 1


def test_cache_keys_are_bounded_and_do_not_alias_punctuation(tmp_path):
    """Different queries retain different identity; query length is not a filename."""
    reader = checker.GitHubReader(tmp_path)
    assert reader._cache_path("a/b") != reader._cache_path("a_b")
    query = "query { " + "field " * 100 + "}"
    target = reader._cache_path(query)
    assert target.parent == tmp_path
    target.write_text("{}")
    assert target.read_text() == "{}"


def test_search_incomplete_results_cannot_be_reported_as_complete(monkeypatch, tmp_path):
    monkeypatch.setattr(checker.subprocess, "run", lambda argv, **kwargs:
                        subprocess.CompletedProcess(argv, 0, response({
                            "total_count": 0, "incomplete_results": True, "items": [],
                        }), ""))
    with pytest.raises(RuntimeError, match="incomplete"):
        checker.GitHubReader(tmp_path).paginated_api("search/issues?q=example")


@pytest.mark.parametrize("budget", [-1, 501])
def test_reader_cannot_raise_hard_ceiling(tmp_path, budget):
    """Issue 4073 item 3 caps every run at 500 calls, including custom budgets."""
    with pytest.raises(ValueError):
        checker.GitHubReader(tmp_path, budget=budget)


@pytest.mark.parametrize("evidence, verdict", [
    ("3 passed", "FAIL"),
    ("No command is recorded; 3 tests", "FAIL"),
    ("pytest tests/unit -q: 3 passed", "PASS"),
    ("python -m unittest: 3 tests", "PASS"),
    ("ctest --output-on-failure: 3 passed", "PASS"),
    ("Command: custom-builder --check; 3 passed", "PASS"),
])
def test_rule_four_requires_command_and_count(evidence, verdict):
    item = {"comments": [{"closing_evidence": True, "body": evidence}]}
    assert checker.check_test_count(item).verdict == verdict


def test_documented_example_has_independently_derived_rule_four_answers():
    """Procedure E.4: count only fails; labelled command plus count passes.

    Both overall outcomes fail because neither input supplies a resolving
    revision or existing path (procedure E.3), independent of rule 4.
    """
    root = Path(__file__).resolve().parents[2]
    items = checker.load_fixture(root / "docs/governance/examples/closure-command-evidence.json")
    assert [checker.check_test_count(item).verdict for item in items] == ["FAIL", "PASS"]
    assert [checker.evaluate_issue(item)["verdict"] for item in items] == ["FAIL", "FAIL"]


def test_graphql_budget_exhaustion_is_not_body_edit_absence(tmp_path):
    reader = checker.GitHubReader(tmp_path, budget=0)
    with pytest.raises(checker.ApiBudgetExceeded):
        checker._body_edit_status({}, reader, "example/tools", 1, "2026-01-01T00:00:00Z")


@pytest.mark.parametrize("link", [
    'Link: <https://example.invalid/page>; rel="next"',
    'Link: <http://api.github.com/page>; rel="next"',
])
def test_pagination_rejects_untrusted_next_origin(link):
    with pytest.raises(RuntimeError, match="untrusted"):
        checker.GitHubReader._next_page(link)


def test_body_only_reference_reads_state_without_expanding_delivery_evidence(monkeypatch):
    """E.3 reads closing evidence; E.5 still needs body successor state.

    A body-only reference therefore needs one state lookup, not recursive
    comments, timeline and revision lookups for the referenced issue.
    """
    class Reader:
        def __init__(self):
            self.pages = []

        def paginated_api(self, route):
            self.pages.append(route)
            return [], None

        def try_api(self, route):
            if route == "repos/example/tools/issues/2":
                return {"number": 2, "state": "closed", "state_reason": "completed"}
            return None

    monkeypatch.setattr(checker, "_body_edit_status", lambda *args: None)
    reader = Reader()
    item = checker._neutral_issue({"number": 1, "body": "- [ ] Remaining #2"}, reader, "example/tools")
    assert item["successor_states"]["2"]["state"] == "closed"
    assert "evidence" not in item["successor_states"]["2"]
    assert not any("/issues/2/" in route for route in reader.pages)


def test_repeated_pagination_page_cannot_create_partial_cache(monkeypatch, tmp_path):
    route = "repos/example/tools/issues"
    monkeypatch.setattr(checker.subprocess, "run", lambda argv, **kwargs:
                        subprocess.CompletedProcess(argv, 0, response([{"number": 1}], route), ""))
    reader = checker.GitHubReader(tmp_path)
    with pytest.raises(RuntimeError, match="repeated"):
        reader.paginated_api(route)
    assert reader.calls == 1
    assert not reader._cache_path(f"paginate/{route}").exists()
