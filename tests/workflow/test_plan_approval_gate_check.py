"""Tests for #2817 plan-approval label-authority gate."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import plan_approval_gate_check as gate  # noqa: E402
import plan_approval_gate_io as gate_io  # noqa: E402


OWNER = "vamseeachanta"
PLAN = "docs/plans/2026-05-30-issue-2817-plan-approval-label-authority.md"
SHA = "2f3d873d48acd05336268ac679f47b5b2708a567"


def _t(hour: int) -> dt.datetime:
    return dt.datetime(2026, 5, 30, hour, 0, tzinfo=dt.timezone.utc)


def _ctx(**kw) -> gate.PrContext:
    base = dict(
        branch_name="feat/2817-plan-approval-gate",
        pr_author=OWNER,
        touched_paths={PLAN, "scripts/workflow/plan_approval_gate_check.py"},
        head_sha="9" * 40,
    )
    base.update(kw)
    return gate.PrContext(**base)


def _binding(**kw) -> gate.PlanBinding:
    base = dict(
        plan_path=PLAN,
        revision_sha=SHA,
        recorded_by=OWNER,
        recorded_by_type="User",
        recorded_at=_t(10),
    )
    base.update(kw)
    return gate.PlanBinding(**base)


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


def _eval(**kw) -> gate.GateDecision:
    base = dict(
        context=_ctx(),
        approvals={2817: _approval()},
        owners={OWNER},
    )
    base.update(kw)
    return gate.evaluate_plan_approval(**base)


def test_authorized_human_label_passes():
    decision = _eval()
    assert decision.allowed is True
    assert "2817" in decision.reason


def test_owners_var_unset_fails_closed():
    decision = _eval(owners=set())
    assert decision.allowed is False
    assert "owners" in decision.reason.lower()


def test_no_linked_issue_fails_closed():
    decision = _eval(context=_ctx(branch_name="feat/misc-cleanup"))
    assert decision.allowed is False
    assert "branch name" in decision.reason.lower()


def test_branch_issue_is_authoritative_over_native_refs():
    assert gate.resolve_linked_issues("feat/2817-plan-approval-gate") == [2817]


def test_pr_body_or_commit_refs_are_not_authority():
    # The resolver has no body/trailer input by design. Without a branch issue or
    # GitHub-native issue list, author-controlled textual refs cannot authorize.
    assert gate.resolve_linked_issues("feat/misc-cleanup") == []


def test_no_plan_approved_label_fails():
    decision = _eval(approvals={2817: _approval(label_actor=None, label_applied_at=None)})
    assert decision.allowed is False
    assert "label" in decision.reason.lower()


def test_unauthorized_label_actor_fails():
    decision = _eval(approvals={2817: _approval(label_actor="contributor")})
    assert decision.allowed is False
    assert "authorized" in decision.reason.lower()


def test_bot_label_actor_fails_by_login_or_type():
    by_login = _eval(
        approvals={2817: _approval(label_actor="renovate[bot]", label_actor_type="User")}
    )
    by_type = _eval(
        approvals={2817: _approval(label_actor="automation", label_actor_type="Bot")}
    )
    assert by_login.allowed is False
    assert by_type.allowed is False
    assert "bot" in by_login.reason.lower()
    assert "bot" in by_type.reason.lower()


def test_plan_binding_missing_fails():
    decision = _eval(approvals={2817: _approval(plan_binding=None)})
    assert decision.allowed is False
    assert "plan" in decision.reason.lower()


def test_plan_binding_by_unauthorized_actor_fails():
    decision = _eval(
        approvals={2817: _approval(plan_binding=_binding(recorded_by="contributor"))}
    )
    assert decision.allowed is False
    assert "binding" in decision.reason.lower()


def test_plan_binding_must_match_issue_number():
    wrong_plan = "docs/plans/2026-05-30-issue-9999-unrelated.md"
    decision = _eval(approvals={2817: _approval(plan_binding=_binding(plan_path=wrong_plan))})
    assert decision.allowed is False
    assert "issue #2817" in decision.reason


def test_plan_binding_issue_match_is_delimiter_safe():
    assert gate.plan_path_matches_issue("docs/plans/2026-05-30-issue-2817-plan.md", 2817) is True
    assert gate.plan_path_matches_issue("docs/plans/2026-05-30-issue-28170-plan.md", 2817) is False
    assert gate.plan_path_matches_issue("docs/plans/2026-05-30-issue-2817x-plan.md", 2817) is False


def test_pr_must_touch_recorded_plan_path():
    decision = _eval(context=_ctx(touched_paths={"scripts/workflow/plan_approval_gate_check.py"}))
    assert decision.allowed is False
    assert PLAN in decision.reason


def test_recorded_revision_must_be_verified_against_plan_path():
    decision = _eval(approvals={2817: _approval(plan_revision_verified=False)})
    assert decision.allowed is False
    assert "revision" in decision.reason.lower()


def test_pr_head_plan_blob_must_match_approved_revision():
    decision = _eval(approvals={2817: _approval(plan_head_matches_revision=False)})
    assert decision.allowed is False
    assert "head plan" in decision.reason.lower()


def test_label_predates_plan_revision_fails():
    decision = _eval(approvals={2817: _approval(label_applied_at=_t(10), plan_revision_time=_t(11))})
    assert decision.allowed is False
    assert "re-approval" in decision.reason.lower() or "fresh" in decision.reason.lower()


def test_label_predates_binding_comment_update_fails():
    decision = _eval(
        approvals={
            2817: _approval(
                label_applied_at=_t(12),
                plan_revision_time=_t(11),
                plan_binding=_binding(recorded_at=_t(13)),
            )
        }
    )
    assert decision.allowed is False
    assert "re-approval" in decision.reason.lower() or "fresh" in decision.reason.lower()


def test_synchronize_after_approval_does_not_invalidate():
    # R2: PR head/push time is intentionally absent from the decision. A later
    # synchronize event cannot stale a plan approval that post-dates the plan.
    decision = _eval(approvals={2817: _approval(label_applied_at=_t(12), plan_revision_time=_t(11))})
    assert decision.allowed is True


def test_separate_approver_default_off_for_solo_operator():
    decision = _eval(context=_ctx(pr_author=OWNER))
    assert decision.allowed is True


def test_separate_approver_opt_in_blocks_author_as_approver():
    decision = _eval(context=_ctx(pr_author=OWNER), require_separate_approver=True)
    assert decision.allowed is False
    assert "separate" in decision.reason.lower()


def test_separate_approver_compares_case_insensitively():
    decision = _eval(context=_ctx(pr_author=OWNER.upper()), require_separate_approver=True)
    assert decision.allowed is False
    assert "separate" in decision.reason.lower()


def test_legacy_marker_grants_no_authority():
    # Legacy local markers are not an input to the server gate. Without the label
    # event, a marker cannot make the decision pass.
    decision = _eval(approvals={2817: _approval(label_actor=None, label_applied_at=None)})
    assert decision.allowed is False


def test_owners_containing_bot_fails_startup():
    decision = gate.validate_owner_types({"vamseeachanta": "User", "renovate[bot]": "Bot"})
    assert decision.allowed is False
    assert "bot" in decision.reason.lower()


def test_extract_plan_binding_requires_authorized_comment_path_and_revision():
    comments = [
        {
            "author": {"login": "contributor"},
            "createdAt": "2026-05-30T10:00:00Z",
            "updatedAt": "2026-05-30T10:30:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`",
        },
        {
            "author": {"login": OWNER},
            "createdAt": "2026-05-30T11:00:00Z",
            "updatedAt": "2026-05-30T11:30:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`",
        },
    ]
    binding = gate.extract_plan_binding(comments, {OWNER}, {OWNER: "User"})
    assert binding == _binding(recorded_at=dt.datetime(2026, 5, 30, 11, 30, tzinfo=dt.timezone.utc))


def test_extract_plan_binding_ignores_comments_without_revision():
    comments = [
        {
            "author": {"login": OWNER},
            "createdAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`",
        }
    ]
    assert gate.extract_plan_binding(comments, {OWNER}, {OWNER: "User"}) is None


def test_load_issue_binding_sources_includes_issue_body_and_comments(monkeypatch):
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
            return [
                {
                    "user": {"login": OWNER},
                    "body": "later comment",
                    "created_at": "2026-05-30T12:00:00Z",
                    "updated_at": "2026-05-30T12:00:00Z",
                }
            ]
        raise AssertionError(args)

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    sources = gate.load_issue_binding_sources("vamseeachanta/workspace-hub", 2817)
    assert sources[0]["body"].startswith("Plan:")
    assert sources[1]["body"] == "later comment"


def test_extract_plan_binding_requires_full_revision_sha():
    comments = [
        {
            "author": {"login": OWNER},
            "createdAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA[:12]}`",
        }
    ]
    assert gate.extract_plan_binding(comments, {OWNER}, {OWNER: "User"}) is None


def test_extract_plan_binding_rejects_overlong_revision_sha():
    comments = [
        {
            "author": {"login": OWNER},
            "createdAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}a`",
        }
    ]
    assert gate.extract_plan_binding(comments, {OWNER}, {OWNER: "User"}) is None


def test_extract_plan_binding_rejects_hex_after_closing_backtick():
    comments = [
        {
            "author": {"login": OWNER},
            "createdAt": "2026-05-30T11:00:00Z",
            "body": f"Plan: `{PLAN}`\nPlan revision: `{SHA}`a",
        }
    ]
    assert gate.extract_plan_binding(comments, {OWNER}, {OWNER: "User"}) is None


def test_event_pr_number_bad_env_fails_closed_not_crash(monkeypatch):
    monkeypatch.setenv("PR_NUMBER", "not-an-int")
    assert gate._event_pr_number() is None


def test_plan_revision_anchor_requires_commit_to_touch_plan(monkeypatch):
    calls = []

    def fake_gh_json(*args):
        calls.append(args)
        if args[:2] == ("api", f"repos/vamseeachanta/workspace-hub/commits/{SHA}"):
            return {"files": [{"filename": PLAN}]}
        return {"data": {"repository": {"object": {"pushedDate": "2026-05-30T12:00:00Z"}}}}

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    anchor, verified = gate.fetch_plan_revision_anchor(
        "vamseeachanta/workspace-hub", SHA, PLAN, _t(11)
    )
    assert verified is True
    assert anchor == _t(12)

    def wrong_file_gh_json(*args):
        if args[:2] == ("api", f"repos/vamseeachanta/workspace-hub/commits/{SHA}"):
            return {"files": [{"filename": "docs/plans/2026-05-30-issue-9999.md"}]}
        return {}

    monkeypatch.setattr(gate_io, "gh_json", wrong_file_gh_json)
    assert gate.fetch_plan_revision_anchor("vamseeachanta/workspace-hub", SHA, PLAN, _t(11)) == (None, False)


def test_plan_revision_anchor_requires_github_pushed_date(monkeypatch):
    def fake_gh_json(*args):
        if args[:2] == ("api", f"repos/vamseeachanta/workspace-hub/commits/{SHA}"):
            return {"files": [{"filename": PLAN}]}
        return {"data": {"repository": {"object": {"pushedDate": None}}}}

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    assert gate.fetch_plan_revision_anchor("vamseeachanta/workspace-hub", SHA, PLAN, _t(13)) == (None, False)


def test_plan_revision_anchor_uses_latest_of_push_and_binding_update(monkeypatch):
    def fake_gh_json(*args):
        if args[:2] == ("api", f"repos/vamseeachanta/workspace-hub/commits/{SHA}"):
            return {"files": [{"filename": PLAN}]}
        return {"data": {"repository": {"object": {"pushedDate": "2026-05-30T09:00:00Z"}}}}

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    anchor, verified = gate.fetch_plan_revision_anchor(
        "vamseeachanta/workspace-hub", SHA, PLAN, _t(13)
    )
    assert verified is True
    assert anchor == _t(13)


def test_plan_blob_matches_revision_compares_head_and_revision_blobs(monkeypatch):
    def fake_gh_json(*args):
        ref = args[1].split("ref=", 1)[1]
        if ref == SHA:
            return {"sha": "blob-a"}
        return {"sha": "blob-a" if ref == "9" * 40 else "blob-b"}

    monkeypatch.setattr(gate_io, "gh_json", fake_gh_json)
    assert gate.plan_blob_matches_revision("vamseeachanta/workspace-hub", SHA, "9" * 40, PLAN) is True
    assert gate.plan_blob_matches_revision("vamseeachanta/workspace-hub", SHA, "8" * 40, PLAN) is False


def test_enforcement_workflow_runs_new_gate_then_legacy_gate_with_captured_rc():
    text = (REPO / ".github" / "workflows" / "enforcement-gate.yml").read_text()
    new_gate = "uv run python scripts/workflow/plan_approval_gate_check.py"
    capture = "PLAN_APPROVAL_LABEL_GATE_RC=$?"
    legacy = "scripts/enforcement/require-plan-approval.sh --strict"
    final_exit = 'exit "$PLAN_APPROVAL_LABEL_GATE_RC"'
    assert new_gate in text
    assert "PLAN_APPROVAL_GATE_ENABLED=1 is intentionally blocking" in text
    assert capture in text
    assert legacy in text
    assert final_exit in text
    assert text.index(capture) < text.index(legacy) < text.index(final_exit)
