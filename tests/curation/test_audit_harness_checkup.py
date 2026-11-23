"""TDD tests for #3408 — the per-machine harness-checkup (/doctor) audit (epic #3058).

Targets scripts/curation/audit_harness_checkup.py. All collectors are monkeypatched so the suite
never touches the real machine, the network, or ~/.claude*. Covers the pure verdict, fact assembly,
the no-network path, fail-closed on malformed evidence, and the allowlist-safety of emitted facts.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "curation" / "audit_harness_checkup.py"

spec = importlib.util.spec_from_file_location("audit_harness_checkup", MODULE_PATH)
assert spec is not None and spec.loader is not None
ahc = importlib.util.module_from_spec(spec)
sys.modules["audit_harness_checkup"] = ahc
spec.loader.exec_module(ahc)

NOW = datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc)

_CLEAN = {
    "settings_parse_ok": True, "install_method": "npm-global", "duplicate_installs": 0,
    "broken_agents": 0, "version_current": True, "auto_mode_default": True,
    "unused_skills": 3, "unused_plugins": 0,
}


def _facts(**over):
    d = dict(_CLEAN)
    d.update(over)
    return d


# ── pure verdict: checkup_category ────────────────────────────────────────────────────────────────
def test_clean_is_ok():
    assert ahc.checkup_category(_facts()) == "CHECKUP-OK"


def test_missing_settings_evidence():
    assert ahc.checkup_category(_facts(settings_parse_ok=None)) == "MISSING-EVIDENCE"


def test_missing_install_evidence():
    assert ahc.checkup_category(_facts(install_method=None)) == "MISSING-EVIDENCE"


def test_broken_on_settings_parse_fail():
    assert ahc.checkup_category(_facts(settings_parse_ok=False)) == "CHECKUP-BROKEN"


def test_broken_on_duplicate_install():
    assert ahc.checkup_category(_facts(duplicate_installs=1)) == "CHECKUP-BROKEN"


def test_broken_on_broken_agents():
    assert ahc.checkup_category(_facts(broken_agents=2)) == "CHECKUP-BROKEN"


def test_drifted_on_behind_version():
    assert ahc.checkup_category(_facts(version_current=False)) == "CHECKUP-DRIFTED"


def test_drifted_on_non_auto_default():
    assert ahc.checkup_category(_facts(auto_mode_default=False)) == "CHECKUP-DRIFTED"


def test_drifted_on_skill_clutter_over_threshold():
    assert ahc.checkup_category(_facts(unused_skills=16)) == "CHECKUP-DRIFTED"


def test_clutter_at_threshold_is_ok():
    assert ahc.checkup_category(_facts(unused_skills=15)) == "CHECKUP-OK"


def test_drifted_on_unused_plugins():
    assert ahc.checkup_category(_facts(unused_plugins=1)) == "CHECKUP-DRIFTED"


def test_unknown_version_current_is_not_drift():
    # network unavailable ⇒ version_current None ⇒ must NOT be penalised
    assert ahc.checkup_category(_facts(version_current=None)) == "CHECKUP-OK"


def test_broken_beats_drifted():
    # a box that is BOTH behind and has broken settings grades red, not amber
    assert ahc.checkup_category(_facts(settings_parse_ok=False, version_current=False)) == "CHECKUP-BROKEN"


# ── _semver_ge ────────────────────────────────────────────────────────────────────────────────────
def test_semver_equal_is_ge():
    assert ahc._semver_ge("2.1.205", "2.1.205") is True


def test_semver_behind():
    assert ahc._semver_ge("2.1.204", "2.1.205") is False


def test_semver_ahead_prerelease_ignores_build():
    assert ahc._semver_ge("2.1.205+abc123", "2.1.205") is True


# ── fact assembly (audit) with monkeypatched collectors ───────────────────────────────────────────
def _patch(monkeypatch, *, version="2.1.205", install="npm-global", latest="2.1.205",
           dup=0, sok=True, bad=0, uskill=3, uplug=0, mode="auto"):
    monkeypatch.setattr(ahc, "_fingerprint_version_install", lambda: (version, install))
    monkeypatch.setattr(ahc, "_latest_version", lambda _i: latest)
    monkeypatch.setattr(ahc, "_duplicate_installs", lambda: dup)
    monkeypatch.setattr(ahc, "_settings_parse_ok", lambda: sok)
    monkeypatch.setattr(ahc, "_broken_agents", lambda: bad)
    monkeypatch.setattr(ahc, "_unused_counts", lambda: (uskill, uplug))
    monkeypatch.setattr(ahc, "_default_mode", lambda: mode)


def test_audit_reads_fingerprint_version(monkeypatch):
    _patch(monkeypatch)
    f = ahc.audit(machine="test-box", now=NOW)
    assert f["cc_version"] == "2.1.205"
    assert f["install_method"] == "npm-global"
    assert f["checkup"] == "CHECKUP-OK"


def test_audit_version_current_true(monkeypatch):
    _patch(monkeypatch, version="2.1.205", latest="2.1.205")
    assert ahc.audit(machine="b", now=NOW)["version_current"] is True


def test_audit_version_behind(monkeypatch):
    _patch(monkeypatch, version="2.1.200", latest="2.1.205")
    f = ahc.audit(machine="b", now=NOW)
    assert f["version_current"] is False and f["checkup"] == "CHECKUP-DRIFTED"


def test_audit_no_network_path(monkeypatch):
    _patch(monkeypatch, latest=None)              # essential-traffic / offline
    f = ahc.audit(machine="b", now=NOW)
    assert f["cc_latest"] is None
    assert f["version_current"] is None
    assert f["checkup"] == "CHECKUP-OK"           # unknown currency is not drift


def test_audit_settings_parse_fail_is_broken(monkeypatch):
    _patch(monkeypatch, sok=False)
    assert ahc.audit(machine="b", now=NOW)["checkup"] == "CHECKUP-BROKEN"


def test_audit_broken_agent_collision(monkeypatch):
    _patch(monkeypatch, bad=1)
    f = ahc.audit(machine="b", now=NOW)
    assert f["broken_agents"] == 1 and f["checkup"] == "CHECKUP-BROKEN"


def test_audit_malformed_fingerprint_fails_closed(monkeypatch):
    # fingerprint absent/garbled ⇒ version/install None ⇒ install_method None ⇒ MISSING-EVIDENCE,
    # but the audit still returns a well-formed state (never crashes).
    _patch(monkeypatch, version=None, install=None, latest=None)
    f = ahc.audit(machine="b", now=NOW)
    assert f["cc_version"] is None and f["install_method"] is None
    assert f["checkup"] == "MISSING-EVIDENCE"


def test_audit_allowlist_safe(monkeypatch):
    # every emitted value must be a JSON scalar (str/int/bool/None) — no paths, dicts, lists, tokens.
    _patch(monkeypatch)
    f = ahc.audit(machine="test-box", now=NOW)
    expected_keys = {
        "machine", "audited_at", "schema_version", "cc_version", "cc_latest", "version_current",
        "install_method", "duplicate_installs", "settings_parse_ok", "broken_agents",
        "unused_skills", "unused_plugins", "default_mode", "auto_mode_default", "checkup",
    }
    assert set(f.keys()) == expected_keys
    for k, v in f.items():
        assert isinstance(v, (str, int, bool, type(None))), f"{k} leaked non-scalar {type(v)}"
    # no string fact may look like an absolute path (allowlist forbids path leakage)
    for k, v in f.items():
        if isinstance(v, str):
            assert not v.startswith("/"), f"{k} leaked an absolute path"


def test_audit_stamps_machine_and_time(monkeypatch):
    _patch(monkeypatch)
    f = ahc.audit(machine="dev-secondary", now=NOW)
    assert f["machine"] == "dev-secondary"
    assert f["audited_at"] == "2026-07-09T12:00:00+00:00"
    assert f["schema_version"] == 1
