#!/usr/bin/env python3
"""Coordinator dispatch loop contracts for rewire L3 (#4000).

Hermetic: fake gh, fake host state, no network, no runners.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOP = REPO_ROOT / "scripts" / "dispatch" / "coordinator_loop.py"
ROUTING = REPO_ROOT / "config" / "agents" / "host-role-routing.yaml"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def _load():
    spec = importlib.util.spec_from_file_location("coordinator_loop", LOOP)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["coordinator_loop"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()


class FakeGh:
    def __init__(self, issues):
        self.issues = {item["number"]: dict(item) for item in issues}
        self.edits = []
        self.comments = []

    def list_issues(self, label):
        return [
            dict(item)
            for item in self.issues.values()
            if label in item.get("labels", []) and item.get("state", "OPEN") == "OPEN"
        ]

    def issue_comments(self, number):
        return list(self.issues[number].get("comments", []))

    def relabel(self, number, *, remove=(), add=()):
        self.edits.append((number, tuple(remove), tuple(add)))
        labels = set(self.issues[number].setdefault("labels", []))
        labels.difference_update(remove)
        labels.update(add)
        self.issues[number]["labels"] = sorted(labels)

    def comment(self, number, body):
        self.comments.append((number, body))
        self.issues[number].setdefault("comments", []).append(
            {"createdAt": "2026-10-09T00:00:00Z", "body": body}
        )


class FakeRunner:
    def __init__(self):
        self.calls = []

    def start(self, plan):
        self.calls.append(dict(plan))


def routing():
    return C.load_routing(ROUTING)


def issue(number, labels, created="2026-10-07T00:00:00Z", comments=None):
    return {
        "number": number,
        "title": f"issue {number}",
        "url": f"https://github.com/vamseeachanta/workspace-hub/issues/{number}",
        "state": "OPEN",
        "createdAt": created,
        "updatedAt": created,
        "labels": labels,
        "comments": comments or [],
    }


def test_dry_run_selects_ready_issue_and_routes_codex_to_linux_without_claiming():
    gh = FakeGh([issue(11, ["dispatch:ready", "lane:codex"])])
    runner = FakeRunner()

    result = C.run_once(
        gh=gh,
        runner=runner,
        routing=routing(),
        current_host="ace-win-2",
        host_state={},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"][0]["issue"] == 11
    assert result["started"][0]["provider"] == "codex"
    assert result["started"][0]["host"] == "dev-primary"
    assert result["dry_run"] is True
    assert gh.edits == []
    assert runner.calls == []


def test_apply_claims_ready_issue_before_starting_runner():
    gh = FakeGh([issue(12, ["dispatch:ready", "lane:claude"])])
    runner = FakeRunner()

    C.run_once(
        gh=gh,
        runner=runner,
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-win-2": {"active_lanes": 0}},
        apply=True,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert gh.edits == [(12, ("dispatch:ready",), ("dispatch:active",))]
    assert runner.calls and runner.calls[0]["issue"] == 12
    assert gh.issues[12]["labels"].count("dispatch:active") == 1
    assert "dispatch:ready" not in gh.issues[12]["labels"]


def test_third_local_lane_on_coordinator_host_is_refused_and_routed_to_linux():
    gh = FakeGh([issue(13, ["dispatch:ready", "lane:claude", "machine:ace-win-2"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-win-2": {"active_lanes": 2}, "dev-primary": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    plan = result["started"][0]
    assert plan["host"] == "dev-primary"
    assert plan["refused_host"] == "ace-win-2"
    assert "local lane cap" in plan["route_reason"]


def test_requested_local_codex_lane_reports_refusal_before_linux_route():
    gh = FakeGh([issue(17, ["dispatch:ready", "lane:codex", "machine:ace-win-2"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-win-2": {"active_lanes": 2}, "dev-primary": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    plan = result["started"][0]
    assert plan["host"] == "dev-primary"
    assert plan["refused_host"] == "ace-win-2"
    assert "local lane cap" in plan["route_reason"]


def test_decision_labeled_ready_issue_is_not_dispatched():
    gh = FakeGh([issue(14, ["dispatch:ready", "lane:codex", "decision:ecosystem"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"] == []
    assert result["skipped"][0]["reason"] == "decision-label"


def test_stalled_active_issue_without_comments_is_returned_to_ready_with_comment():
    gh = FakeGh([issue(15, ["dispatch:active", "lane:codex"], created="2026-10-06T00:00:00Z")])

    result = C.handle_stalls(
        gh=gh,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
        apply=True,
        stall_hours=48,
    )

    assert result["stalled"][0]["target"] == "dispatch:ready"
    assert gh.edits == [(15, ("dispatch:active",), ("dispatch:ready",))]
    assert gh.comments and "stalled dispatch:active" in gh.comments[0][1]


def test_stalled_active_issue_with_blocker_signal_is_blocked():
    gh = FakeGh([
        issue(
            16,
            ["dispatch:active", "lane:claude", "decision:ecosystem"],
            created="2026-10-06T00:00:00Z",
        )
    ])

    result = C.handle_stalls(
        gh=gh,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
        apply=True,
        stall_hours=48,
    )

    assert result["stalled"][0]["target"] == "dispatch:blocked"
    assert gh.edits == [(16, ("dispatch:active",), ("dispatch:blocked",))]


def test_dispatch_loop_is_registered_but_not_installed_as_a_schedule():
    tasks = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))["tasks"]
    task = next(item for item in tasks if item["id"] == "coordinator-dispatch-loop")

    assert task["install"] == "manual-registration-only"
    assert task["machines"] == ["dev-primary", "ace-linux-1"]
    assert "scripts/dispatch/coordinator_loop.py" in task["command"]
