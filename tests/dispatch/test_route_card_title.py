#!/usr/bin/env python3
"""TDD tests for card titles surviving the live-GitHub routing input (#3763).

Every card in every regenerated queue file carried `title: ''` — 1341 of 1341
on dev-primary. The cards were otherwise correct; only the title was gone.

The cause is a reuse mismatch, not broken code. `fetch_issues_for_coverage`
requests `--json number,labels`, which is exactly right for coverage reporting
— its namesake purpose. #3736 then reused it as the ROUTING input, and routing
additionally needs the title. `issue_to_card` does `issue.get("title") or ""`,
which is correct given an input that never carries one.

So the assertion that matters is not "does issue_to_card handle a title" (it
always did) but "does a title put on the wire by gh reach the card". That is a
property of the PIPELINE, and it is what nothing asserted.

Per feedback_tests_that_pin_a_name_not_a_property: the primary test below fails
if the title is dropped ANYWHERE between gh and the card, rather than pinning
the literal field list of the gh invocation. The field-list test is kept as a
cheaper, more localised signal, but it is the secondary one deliberately — it
would keep passing if a later refactor requested `title` and then discarded it.

Hermetic: gh is stubbed; no network.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/test_route_card_title.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"

ISSUE_TITLE = "Deckhand: wire + harden rate-limit / abuse controls"


def _load():
    spec = importlib.util.spec_from_file_location("route", ROUTE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["route"] = mod
    spec.loader.exec_module(mod)
    return mod


class _CompletedProcess:
    """Stand-in for subprocess.CompletedProcess with only what the code reads."""

    def __init__(self, stdout: str, returncode: int = 0):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


@pytest.fixture
def route():
    return _load()


@pytest.fixture
def gh_payload():
    """What `gh issue list --json ...` would emit for one titled, labelled issue."""
    return json.dumps(
        [
            {
                "number": 4,
                "title": ISSUE_TITLE,
                "labels": [{"name": "priority:high"}, {"name": "domain:routing"}],
            }
        ]
    )


def _stub_gh(monkeypatch, route, payload, captured):
    def fake_run(argv, *a, **kw):
        captured.append(argv)
        return _CompletedProcess(payload)

    monkeypatch.setattr(route.subprocess, "run", fake_run)


def test_title_survives_the_fetch_to_card_pipeline(monkeypatch, route, gh_payload):
    """THE test. A title on the wire must reach the card.

    Fails on main: the fetch drops every field except number and labels, so the
    card's title is "" no matter what gh returned.
    """
    _stub_gh(monkeypatch, route, gh_payload, [])

    issues = route.fetch_issues_for_coverage("vamseeachanta/deckhand")
    assert issues, "fetch returned nothing — stub not wired"

    card = route.issue_to_card(issues[0], "vamseeachanta/deckhand")

    assert card["title"] == ISSUE_TITLE, (
        f"card title is {card['title']!r}; the title gh returned was dropped "
        "between the fetch and the card. This is what put `title: ''` on all "
        "1341 dev-primary queue cards."
    )


def test_fetch_requests_the_title_field(monkeypatch, route, gh_payload):
    """Secondary, localised signal: the gh query must ask for the title.

    Weaker than the pipeline test on purpose — it pins the request, not the
    outcome, and would survive a refactor that asked for the title and then
    threw it away.
    """
    captured: list[list[str]] = []
    _stub_gh(monkeypatch, route, gh_payload, captured)

    route.fetch_issues_for_coverage("vamseeachanta/deckhand")

    assert captured, "gh was never invoked"
    argv = captured[0]
    assert "--json" in argv, f"no --json in gh invocation: {argv}"
    fields = argv[argv.index("--json") + 1].split(",")
    assert "title" in fields, (
        f"gh --json field list is {fields}; routing needs the title and the "
        "coverage reporter's two-field list does not provide it."
    )


def test_labels_and_number_still_survive(monkeypatch, route, gh_payload):
    """Regression guard: adding the title must not disturb what already worked.

    Coverage reporting is the original caller and depends on exactly these two.
    """
    _stub_gh(monkeypatch, route, gh_payload, [])

    issues = route.fetch_issues_for_coverage("vamseeachanta/deckhand")
    card = route.issue_to_card(issues[0], "vamseeachanta/deckhand")

    assert issues[0]["number"] == 4
    assert issues[0]["labels"] == ["priority:high", "domain:routing"]
    assert card["priority"] == 3, "priority:high must still resolve to 3"
    assert "domain:routing" in card["gh_labels"]


def test_missing_title_still_yields_empty_string(monkeypatch, route):
    """An issue with no title must not crash the pass.

    A single malformed card must not take down a 1,700-issue run — the same
    fail-closed-per-card posture propose() already takes for contradictory axes.
    """
    payload = json.dumps([{"number": 9, "labels": []}])
    _stub_gh(monkeypatch, route, payload, [])

    issues = route.fetch_issues_for_coverage("vamseeachanta/deckhand")
    card = route.issue_to_card(issues[0], "vamseeachanta/deckhand")

    assert card["title"] == ""
