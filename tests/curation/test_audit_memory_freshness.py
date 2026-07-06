"""TDD tests for #3255 + #3384 — the memory-freshness audit engine (epic #3248).

Targets scripts/curation/audit_memory_freshness.py.

#3384 change: freshness is clocked by the daily BRIDGE HEARTBEAT (a committed liveness marker),
not by the deterministic/byte-invariant content surfaces. The four content surfaces
(context.md / agents.md / codex+gemini slices) are graded by FILESYSTEM PRESENCE (exists + non-empty)
so a deleted/clobbered surface is caught — git-commit-history presence would report a deleted path as
still-present via its last commit. `_git_commit_iso` is monkeypatched so the suite never depends on
real repo history; presence is exercised against a temp `amf.REPO`.
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
    assert amf.categorize([1, 80]) == "MEMORY-EXPIRED"


def test_absent_surface_ignored():
    assert amf.categorize([1]) == "MEMORY-FRESH"


def test_missing_evidence_no_present_surface():
    assert amf.categorize([]) == "MISSING-EVIDENCE"


def test_missing_evidence_future_stamp_failclosed():
    assert amf.categorize([1, -3, 50]) == "MISSING-EVIDENCE"


def test_categorize_ignores_non_numeric():
    assert amf.categorize([None, "x"]) == "MISSING-EVIDENCE"


# ── #3384 surface topology ───────────────────────────────────────────────────────────────────────
def test_heartbeat_is_the_recency_git_surface():
    # THE liveness clock is the bridge heartbeat, not the byte-invariant content surfaces.
    assert amf.RECENCY_GIT_SURFACES == {
        "bridge_heartbeat": ".claude/state/memory-bridge-heartbeat.json"
    }


def test_content_surfaces_are_presence_only():
    # context.md / agents.md / slices are graded present/absent, NOT recency-clocked.
    assert set(amf.PRESENCE_SURFACES) == {
        "context_md", "agents_md", "codex_runtime", "gemini_runtime"
    }
    assert amf.PRESENCE_SURFACES["context_md"] == ".claude/memory/context.md"
    assert amf.PRESENCE_SURFACES["codex_runtime"] == "config/agents/codex/MEMORY.runtime.md"


# ── audit() fact-emitter (git runner monkeypatched; presence against temp REPO) ──────────────────
def _patch_git(monkeypatch, mapping):
    """mapping: {rel_path: iso|None}; unmapped ⇒ None (fail-closed)."""
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: mapping.get(rel))


def _make_presence(monkeypatch, repo: Path, present=True):
    """Create (or omit) the 4 presence content surfaces under a temp REPO."""
    monkeypatch.setattr(amf, "REPO", repo)
    if present:
        for rel in amf.PRESENCE_SURFACES.values():
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("content\n")


def test_audit_fresh_from_heartbeat(monkeypatch, tmp_path):
    # heartbeat 2h old, content present ⇒ FRESH (content byte-age is irrelevant now)
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(2)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="dev-primary", now=NOW)
    assert state["freshness"] == "MEMORY-FRESH"
    hb = state["surfaces"]["bridge_heartbeat"]
    assert hb["present"] is True and hb["signal"] == "git-commit"
    assert abs(hb["age_hours"] - 2.0) < 1e-6
    # content surfaces are present but presence-signalled (not recency)
    assert state["surfaces"]["context_md"]["present"] is True
    assert state["surfaces"]["context_md"]["signal"] == "presence"
    assert state["surfaces"]["context_md"]["age_hours"] is None


def test_audit_expired_dead_heartbeat(monkeypatch, tmp_path):
    # heartbeat 80h old ⇒ EXPIRED even though content is present (bridge dead)
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(80)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    assert state["freshness"] == "MEMORY-EXPIRED"
    assert abs(state["worst_age_hours"] - 80.0) < 1e-6


def test_audit_content_byte_age_does_not_starve_clock(monkeypatch, tmp_path):
    """#3384 core: a byte-invariant content surface committed 200h ago must NOT drive EXPIRED —
    only the heartbeat (fresh) + hermes clock freshness."""
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(3)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    assert state["freshness"] == "MEMORY-FRESH"  # heartbeat 3h wins; content age irrelevant


def test_audit_missing_on_deleted_content_surface(monkeypatch, tmp_path):
    """r2 Finding 2: a content surface that EXISTED then was DELETED must read MISSING-EVIDENCE.
    Filesystem presence catches this; git-log-history would not."""
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(2)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    (tmp_path / amf.PRESENCE_SURFACES["context_md"]).unlink()  # delete a present surface
    state = amf.audit(machine="m", now=NOW)
    assert state["surfaces"]["context_md"]["present"] is False
    assert state["freshness"] == "MISSING-EVIDENCE"


def test_audit_missing_on_empty_content_surface(monkeypatch, tmp_path):
    # a zero-byte surface is not "present" (clobbered-to-empty case)
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(2)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    (tmp_path / amf.PRESENCE_SURFACES["agents_md"]).write_text("")  # truncate
    state = amf.audit(machine="m", now=NOW)
    assert state["surfaces"]["agents_md"]["present"] is False
    assert state["freshness"] == "MISSING-EVIDENCE"


def test_audit_first_run_no_heartbeat_failcloses(monkeypatch, tmp_path):
    # before the first heartbeat commit lands: heartbeat absent, no hermes ⇒ MISSING-EVIDENCE
    _patch_git(monkeypatch, {})  # heartbeat unmapped ⇒ None
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    assert state["surfaces"]["bridge_heartbeat"]["present"] is False
    assert state["freshness"] == "MISSING-EVIDENCE"
    assert state["worst_age_hours"] is None


def test_audit_heartbeat_uses_git_commit_not_mtime(monkeypatch, tmp_path):
    old = _iso_ago(100)
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: old})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    hb = state["surfaces"]["bridge_heartbeat"]
    assert hb["refreshed_at"] == old and hb["signal"] == "git-commit"
    assert state["freshness"] == "MEMORY-EXPIRED"


def test_audit_hermes_co_signal_drives_expired(monkeypatch, tmp_path):
    # a fresh heartbeat but a genuinely-dead Hermes still trips EXPIRED (max over recency surfaces)
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(2)})
    hdir = tmp_path / "hermes"
    hdir.mkdir()
    f = hdir / "MEMORY.md"
    f.write_text("x")
    import os
    target = NOW - timedelta(hours=90)
    os.utime(f, (target.timestamp(), target.timestamp()))
    monkeypatch.setattr(amf, "HERMES_DIR", hdir)
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    assert state["surfaces"]["hermes_memories"]["signal"] == "file-mtime"
    assert state["freshness"] == "MEMORY-EXPIRED"
    assert abs(state["worst_age_hours"] - 90.0) < 0.01


def test_audit_emits_no_abs_paths_and_iso_stamps(monkeypatch, tmp_path):
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(3)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(machine="m", now=NOW)
    blob = json.dumps(state)
    assert "/mnt/" not in blob and str(REPO_ROOT) not in blob and str(tmp_path) not in blob
    for s in state["surfaces"].values():
        if s["present"] and s["refreshed_at"] is not None:
            assert amf._parse_iso(s["refreshed_at"]) is not None
    assert state["schema_version"] >= 1


def test_audit_writes_state_file(monkeypatch, tmp_path):
    _patch_git(monkeypatch, {amf.RECENCY_GIT_SURFACES["bridge_heartbeat"]: _iso_ago(1)})
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    monkeypatch.setattr(amf, "STATE", tmp_path / "state")
    monkeypatch.setattr(amf, "_now", lambda: NOW)
    rc = amf.main(["--machine", "boxx"])
    assert rc == 0
    out = tmp_path / "state" / "memory-freshness-boxx.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["machine"] == "boxx"
    assert data["freshness"] == "MEMORY-FRESH"


def test_audit_machine_label_reused(monkeypatch, tmp_path):
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "curation"))
    import audit_skill_currency
    monkeypatch.setattr(audit_skill_currency, "machine_label", lambda: "fake-box")
    monkeypatch.setattr(amf, "_git_commit_iso", lambda rel: None)
    monkeypatch.setattr(amf, "HERMES_DIR", tmp_path / "nope")
    _make_presence(monkeypatch, tmp_path, present=True)
    state = amf.audit(now=NOW)
    assert state["machine"] == "fake-box"


def test_thresholds_documented_constants():
    assert amf.MEMORY_STALE_H == 36
    assert amf.MEMORY_EXPIRED_H == 72
