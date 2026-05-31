"""#2817 PR1: shared label-actor-authority helper, generalized from #2798's
completeness_gate_runner (`_verified_label_event`). The extraction must be a pure,
non-regressive move — the same timeline-resolution behavior, parameterized by label name —
so BOTH the completeness gate and the new plan-approval gate share one audited primitive.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "scripts" / "workflow" / "label_authority.py"

spec = importlib.util.spec_from_file_location("label_authority", MOD)
assert spec is not None and spec.loader is not None
la = importlib.util.module_from_spec(spec)
sys.modules["label_authority"] = la  # register before exec (import safety)
spec.loader.exec_module(la)


def test_parse_iso_handles_z_suffix_and_none():
    dt = la.parse_iso("2026-05-30T04:00:00Z")
    assert dt is not None and dt.year == 2026 and dt.month == 5 and dt.day == 30
    assert la.parse_iso(None) is None
    assert la.parse_iso("") is None


def test_verified_label_event_returns_latest_application(monkeypatch):
    # multiple applications of the SAME label -> the most recent (actor, applied_at) wins
    events = [
        {"event": "labeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "alice"}, "created_at": "2026-05-01T00:00:00Z"},
        {"event": "labeled", "label": {"name": "unrelated"},
         "actor": {"login": "bob"}, "created_at": "2026-05-02T00:00:00Z"},
        {"event": "labeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "vamsee"}, "created_at": "2026-05-03T00:00:00Z"},
    ]
    monkeypatch.setattr(la, "gh_json", lambda *a: events)
    actor, at = la.verified_label_event("o/r", 1, "status:plan-approved")
    assert actor == "vamsee"
    assert at == la.parse_iso("2026-05-03T00:00:00Z")


def test_verified_label_event_parameterized_by_label(monkeypatch):
    # the SAME timeline yields different results for different label names (the generalization)
    events = [
        {"event": "labeled", "label": {"name": "status:completeness-verified"},
         "actor": {"login": "owner"}, "created_at": "2026-05-03T00:00:00Z"},
    ]
    monkeypatch.setattr(la, "gh_json", lambda *a: events)
    assert la.verified_label_event("o/r", 1, "status:completeness-verified")[0] == "owner"
    assert la.verified_label_event("o/r", 1, "status:plan-approved") == (None, None)


def test_verified_label_event_absent_is_none_pair(monkeypatch):
    monkeypatch.setattr(la, "gh_json", lambda *a: [])
    assert la.verified_label_event("o/r", 1, "status:plan-approved") == (None, None)
    monkeypatch.setattr(la, "gh_json", lambda *a: None)  # gh returned empty
    assert la.verified_label_event("o/r", 1, "status:plan-approved") == (None, None)


def test_verified_label_event_ignores_unlabeled_events(monkeypatch):
    # an "unlabeled" event for the same name must NOT count as an application
    events = [
        {"event": "labeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "vamsee"}, "created_at": "2026-05-03T00:00:00Z"},
        {"event": "unlabeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "vamsee"}, "created_at": "2026-05-04T00:00:00Z"},
    ]
    monkeypatch.setattr(la, "gh_json", lambda *a: events)
    actor, at = la.verified_label_event("o/r", 1, "status:plan-approved")
    assert actor == "vamsee" and at == la.parse_iso("2026-05-03T00:00:00Z")


def test_verified_label_event_uses_readd_actor_after_unlabel(monkeypatch):
    events = [
        {"event": "labeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "owner"}, "created_at": "2026-05-03T00:00:00Z"},
        {"event": "unlabeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "owner"}, "created_at": "2026-05-04T00:00:00Z"},
        {"event": "labeled", "label": {"name": "status:plan-approved"},
         "actor": {"login": "contributor"}, "created_at": "2026-05-05T00:00:00Z"},
    ]
    monkeypatch.setattr(la, "gh_json", lambda *a: events)
    actor, at = la.verified_label_event("o/r", 1, "status:plan-approved")
    assert actor == "contributor" and at == la.parse_iso("2026-05-05T00:00:00Z")


def test_is_authorized_human_membership_only_by_default():
    # R6: callers opt into bot rejection. Existing completeness behavior remains
    # membership-only and can still accept a service account if configured.
    assert la.is_authorized_human("service[bot]", {"service[bot]"}) is True


def test_is_authorized_human_rejects_bots_when_opted_in():
    owners = {"service[bot]", "automation", "vamseeachanta"}
    assert la.is_authorized_human("vamseeachanta", owners, reject_bots=True, actor_type="User") is True
    assert la.is_authorized_human("service[bot]", owners, reject_bots=True, actor_type="User") is False
    assert la.is_authorized_human("automation", owners, reject_bots=True, actor_type="Bot") is False


def test_is_authorized_human_matches_github_logins_case_insensitively():
    assert la.is_authorized_human("VamseeAchanta", {"vamseeachanta"}, reject_bots=True,
                                  actor_type="User") is True


def test_label_is_fresh_requires_label_at_or_after_anchor():
    plan_time = la.parse_iso("2026-05-30T11:00:00Z")
    approved_after = la.parse_iso("2026-05-30T12:00:00Z")
    approved_before = la.parse_iso("2026-05-30T10:00:00Z")
    assert la.label_is_fresh(approved_after, plan_time) is True
    assert la.label_is_fresh(approved_before, plan_time) is False
    assert la.label_is_fresh(None, plan_time) is False
    assert la.label_is_fresh(approved_after, None) is False
