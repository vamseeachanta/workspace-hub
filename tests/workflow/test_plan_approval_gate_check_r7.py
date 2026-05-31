"""R7 regression tests for the #2817 plan-approval gate."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import plan_approval_gate_check as gate  # noqa: E402
import plan_approval_gate_io as gate_io  # noqa: E402


OWNER = "vamseeachanta"
PLAN = "docs/plans/2026-05-30-issue-2817-plan-approval-label-authority.md"
SHA = "2f3d873d48acd05336268ac679f47b5b2708a567"
HEAD = "9" * 40
BASE = "7" * 40


def _t(hour: int) -> dt.datetime:
    return dt.datetime(2026, 5, 30, hour, 0, tzinfo=dt.timezone.utc)


def _binding() -> gate.PlanBinding:
    return gate.PlanBinding(PLAN, SHA, OWNER, "User", _t(10))


def _approval(**kw) -> gate.IssueApproval:
    base = dict(
        issue_number=2817,
        label_actor=OWNER,
        label_actor_type="User",
        label_applied_at=_t(12),
        plan_binding=_binding(),
        plan_revision_time=_t(11),
    )
    base.update(kw)
    return gate.IssueApproval(**base)


def test_current_label_state_is_required():
    decision = gate.evaluate_plan_approval(
        gate.PrContext("feat/2817-plan-approval-gate", OWNER, {PLAN}, HEAD),
        {2817: _approval(label_current=False)},
        {OWNER},
    )
    assert decision.allowed is False
    assert "currently" in decision.reason.lower()


def test_revision_must_be_reachable_from_pr_head():
    decision = gate.evaluate_plan_approval(
        gate.PrContext("feat/2817-plan-approval-gate", OWNER, {PLAN}, HEAD),
        {2817: _approval(plan_revision_in_head=False)},
        {OWNER},
    )
    assert decision.allowed is False
    assert "head history" in decision.reason.lower()


def test_revision_must_not_already_be_in_pr_base():
    decision = gate.evaluate_plan_approval(
        gate.PrContext("feat/2817-plan-approval-gate", OWNER, {PLAN}, HEAD, BASE),
        {2817: _approval(plan_revision_in_base=True)},
        {OWNER},
    )
    assert decision.allowed is False
    assert "base history" in decision.reason.lower()


def test_revision_reaches_head_uses_compare_status(monkeypatch):
    def fake_gh_json(*args):
        assert args[:2] == ("api", f"repos/vamseeachanta/workspace-hub/compare/{SHA}...{HEAD}")
        return {"status": "ahead"}

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    assert gate.revision_reaches_head("vamseeachanta/workspace-hub", SHA, HEAD) is True

    monkeypatch.setattr(gate_io, "gh_json", lambda *args: {"status": "diverged"})
    assert gate.revision_reaches_head("vamseeachanta/workspace-hub", SHA, HEAD) is False


def test_issue_body_binding_uses_body_edit_time_not_issue_update(monkeypatch):
    def fake_gh_json(*args):
        if args[:2] == ("api", "graphql"):
            return {
                "data": {
                    "repository": {
                        "issue": {
                            "author": {"login": OWNER},
                            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`",
                            "createdAt": "2026-05-30T10:00:00Z",
                            "lastEditedAt": "2026-05-30T11:00:00Z",
                        }
                    }
                }
            }
        if args[:2] == ("api", "repos/vamseeachanta/workspace-hub/issues/2817/comments"):
            return []
        raise AssertionError(args)

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    sources = gate.load_issue_binding_sources("vamseeachanta/workspace-hub", 2817)
    assert sources[0]["updatedAt"] == "2026-05-30T11:00:00Z"


def test_binding_sources_support_pull_request_body(monkeypatch):
    def fake_gh_json(*args):
        if args[:2] == ("api", "graphql"):
            return {
                "data": {
                    "repository": {
                        "issue": None,
                        "pullRequest": {
                            "author": {"login": OWNER},
                            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`",
                            "createdAt": "2026-05-30T10:00:00Z",
                            "lastEditedAt": "2026-05-30T11:00:00Z",
                        },
                    }
                }
            }
        if args[:2] == ("api", "repos/vamseeachanta/workspace-hub/issues/2817/comments"):
            return []
        raise AssertionError(args)

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    sources = gate.load_issue_binding_sources("vamseeachanta/workspace-hub", 2817)
    assert sources[0]["author"]["login"] == OWNER


def test_current_labels_are_loaded_by_name(monkeypatch):
    monkeypatch.setattr(
        gate_io,
        "gh_json",
        lambda *args: {"labels": [{"name": gate.PLAN_APPROVED_LABEL}, {"name": "other"}]},
    )
    assert gate.load_current_issue_labels("vamseeachanta/workspace-hub", 2817) == {
        gate.PLAN_APPROVED_LABEL,
        "other",
    }


def test_normalize_path_keeps_dot_prefixed_repo_paths():
    assert gate._normalize_path(".github/workflows/main.yml") == ".github/workflows/main.yml"
    assert gate._normalize_path("./docs/plans/issue.md") == "docs/plans/issue.md"


def test_load_pr_context_reads_head_and_base(monkeypatch):
    def fake_gh_json(*args):
        assert args[:5] == ("pr", "view", "2881", "--repo", "vamseeachanta/workspace-hub")
        return {
            "headRefName": "feat/2817-plan-approval-gate",
            "headRefOid": HEAD,
            "baseRefOid": BASE,
            "author": {"login": OWNER},
        }

    monkeypatch.setattr(gate, "gh_json", fake_gh_json)
    monkeypatch.setattr(gate, "load_pr_changed_paths", lambda *args: {PLAN})

    context = gate.load_pr_context("vamseeachanta/workspace-hub", 2881)
    assert context.head_sha == HEAD
    assert context.base_sha == BASE


def test_run_enabled_can_allow_valid_mocked_context(monkeypatch):
    args = type("Args", (), {
        "repo": "vamseeachanta/workspace-hub",
        "pr": 2881,
        "owners": OWNER,
        "require_separate_approver": False,
    })()
    monkeypatch.setattr(gate, "fetch_actor_type", lambda login: "User")
    monkeypatch.setattr(gate, "load_pr_context", lambda *a: gate.PrContext(
        "feat/2817-plan-approval-gate", OWNER, {PLAN}, HEAD, BASE))
    monkeypatch.setattr(gate, "load_issue_approval", lambda *a: _approval())
    assert gate._run_enabled(args) == 0


def test_run_enabled_skips_low_risk_paths_without_issue_branch(monkeypatch):
    args = type("Args", (), {
        "repo": "vamseeachanta/workspace-hub",
        "pr": 2881,
        "owners": OWNER,
        "require_separate_approver": False,
    })()
    monkeypatch.setattr(gate, "fetch_actor_type", lambda login: "User")
    monkeypatch.setattr(gate, "load_pr_context", lambda *a: gate.PrContext(
        "docs/no-issue", OWNER, {"docs/readme.md", "tests/workflow/test_x.py"}, HEAD, BASE))
    monkeypatch.setattr(gate, "load_issue_approval", lambda *a: (_ for _ in ()).throw(AssertionError))
    assert gate._run_enabled(args) == 0


def test_needs_plan_approval_paths_matches_legacy_scope():
    assert gate.needs_plan_approval_paths({"src/app.py"}) is True
    assert gate.needs_plan_approval_paths({"scripts/workflow/gate.py", "tests/test_gate.py"}) is False


def test_enforcement_workflow_falls_back_when_uv_is_absent():
    text = (Path(__file__).resolve().parents[2] / ".github" / "workflows" /
            "enforcement-gate.yml").read_text()
    assert "command -v uv" in text
    assert "python3 scripts/workflow/plan_approval_gate_check.py" in text


def test_latest_authorized_binding_ignores_later_unauthorized_attempt():
    sources = [
        {
            "author": {"login": OWNER},
            "updatedAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`",
        },
        {
            "author": {"login": "contributor"},
            "updatedAt": "2026-05-30T12:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{'8' * 40}`",
        },
    ]
    binding = gate.extract_plan_binding(sources, {OWNER}, {OWNER: "User"})
    assert binding is not None and binding.recorded_by == OWNER


def test_extract_plan_binding_rejects_ambiguous_multiple_paths_or_revisions():
    sources = [
        {
            "author": {"login": OWNER},
            "updatedAt": "2026-05-30T11:00:00Z",
            "body": (
                f"Plan: `{PLAN}`\n"
                f"Plan: `docs/plans/2026-05-30-issue-9999-other.md`\n"
                f"Plan revision: `{SHA}`"
            ),
        }
    ]
    assert gate.extract_plan_binding(sources, {OWNER}, {OWNER: "User"}) is None


def test_extract_plan_binding_rejects_non_hex_suffix_on_revision():
    sources = [
        {
            "author": {"login": OWNER},
            "updatedAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: {SHA}zzzz",
        }
    ]
    assert gate.extract_plan_binding(sources, {OWNER}, {OWNER: "User"}) is None
