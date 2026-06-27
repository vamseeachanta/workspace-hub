"""TDD tests for #3255 — the memory-freshness audit engine (epic #3248).

Targets scripts/curation/audit_memory_freshness.py: the pure verdict tiers (freshness_category /
categorize) and the audit() fact-emitter. The git `git log` runner (`_git_commit_iso`) is
monkeypatched everywhere so the suite never depends on real repo history; one regression test
proves the bridged surfaces take their clock from the git commit time, NOT file mtime.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "curation" / "audit_memory_freshness.py"

spec = importlib.util.spec_from_file_location("audit_memory_freshness", MODULE_PATH)
assert spec is not None and spec.loader is not None
amf = importlib.util.module_from_spec(spec)
sys.modules["audit_memory_freshness"] = amf
spec.loader.exec_module(amf)

NOW = datetime(2026, 6, 26, 12, 0, 0, tzinfo=timezone.utc)


def _iso_ago(hours: float) -> str:
    return (NOW - timedelta(hours=hours)).isoformat(timespec="seconds")


# ── pure verdict: freshness_category (single worst age) ──────────────────────────────────────────
def test_fresh_at_1h():
    assert amf.freshness_category(1) == "MEMORY-FRESH"


def test_fresh_at_exactly_36h_boundary_inclusive():
    assert amf.freshness_category(36) == "MEMORY-FRESH"


def test_stale_at_36_5h():
    assert amf.freshness_category(36.5) == "MEMORY-STALE"


def test_stale_at_exactly_72h_boundary_inclusive():
    assert amf.freshness_category(72) == "MEMORY-STALE"


def test_expired_at_73h():
    assert amf.freshness_category(73) == "MEMORY-EXPIRED"


def test_category_none_is_missing_evidence():
    assert amf.freshness_category(None) == "MISSING-EVIDENCE"


def test_category_negative_is_missing_evidence():
    assert amf.freshness_category(-3) == "MISSING-EVIDENCE"


# ── pure verdict: categorize (list of present ages) ──────────────────────────────────────────────
def test_worst_surface_dominates():
    # one fresh (1h) + one expired (80h) ⇒ the oldest drives the verdict
    assert amf.categorize([1, 80]) == "MEMORY-EXPIRED"


def test_absent_surface_ignored():
    # only the present surface (1h) is in the list ⇒ fresh
    assert amf.categorize([1]) == "MEMORY-FRESH"


def test_missing_evidence_no_present_surface():
    assert amf.categorize([]) == "MISSING-EVIDENCE"


def test_missing_evidence_future_stamp_failclosed():
    # a future stamp anywhere (clock skew) fails the whole verdict closed
    assert amf.categorize([1, -3, 50]) == "MISSING-EVIDENCE"


def test_categorize_ignores_non_numeric():
    assert amf.categorize([None, "x"]) == "MISSING-EVIDENCE"


# ── audit() fact-emitter (git runner monkeypatched) ──────────────────────────────────────────────
def _patch_git(monkeypatch, mapping):
    """mapping: {rel_path: iso|None}; unmapped paths return None (fail-closed)."""
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: mapping.get(rel))


def test_audit_all_git_surfaces_fresh(monkeypatch, tmp_path):
    mapping = {rel: _iso_ago(2) for rel in amf.GIT_SURFACES.values()}
    _patch_git(monkeypatch, mapping)
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")  # absent hermes
    state = amf.audit(machine="dev-primary", now=NOW)
    assert state["machine"] == "dev-primary"
    assert state["freshness"] == "MEMORY-FRESH"
    assert state["surfaces"]["context_md"]["present"] is True
    assert state["surfaces"]["context_md"]["signal"] == "git-commit"
    assert abs(state["surfaces"]["context_md"]["age_hours"] - 2.0) < 1e-6
    assert state["surfaces"]["hermes_memories"]["present"] is False
    assert state["worst_age_hours"] is not None


def test_audit_worst_surface_drives_freshness(monkeypatch, tmp_path):
    mapping = {
        ".claude/memory/context.md": _iso_ago(1),
        ".claude/memory/agents.md": _iso_ago(1),
        "config/agents/codex/MEMORY.runtime.md": _iso_ago(1),
        "config/agents/gemini/MEMORY.runtime.md": _iso_ago(80),  # stale provider runtime
    }
    _patch_git(monkeypatch, mapping)
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    state = amf.audit(machine="m", now=NOW)
    assert state["freshness"] == "MEMORY-EXPIRED"
    assert abs(state["worst_age_hours"] - 80.0) < 1e-6
    # newest_refresh is the most-recently refreshed present surface (the 1h ones)
    assert state["newest_refresh"] == _iso_ago(1)


def test_audit_git_unavailable_failcloses(monkeypatch, tmp_path):
    # git missing / not-a-repo ⇒ runner returns None ⇒ every bridged surface absent
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: None)
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    state = amf.audit(machine="m", now=NOW)
    for key in amf.GIT_SURFACES:
        assert state["surfaces"][key]["present"] is False
    assert state["freshness"] == "MISSING-EVIDENCE"
    assert state["worst_age_hours"] is None


def test_audit_bridged_surface_uses_git_commit_not_mtime(monkeypatch, tmp_path):
    """CORE must-fix #1: the freshness clock for a git-bridged surface is the git COMMIT time,
    immune to a freshly-bumped file mtime. We feed an OLD commit iso through the runner; the audit
    must report exactly that old stamp (signal git-commit), never a 'now' mtime."""
    old = _iso_ago(100)
    _patch_git(monkeypatch, {rel: old for rel in amf.GIT_SURFACES.values()})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    state = amf.audit(machine="m", now=NOW)
    rec = state["surfaces"]["context_md"]
    assert rec["refreshed_at"] == old
    assert rec["signal"] == "git-commit"
    assert state["freshness"] == "MEMORY-EXPIRED"  # 100h > 72h, NOT fresh-from-mtime


def test_audit_hermes_surface_uses_local_mtime(monkeypatch, tmp_path):
    # local (non-git) surface: freshness clock = real file mtime
    hdir = tmp_path / "hermes"
    hdir.mkdir()
    f = hdir / "MEMORY.md"
    f.write_text("x")
    target = NOW - timedelta(hours=5)
    import os
    os.utime(f, (target.timestamp(), target.timestamp()))
    monkeypatch.setattr(amf, "HERMES_DIR", hdir)
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: None)  # isolate hermes
    state = amf.audit(machine="m", now=NOW)
    rec = state["surfaces"]["hermes_memories"]
    assert rec["present"] is True
    assert rec["signal"] == "file-mtime"
    assert abs(rec["age_hours"] - 5.0) < 0.01
    assert state["freshness"] == "MEMORY-FRESH"


def test_audit_hermes_absent_marked(monkeypatch, tmp_path):
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "absent")
    _patch_git(monkeypatch, {rel: _iso_ago(1) for rel in amf.GIT_SURFACES.values()})
    state = amf.audit(machine="m", now=NOW)
    assert state["surfaces"]["hermes_memories"]["present"] is False


def test_audit_machine_label_reused(monkeypatch, tmp_path):
    # machine label comes from audit_skill_currency.machine_label, not a re-impl
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "curation"))
    import audit_skill_currency
    monkeypatch.setattr(audit_skill_currency, "machine_label", lambda: "fake-box")
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: None)
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    state = amf.audit(now=NOW)  # machine=None ⇒ derives via reused label
    assert state["machine"] == "fake-box"


def test_audit_emits_no_abs_paths_and_iso_stamps(monkeypatch, tmp_path):
    _patch_git(monkeypatch, {rel: _iso_ago(3) for rel in amf.GIT_SURFACES.values()})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    state = amf.audit(machine="m", now=NOW)
    blob = json.dumps(state)
    assert "/mnt/" not in blob and str(REPO_ROOT) not in blob  # abs-path-allowed
    # every present surface's refreshed_at parses as ISO
    for s in state["surfaces"].values():
        if s["present"]:
            assert amf._parse_iso(s["refreshed_at"]) is not None
    assert state["schema_version"] == 1


def test_audit_writes_state_file(monkeypatch, tmp_path):
    _patch_git(monkeypatch, {rel: _iso_ago(1) for rel in amf.GIT_SURFACES.values()})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    monkeypatch.setattr(amf, "STATE", tmp_path / "state")
    monkeypatch.setattr(amf, "_now", lambda: NOW)
    rc = amf.main(["--machine", "boxx"])
    assert rc == 0
    out = tmp_path / "state" / "memory-freshness-boxx.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["machine"] == "boxx"
    assert data["freshness"] == "MEMORY-FRESH"


def test_thresholds_documented_constants():
    assert amf.MEMORY_STALE_H == 36
    assert amf.MEMORY_EXPIRED_H == 72
