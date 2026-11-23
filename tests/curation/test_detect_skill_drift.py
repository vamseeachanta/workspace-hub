"""TDD tests for #3250 — the cross-provider skill-drift detector + alert (epic #3248).

Targets scripts/curation/detect_skill_drift.py: the PURE decide-core
(drift_signature / evaluate_drift) plus the thin CLI (run_cli, publish_drift). Pattern mirrors
tests/readiness/test_skill_currency.py (importlib spec load + a small fixture builder).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "curation" / "detect_skill_drift.py"

spec = importlib.util.spec_from_file_location("detect_skill_drift", MODULE_PATH)
assert spec is not None and spec.loader is not None
det = importlib.util.module_from_spec(spec)
sys.modules["detect_skill_drift"] = det
spec.loader.exec_module(det)

NOW = "2026-06-26T12:00:00+00:00"


def _facts(**kw) -> dict:
    """A skill-currency FACTS dict (as audit_skill_currency.py emits)."""
    base = {
        "machine": "dev-primary",
        "audited_at": NOW,
        "canonical_count": 44,
        "gemini_present": True,
        "gemini_unexpected": 0,
        "gemini_expected": 0,
        "gemini_unexpected_families": [],
        "index_dangling": 0,
        "index_stale": False,
        "schema_version": 2,
    }
    base.update(kw)
    return base


def _drift_facts(families, **kw) -> dict:
    return _facts(gemini_unexpected=len(families), gemini_unexpected_families=list(families), **kw)


# ── drift_signature: PURE fingerprint ──────────────────────────────────────
def test_signature_clean():
    assert det.drift_signature(_facts()) == "CLEAN"


def test_signature_names_sorted():
    # order-independent + name-stable
    a = det.drift_signature(_drift_facts(["b", "a"]))
    b = det.drift_signature(_drift_facts(["a", "b"]))
    assert a == b == "fam:a,b"


def test_signature_index_excluded_by_default():
    # standing index rot must NOT enter the default signature
    assert det.drift_signature(_facts(index_dangling=200)) == "CLEAN"


def test_signature_includes_index_optin():
    sig = det.drift_signature(_facts(index_dangling=3), include_index=True)
    assert "idx:3" in sig


def test_signature_index_optin_ignores_zero_and_bool():
    assert det.drift_signature(_facts(index_dangling=0), include_index=True) == "CLEAN"
    assert det.drift_signature(_facts(index_dangling=True), include_index=True) == "CLEAN"


def test_signature_unreadable():
    for bad in (0, None, "44", -1, True):
        assert det.drift_signature(_facts(canonical_count=bad)) == "UNREADABLE"


def test_signature_gemini_absent_no_drift():
    # a stale count/names list must be ignored when the gemini surface isn't present
    assert det.drift_signature(
        _facts(gemini_present=False, gemini_unexpected=5,
               gemini_unexpected_families=["x"])) == "CLEAN"


def test_signature_count_fallback_without_names():
    # schema-1 audit (count but no names) still registers drift
    f = _facts(gemini_unexpected=2)
    f.pop("gemini_unexpected_families")
    assert det.drift_signature(f) == "fam-count:2"


# ── evaluate_drift: transition + spam suppression ──────────────────────────
def test_first_run_no_falsefire_on_index_rot():
    r = det.evaluate_drift(_facts(index_dangling=200), None, now_iso=NOW)
    assert r["new_drift"] is False
    assert r["alerts"] == []
    assert r["signature"] == "CLEAN"


def test_new_drift_alerts_once():
    r = det.evaluate_drift(_drift_facts(["x"]), None, now_iso=NOW)
    assert r["new_drift"] is True
    assert len(r["alerts"]) == 1
    assert r["alerts"][0]["status"] == "fail"
    assert r["alerts"][0]["kind"] == "skill-drift"


def test_same_drift_suppressed():
    last = {"signature": "fam:x", "drift_present": True, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(_drift_facts(["x"]), last, now_iso="2026-06-26T18:00:00+00:00")
    assert r["new_drift"] is False
    assert r["alerts"] == []
    # first_seen preserved across an unchanged standing drift
    assert r["new_state"]["first_seen"] == NOW


def test_changed_drift_realerts():
    last = {"signature": "fam:a", "drift_present": True, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(_drift_facts(["a", "b"]), last, now_iso=NOW)
    assert r["new_drift"] is True
    assert len(r["alerts"]) == 1
    assert r["new_state"]["signature"] == "fam:a,b"


def test_recovery_emits_pass():
    last = {"signature": "fam:a", "drift_present": True, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(_facts(), last, now_iso=NOW)
    assert r["recovered"] is True
    assert len(r["alerts"]) == 1
    assert r["alerts"][0]["status"] == "pass"
    assert r["alerts"][0]["kind"] == "skill-drift-cleared"


def test_clean_stays_quiet():
    last = {"signature": "CLEAN", "drift_present": False, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(_facts(), last, now_iso=NOW)
    assert r["new_drift"] is False
    assert r["recovered"] is False
    assert r["alerts"] == []


def test_full_transition_sequence_alerts_once_each():
    # none -> drift -> same -> changed -> recovery: exactly one alert per distinct state
    s0 = None
    r1 = det.evaluate_drift(_drift_facts(["a"]), s0, now_iso=NOW)               # none -> drift
    r2 = det.evaluate_drift(_drift_facts(["a"]), r1["new_state"], now_iso=NOW)  # drift -> same
    r3 = det.evaluate_drift(_drift_facts(["a", "b"]), r2["new_state"], now_iso=NOW)  # changed
    r4 = det.evaluate_drift(_facts(), r3["new_state"], now_iso=NOW)             # recovery
    assert [len(r["alerts"]) for r in (r1, r2, r3, r4)] == [1, 0, 1, 1]
    assert [r["alerts"][0]["status"] for r in (r1, r3, r4)] == ["fail", "fail", "pass"]


def test_unreadable_alerts_failclosed():
    last = {"signature": "CLEAN", "drift_present": False, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(_facts(canonical_count=None), last, now_iso=NOW)
    assert len(r["alerts"]) == 1
    assert r["alerts"][0]["kind"] == "audit-unreadable"
    assert r["alerts"][0]["status"] == "fail"


def test_unreadable_suppressed_when_unchanged():
    last = {"signature": "UNREADABLE", "drift_present": True, "first_seen": NOW, "updated_at": NOW}
    r = det.evaluate_drift(None, last, now_iso=NOW)
    assert r["signature"] == "UNREADABLE"
    assert r["alerts"] == []


def test_gemini_absent_no_drift_evaluate():
    r = det.evaluate_drift(
        _facts(gemini_present=False, gemini_unexpected=5, gemini_unexpected_families=["x"]),
        None, now_iso=NOW)
    assert r["signature"] == "CLEAN"
    assert r["alerts"] == []


def test_evaluate_pure_no_io(monkeypatch):
    # evaluate_drift must touch neither the filesystem nor subprocess.
    def _boom(*a, **k):
        raise AssertionError("evaluate_drift performed IO")
    monkeypatch.setattr(det.subprocess, "run", _boom)
    monkeypatch.setattr("builtins.open", _boom)
    r = det.evaluate_drift(_drift_facts(["a"]), None, now_iso=NOW)
    assert r["new_drift"] is True


# ── run_cli: injected notify, machine-label borrow, report-always ──────────
def _setup_state(tmp_path, monkeypatch, label, currency_facts=None):
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(det, "STATE", state)
    monkeypatch.setattr(det.audit_skill_currency, "machine_label", lambda: label)
    if currency_facts is not None:
        (state / f"skill-currency-{label}.json").write_text(json.dumps(currency_facts))
    return state


def test_run_cli_injected_notify(tmp_path, monkeypatch):
    state = _setup_state(tmp_path, monkeypatch, "dev-primary", _drift_facts(["x"]))
    calls = []
    rc = det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=calls.append)
    assert rc == 0   # success even on new-drift (exit code not overloaded; the alert is the signal)
    assert len(calls) == 1
    assert (state / "skill-drift-report-dev-primary.json").exists()
    assert (state / "skill-drift-dev-primary.json").exists()


def test_run_cli_uses_audit_machine_label(tmp_path, monkeypatch):
    state = _setup_state(tmp_path, monkeypatch, "BOXLBL", _drift_facts(["y"]))
    det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=lambda a: None)
    # keyed entirely on the audit's machine_label()
    assert (state / "skill-drift-report-BOXLBL.json").exists()
    assert (state / "skill-drift-BOXLBL.json").exists()


def test_run_cli_spam_suppressed_across_two_runs(tmp_path, monkeypatch):
    _setup_state(tmp_path, monkeypatch, "dev-primary", _drift_facts(["x"]))
    calls = []
    det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=calls.append)
    det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=calls.append)
    assert len(calls) == 1  # second run on the same standing drift is silent


def test_run_cli_report_always_written_when_clean(tmp_path, monkeypatch):
    state = _setup_state(tmp_path, monkeypatch, "dev-primary", _facts())
    calls = []
    rc = det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=calls.append)
    assert rc == 0
    assert calls == []
    assert (state / "skill-drift-report-dev-primary.json").exists()


def test_run_cli_missing_audit_state_alerts_failclosed(tmp_path, monkeypatch):
    # no skill-currency file written → unreadable → one audit-unreadable alert
    _setup_state(tmp_path, monkeypatch, "dev-primary", None)
    calls = []
    det.run_cli(SimpleNamespace(include_index=False, publish=False), notify_fn=calls.append)
    assert len(calls) == 1
    assert calls[0]["kind"] == "audit-unreadable"


def test_default_notify_uses_skill_drift_job(tmp_path, monkeypatch):
    recorded = {}
    monkeypatch.setattr(det.subprocess, "run",
                        lambda cmd, **k: recorded.setdefault("cmd", cmd))
    det._default_notify({"kind": "skill-drift", "detail": "d", "status": "fail"})
    cmd = recorded["cmd"]
    assert cmd[1:5] == [str(det.NOTIFY_SH), "cron", "skill-drift", "fail"]


# ── publish_drift: bounded + fail-soft ─────────────────────────────────────
def test_publish_bounded_timeout(tmp_path, monkeypatch):
    state = _setup_state(tmp_path, monkeypatch, "dev-primary")
    (state / "skill-drift-report-dev-primary.json").write_text("{}")

    def _timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="publish", timeout=det.PUBLISH_TIMEOUT_S)
    monkeypatch.setattr(det.subprocess, "run", _timeout)
    assert det.publish_drift("dev-primary") == f"publish-timeout ({det.PUBLISH_TIMEOUT_S}s)"


def test_publish_skipped_when_no_report(tmp_path, monkeypatch):
    _setup_state(tmp_path, monkeypatch, "dev-primary")
    assert det.publish_drift("dev-primary").startswith("publish-skipped")
