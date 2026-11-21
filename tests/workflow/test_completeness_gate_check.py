"""Tests for the #2798 close-gate decision (hardened per code review)."""
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import completeness_gate_check as gate  # noqa: E402

VERIFIED = "status:completeness-verified"
OWNERS = {"vamseeachanta"}


def _record(pct=95, cls="code", issue=2798, **extra):
    r = {"completeness_pct": pct, "cls": cls, "issue_number": issue}
    r.update(extra)
    return r


def _eval(**kw):
    base = dict(record=_record(), labels=[VERIFIED], label_actor="vamseeachanta",
                closing_actor="hermes-bot", authorized_appliers=OWNERS,
                expected_issue=2798, body_verified_fresh=True, work_authors={"pr-author"})
    base.update(kw)
    return gate.evaluate_close(**base)


def test_allows_when_all_conditions_met():
    assert _eval().allowed is True


def test_denies_when_no_record():
    d = _eval(record=None)
    assert d.allowed is False and "record" in d.reason.lower()


def test_denies_when_record_issue_mismatch_forged():
    d = _eval(record=_record(issue=9999))  # copied/forged record from another issue
    assert d.allowed is False and ("match" in d.reason.lower() or "forged" in d.reason.lower())


def test_threshold_comes_from_config_not_record_so_forged_threshold_ignored():
    # forged record claims threshold 0 to sneak a low score past the gate
    d = _eval(record=_record(pct=10, cls="code", threshold=0))
    assert d.allowed is False  # config threshold 90 applies, 10 < 90
    assert "90" in d.reason


def test_denies_unknown_class():
    d = _eval(record=_record(cls="bogus"))
    assert d.allowed is False and "class" in d.reason.lower()


def test_denies_when_verified_label_absent():
    d = _eval(labels=["status:plan-approved"], label_actor=None)
    assert d.allowed is False and "label" in d.reason.lower()


def test_denies_unauthorized_label_actor():
    d = _eval(label_actor="random-contributor")
    assert d.allowed is False and ("authorized" in d.reason.lower() or "actor" in d.reason.lower())


def test_allows_same_actor_by_default_solo_operation():
    # solo operator both verifies and closes — allowed by default (separation is opt-in)
    d = _eval(label_actor="vamseeachanta", closing_actor="vamseeachanta")
    assert d.allowed is True


def test_denies_same_actor_only_when_separate_closer_required():
    d = _eval(label_actor="vamseeachanta", closing_actor="vamseeachanta", require_separate_closer=True)
    assert d.allowed is False and ("separate" in d.reason.lower() or "same" in d.reason.lower())


def test_denies_when_body_edited_after_verification():
    d = _eval(body_verified_fresh=False)
    assert d.allowed is False and ("edited" in d.reason.lower() or "re-verification" in d.reason.lower())


def test_denies_when_pct_below_config_threshold():
    d = _eval(record=_record(pct=70))
    assert d.allowed is False and "70" in d.reason


def test_evidence_class_uses_80_threshold():
    assert _eval(record=_record(pct=85, cls="evidence")).allowed is True   # 85 >= 80
    assert _eval(record=_record(pct=75, cls="evidence")).allowed is False  # 75 < 80


# ---- opt-in scoping (rollout fix) ----

def test_gate_applies_to_legacy_opt_in_with_plan_approval():
    assert gate.gate_applies(["gate:completeness", "status:plan-approved"]) is True


def test_gate_does_not_apply_without_opt_in_label():
    # the existing backlog (plan-approved but not opted-in) is untouched
    assert gate.gate_applies(["status:plan-approved"]) is False


def test_gate_applies_without_separate_plan_approval():
    assert gate.gate_applies(["gate:completeness", "gate:completeness-v2"]) is True


def test_bulk_labeled_legacy_backlog_remains_out_of_scope():
    assert gate.gate_applies(["gate:completeness"]) is False


def test_legacy_parameter_cannot_add_an_approval_requirement():
    assert gate.gate_applies(["custom:complete", "gate:completeness-v2"], "custom:complete", "legacy:approved") is True


def test_autoapply_covers_new_and_resumed_work_without_backlog_sweep():
    workflow = Path(__file__).resolve().parents[2] / ".github/workflows/autoapply-completeness-label.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "types: [opened, labeled]" in text
    condition = text.split("    if: >-", 1)[1].split("    steps:", 1)[0]
    assert "github.event.action == 'opened'" in condition
    for status in ("status:plan-review", "dispatch:active", "status:plan-approved"):
        assert status in condition
    assert "issues: write" in text
    assert "gate:completeness-v2" in text


def test_gate_does_not_apply_to_unlabeled_issue():
    assert gate.gate_applies([]) is False


def test_closure_guidance_preserves_approval_independent_enrollment():
    from pathlib import Path
    text = (Path(__file__).resolve().parents[2] / ".claude/rules/completeness-before-close.md").read_text(encoding="utf-8")
    assert "gate:completeness-v2" in text
    assert "historical" in text
    assert "owner-only `status:completeness-verified`" not in text
    assert "did not write the work" in text
    assert "`work_by`" in text and "`verified_by`" in text


# ---- verifier did not write the work (rules review r5, card A) ----

def test_reviewer_who_is_not_the_author_may_verify():
    d = _eval(label_actor="reviewer", authorized_appliers={"vamseeachanta", "reviewer"},
              work_authors={"vamseeachanta"})
    assert d.allowed is True


def test_denies_labeler_who_authored_the_closing_pr_without_named_verifier():
    d = _eval(work_authors={"vamseeachanta"})
    assert d.allowed is False and "author of the closing PR or commit" in d.reason


def test_author_check_is_case_insensitive():
    assert _eval(work_authors={"VamseeAchanta"}).allowed is False


def test_shared_login_passes_when_record_names_a_separate_verifier():
    rec = _record(work_by="claude-worker", verified_by="codex-reviewer")
    assert _eval(record=rec, work_authors={"vamseeachanta"}).allowed is True


def test_shared_login_denies_when_verifier_is_the_author():
    rec = _record(work_by="claude-worker", verified_by="Claude-Worker")
    assert _eval(record=rec, work_authors={"vamseeachanta"}).allowed is False


def test_shared_login_denies_when_only_one_field_is_named():
    assert _eval(record=_record(verified_by="codex-reviewer"), work_authors={"vamseeachanta"}).allowed is False


def test_unknown_author_needs_named_verifier():
    assert _eval(work_authors=set()).allowed is False
    assert _eval(work_authors=None).allowed is False
    rec = _record(work_by="claude-worker", verified_by="codex-reviewer")
    assert _eval(record=rec, work_authors=set()).allowed is True


def test_unauthorized_labeler_still_denied_even_if_not_the_author():
    d = _eval(label_actor="random-contributor", work_authors={"vamseeachanta"})
    assert d.allowed is False and "unauthorized" in d.reason


def test_work_authors_from_pr_closer_commit_closer_and_merged_links():
    node = {
        "timelineItems": {"nodes": [{"closer": {"author": {"login": "pr-author"}}}]},
        "closedByPullRequestsReferences": {"nodes": [
            {"state": "MERGED", "author": {"login": "linked-author"}},
            {"state": "OPEN", "author": {"login": "open-author"}},
            {"state": "CLOSED", "author": {"login": "closed-author"}},
        ]},
    }
    assert gate.work_authors_from(node) == {"pr-author", "linked-author"}
    commit = {"timelineItems": {"nodes": [{"closer": {"author": {"user": {"login": "committer"}}}}]}}
    assert gate.work_authors_from(commit) == {"committer"}


def test_work_authors_from_manual_close_or_missing_data_is_empty():
    assert gate.work_authors_from({"timelineItems": {"nodes": [{"closer": None}]}}) == set()
    assert gate.work_authors_from(None) == set()
    assert gate.work_authors_from({"timelineItems": {"nodes": [{"closer": {"author": None}}]}}) == set()


def test_workflow_passes_reviewer_appliers_variable():
    workflow = Path(__file__).resolve().parents[2] / ".github/workflows/completeness-gate.yml"
    assert "COMPLETENESS_REVIEWERS: ${{ vars.COMPLETENESS_REVIEWERS }}" in workflow.read_text(encoding="utf-8")


# ---- body-freshness helper (fix #5: anchor on lastEditedAt, not updatedAt) ----

import datetime as _dt  # noqa: E402

def _t(h):  # helper: a UTC datetime at hour h on a fixed day
    return _dt.datetime(2026, 5, 26, h, 0, tzinfo=_dt.timezone.utc)


def test_fresh_when_label_after_body_edit():
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=_t(12), created_at=_t(0)) is True


def test_not_fresh_when_label_before_body_edit():
    assert gate.body_is_fresh(label_at=_t(11), last_edited_at=_t(12), created_at=_t(0)) is False


def test_falls_back_to_created_at_when_never_edited():
    # body never edited (lastEditedAt None) -> compare against createdAt
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=None, created_at=_t(0)) is True
    assert gate.body_is_fresh(label_at=_t(11), last_edited_at=None, created_at=_t(12)) is False


def test_not_fresh_when_no_label():
    assert gate.body_is_fresh(label_at=None, last_edited_at=_t(12), created_at=_t(0)) is False


def test_close_does_not_break_freshness_regression():
    # the bug: a later updatedAt (e.g. from the close) must NOT enter the calc.
    # helper only sees body-edit time, so a label applied after the body edit stays fresh
    # regardless of any later issue activity.
    assert gate.body_is_fresh(label_at=_t(16), last_edited_at=_t(12), created_at=_t(0)) is True
