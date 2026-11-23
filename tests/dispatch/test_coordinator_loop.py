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
    def __init__(self, fail=False, fail_issues=None):
        self.calls = []
        self.fail = fail
        self.fail_issues = set(fail_issues or [])

    def start(self, plan):
        if self.fail or plan["issue"] in self.fail_issues:
            raise RuntimeError("runner exploded")
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
        host_state={"ace-linux-1": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"][0]["issue"] == 11
    assert result["started"][0]["provider"] == "codex"
    assert result["started"][0]["host"] == "ace-linux-1"
    assert result["dry_run"] is True
    assert gh.edits == []
    assert runner.calls == []


def test_default_run_dispatch_limit_is_one_and_counts_planned_lanes():
    gh = FakeGh([
        issue(101, ["dispatch:ready", "lane:codex"]),
        issue(102, ["dispatch:ready", "lane:codex"]),
    ])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-linux-1": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert [item["issue"] for item in result["started"]] == [101]
    assert result["skipped"] == [{"issue": 102, "reason": "max-dispatches-per-run"}]


def test_all_hosts_full_defers_instead_of_returning_capped_host():
    gh = FakeGh([issue(103, ["dispatch:ready", "lane:codex"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={
            "ace-win-2": {"active_lanes": 2},
            "ace-linux-1": {"active_lanes": 6},
            "ace-linux-2": {"active_lanes": 4},
        },
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"] == []
    assert result["skipped"] == [{"issue": 103, "reason": "all-hosts-at-cap"}]


def test_missing_host_state_is_derived_from_active_dispatch_items():
    gh = FakeGh([
        issue(104, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(105, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(106, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(107, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(108, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(109, ["dispatch:active", "lane:codex", "machine:ace-linux-1"]),
        issue(110, ["dispatch:ready", "lane:codex"]),
    ])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state=None,
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"][0]["host"] == "ace-linux-2"


def test_missing_host_state_with_unlocated_active_item_treats_provider_hosts_as_full():
    gh = FakeGh([
        issue(113, ["dispatch:active", "lane:codex"]),
        issue(114, ["dispatch:ready", "lane:codex"]),
    ])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state=None,
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"] == []
    assert result["skipped"] == [{"issue": 114, "reason": "all-hosts-at-cap"}]


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


def test_runner_failure_returns_issue_to_ready_with_comment_and_continues():
    gh = FakeGh([
        issue(111, ["dispatch:ready", "lane:codex"]),
        issue(112, ["dispatch:ready", "lane:codex"]),
    ])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(fail=True),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-linux-1": {"active_lanes": 0}},
        apply=True,
        max_dispatches_per_run=2,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"] == []
    assert [item["issue"] for item in result["runner_failed"]] == [111, 112]
    assert all("dispatch:ready" in gh.issues[number]["labels"] for number in (111, 112))
    assert all("dispatch:active" not in gh.issues[number]["labels"] for number in (111, 112))
    assert len(gh.comments) == 2
    assert "runner failed" in gh.comments[0][1]


def test_runner_failure_does_not_spend_successful_dispatch_budget():
    gh = FakeGh([
        issue(115, ["dispatch:ready", "lane:codex"]),
        issue(116, ["dispatch:ready", "lane:codex"]),
    ])
    runner = FakeRunner(fail_issues={115})

    result = C.run_once(
        gh=gh,
        runner=runner,
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-linux-1": {"active_lanes": 0}},
        apply=True,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert [item["issue"] for item in result["runner_failed"]] == [115]
    assert [item["issue"] for item in result["started"]] == [116]
    assert "dispatch:ready" in gh.issues[115]["labels"]
    assert "dispatch:active" in gh.issues[116]["labels"]


def test_third_local_lane_on_coordinator_host_is_refused_and_routed_to_linux():
    gh = FakeGh([issue(13, ["dispatch:ready", "lane:claude", "machine:ace-win-2"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-win-2": {"active_lanes": 2}, "ace-linux-1": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    plan = result["started"][0]
    assert plan["host"] == "ace-linux-1"
    assert plan["refused_host"] == "ace-win-2"
    assert "local lane cap" in plan["route_reason"]


def test_requested_local_codex_lane_reports_refusal_before_linux_route():
    gh = FakeGh([issue(17, ["dispatch:ready", "lane:codex", "machine:ace-win-2"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-win-2": {"active_lanes": 2}, "ace-linux-1": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    plan = result["started"][0]
    assert plan["host"] == "ace-linux-1"
    assert plan["refused_host"] == "ace-win-2"
    assert "local lane cap" in plan["route_reason"]


def test_decision_labeled_ready_issue_is_not_dispatched():
    gh = FakeGh([issue(14, ["dispatch:ready", "lane:codex", "decision:ecosystem"])])

    result = C.run_once(
        gh=gh,
        runner=FakeRunner(),
        routing=routing(),
        current_host="ace-win-2",
        host_state={"ace-linux-1": {"active_lanes": 0}},
        apply=False,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
    )

    assert result["started"] == []
    assert result["skipped"][0]["reason"] == "decision-label"


def test_stalled_active_issue_without_comments_is_blocked_with_decision_label():
    gh = FakeGh([issue(15, ["dispatch:active", "lane:codex"], created="2026-10-06T00:00:00Z")])

    result = C.handle_stalls(
        gh=gh,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
        apply=True,
        stall_hours=48,
    )

    assert result["stalled"][0]["target"] == "dispatch:blocked"
    assert gh.edits == [(15, ("dispatch:active",), ("dispatch:blocked", "decision:ecosystem"))]
    assert gh.comments and "stalled dispatch:active" in gh.comments[0][1]


def test_stalled_active_issue_age_is_measured_from_latest_comment():
    gh = FakeGh([
        issue(
            16,
            ["dispatch:active", "lane:claude"],
            created="2026-10-01T00:00:00Z",
            comments=[{"createdAt": "2026-10-08T23:00:00Z", "body": "still running"}],
        )
    ])

    result = C.handle_stalls(
        gh=gh,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
        apply=True,
        stall_hours=48,
    )

    assert result["stalled"] == []
    assert gh.edits == []


def test_stalled_active_issue_with_stale_comment_is_blocked():
    gh = FakeGh([
        issue(
            17,
            ["dispatch:active", "lane:claude", "decision:ecosystem"],
            created="2026-10-06T00:00:00Z",
            comments=[{"createdAt": "2026-10-06T00:30:00Z", "body": "started"}],
        )
    ])

    result = C.handle_stalls(
        gh=gh,
        now=datetime(2026, 10, 9, tzinfo=timezone.utc),
        apply=True,
        stall_hours=48,
    )

    assert result["stalled"][0]["target"] == "dispatch:blocked"
    assert gh.edits == [(17, ("dispatch:active",), ("dispatch:blocked", "decision:ecosystem"))]


def test_dispatch_loop_is_registered_but_not_installed_as_a_schedule():
    tasks = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))["tasks"]
    task = next(item for item in tasks if item["id"] == "coordinator-dispatch-loop")

    assert task["install"] == "manual-registration-only"
    assert task["schedule"] == "0 0 31 2 *"
    assert task["machines"] == ["ace-linux-1"]
    assert "scripts/dispatch/coordinator_loop.py" in task["command"]
