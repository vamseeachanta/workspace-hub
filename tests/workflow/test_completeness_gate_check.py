"""Tests for the #2798 close-gate decision logic.

The decision function is the authoritative core called by BOTH the GitHub Action
(on issues.closed -> reopen if it denies) and the local advisory pre-flight. It
encodes the review fixes: a computed record must exist; an owner-only verified
label must be present; the label must have been applied by an authorized actor
who is NOT the closing actor (closes the agent-self-verify spoof, Claude#2/Codex#20).
"""
import sys
from pathlib import Path

SCRIPTS_WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(SCRIPTS_WORKFLOW))

import completeness_gate_check as gate  # noqa: E402

VERIFIED = "status:completeness-verified"
OWNERS = {"vamseeachanta"}


def _record(pct=95, threshold=90):
    return {"completeness_pct": pct, "threshold": threshold, "cls": "code"}


def test_allows_when_record_and_verified_label_by_authorized_distinct_actor():
    d = gate.evaluate_close(
        record=_record(), labels=[VERIFIED], label_actor="vameseeachanta" if False else "vamseeachanta",
        closing_actor="hermes-bot", authorized_appliers=OWNERS,
    )
    assert d.allowed is True


def test_denies_when_no_computed_record():
    d = gate.evaluate_close(record=None, labels=[VERIFIED], label_actor="vamseeachanta",
                            closing_actor="hermes-bot", authorized_appliers=OWNERS)
    assert d.allowed is False
    assert "record" in d.reason.lower()


def test_denies_when_verified_label_absent():
    d = gate.evaluate_close(record=_record(), labels=["status:plan-approved"], label_actor=None,
                            closing_actor="hermes-bot", authorized_appliers=OWNERS)
    assert d.allowed is False
    assert "label" in d.reason.lower()


def test_denies_when_label_applied_by_unauthorized_actor():
    # spoof attempt: a non-owner applied the verified label
    d = gate.evaluate_close(record=_record(), labels=[VERIFIED], label_actor="random-contributor",
                            closing_actor="hermes-bot", authorized_appliers=OWNERS)
    assert d.allowed is False
    assert "authorized" in d.reason.lower() or "actor" in d.reason.lower()


def test_denies_when_label_actor_equals_closing_actor():
    # the closer cannot also be the verifier (no self-verify)
    d = gate.evaluate_close(record=_record(), labels=[VERIFIED], label_actor="vamseeachanta",
                            closing_actor="vamseeachanta", authorized_appliers=OWNERS)
    assert d.allowed is False
    assert "self" in d.reason.lower() or "same" in d.reason.lower()


def test_denies_when_pct_below_threshold():
    d = gate.evaluate_close(record=_record(pct=70, threshold=90), labels=[VERIFIED],
                            label_actor="vamseeachanta", closing_actor="hermes-bot",
                            authorized_appliers=OWNERS)
    assert d.allowed is False
    assert "threshold" in d.reason.lower() or "70" in d.reason


def test_reason_is_present_on_allow_too():
    d = gate.evaluate_close(record=_record(), labels=[VERIFIED], label_actor="vamseeachanta",
                            closing_actor="hermes-bot", authorized_appliers=OWNERS)
    assert d.reason  # non-empty explanation either way
