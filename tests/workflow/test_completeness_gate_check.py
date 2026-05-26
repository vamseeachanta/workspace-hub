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
                expected_issue=2798, body_verified_fresh=True)
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

def test_gate_applies_only_when_opted_in_and_plan_approved():
    assert gate.gate_applies(["gate:completeness", "status:plan-approved"]) is True


def test_gate_does_not_apply_without_opt_in_label():
    # the existing backlog (plan-approved but not opted-in) is untouched
    assert gate.gate_applies(["status:plan-approved"]) is False


def test_gate_does_not_apply_without_plan_approved():
    assert gate.gate_applies(["gate:completeness"]) is False


def test_gate_does_not_apply_to_unlabeled_issue():
    assert gate.gate_applies([]) is False


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
