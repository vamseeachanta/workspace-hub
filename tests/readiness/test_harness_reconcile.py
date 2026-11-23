"""TDD for #2968 (F1) — role-overlay harness reconciler.

Pure-core tests (dict in / dict out) using fixtures, plus the array-merge and
live-gating semantics added per Codex r1 MAJOR. No network / no real registry.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "scripts" / "readiness" / "harness_reconcile.py"
spec = importlib.util.spec_from_file_location("harness_reconcile", MOD)
hr = importlib.util.module_from_spec(spec)
sys.modules["harness_reconcile"] = hr
spec.loader.exec_module(hr)


# ── fixtures ──────────────────────────────────────────────────────────────────
ROLES = {
    "roles": {
        "_base": {
            "deny_required": ["Bash(rm -rf /)", "Bash(sudo:*)"],
            "hooks_required": {"Stop": [{"hooks": [{"type": "command", "command": "x.py"}]}]},
            "skill_families": ["core"],
        },
        "control-plane": {"scalar_required": {"effortLevel": "high"},
                          "skill_families": ["coordination"]},
        "comms-dispatch": {"skill_families": ["deckhand"]},
        "sim-worker": {"skill_families": ["engineering-sim"]},
    }
}


# ── role composition (Q1) ─────────────────────────────────────────────────────
def test_compose_union_two_roles():
    ov = hr.compose_overlay(ROLES, ["comms-dispatch", "sim-worker"])
    assert set(ov["skill_families"]) == {"core", "deckhand", "engineering-sim"}


def test_base_applies_to_all_managed():
    ov = hr.compose_overlay(ROLES, ["comms-dispatch"])
    assert "Bash(sudo:*)" in ov["deny_required"]
    assert "Stop" in ov["hooks_required"]


def test_overlay_conflict_fails_closed():
    roles = {"roles": {"_base": {"scalar_required": {"effortLevel": "high"}},
                       "a": {"scalar_required": {"effortLevel": "low"}}}}
    with pytest.raises(hr.ReconcileError):
        hr.compose_overlay(roles, ["a"])


def test_unknown_role_fails_closed():
    with pytest.raises(hr.ReconcileError):
        hr.compose_overlay(ROLES, ["nope"])


# ── managed gate (Q2) ─────────────────────────────────────────────────────────
def test_managed_false_skips():
    assert hr.is_managed({"managed": False, "roles": ["licensed-solver"]}) is False
    assert hr.is_managed(None) is False
    assert hr.is_managed({"managed": True, "roles": ["control-plane"]}) is True


# ── deny array semantics (Codex MAJOR #2) ────────────────────────────────────
def test_deny_union_dedup_sorted():
    out = hr.merge_deny(["Bash(z)", "Bash(sudo:*)"], ["Bash(sudo:*)", "Bash(rm -rf /)"])
    assert out == sorted(set(out))            # sorted, deduped
    assert out.count("Bash(sudo:*)") == 1
    assert "Bash(z)" in out                    # local never dropped


# ── hook array semantics (Codex MAJOR #2/#3) ─────────────────────────────────
def test_hooks_union_by_identity():
    local = {"Stop": [{"hooks": [{"type": "command", "command": "x.py"}]}]}
    req = {"Stop": [{"hooks": [{"type": "command", "command": "x.py"}]}]}
    merged = hr.merge_hooks(local, req)
    flat = [h for g in merged["Stop"] for h in g["hooks"]]
    assert len(flat) == 1                       # deduped by (event,type,command)


def test_hooks_conflict_fails_closed():
    local = {"Stop": [{"hooks": [{"type": "command", "command": "x.py", "timeout": 10}]}]}
    req = {"Stop": [{"hooks": [{"type": "command", "command": "x.py", "timeout": 45}]}]}
    with pytest.raises(hr.ReconcileError):
        hr.merge_hooks(local, req)


def test_hooks_preserve_local_only():
    local = {"Stop": [{"hooks": [{"type": "command", "command": "local.py"}]}]}
    req = {"Stop": [{"hooks": [{"type": "command", "command": "req.py"}]}]}
    merged = hr.merge_hooks(local, req)
    cmds = {h["command"] for g in merged["Stop"] for h in g["hooks"]}
    assert cmds == {"local.py", "req.py"}       # local preserved, required added


# ── drift + apply ─────────────────────────────────────────────────────────────
def test_apply_is_additive_preserves_unknown():
    overlay = hr.compose_overlay(ROLES, ["control-plane"])
    current = {"theme": "dark", "permissions": {"deny": ["Bash(custom)"]}}
    new = hr.apply_overlay(current, overlay)
    assert new["theme"] == "dark"               # unknown key preserved
    assert "Bash(custom)" in new["permissions"]["deny"]   # local deny preserved
    assert "Bash(sudo:*)" in new["permissions"]["deny"]   # required added
    assert new["effortLevel"] == "high"


def test_apply_byte_identical_on_rerun():
    overlay = hr.compose_overlay(ROLES, ["control-plane"])
    current = {"theme": "light"}
    once = hr.apply_overlay(current, overlay)
    twice = hr.apply_overlay(once, overlay)
    assert hr.serialize(once) == hr.serialize(twice)   # idempotent, byte-stable


def test_dry_run_reports_drift_for_empty_settings():
    overlay = hr.compose_overlay(ROLES, ["control-plane"])
    drift = hr.compute_drift({}, overlay)
    keys = {d["key"] for d in drift}
    assert "permissions.deny" in keys and "hooks" in keys and "effortLevel" in keys


# ── uncataloged-live (Codex MAJOR #6 / blast-radius) ─────────────────────────
def test_uncataloged_live_blocks_apply():
    current = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "mystery.py"}]}]}}
    classes = {"hooks_known": [{"event": "Stop", "type": "command", "command": "x.py"}]}
    flagged = hr.find_uncataloged_live(current, classes)
    assert flagged and "mystery.py" in flagged[0]


def test_cataloged_hook_not_flagged():
    current = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "x.py"}]}]}}
    classes = {"hooks_known": [{"event": "Stop", "type": "command", "command": "x.py"}]}
    assert hr.find_uncataloged_live(current, classes) == []


# ── live-session gating (Codex MAJOR #1) ─────────────────────────────────────
def test_apply_refuses_on_live_daemon():
    # daemons active + hook change + not allowed → block
    assert hr.should_block_apply(True, True, False) is True
    # explicit override → allowed
    assert hr.should_block_apply(True, True, True) is False
    # no hook change → allowed even if live
    assert hr.should_block_apply(True, False, False) is False
    # no daemons → allowed
    assert hr.should_block_apply(False, True, False) is False


def test_detect_live_daemons_injectable():
    daemons = hr.detect_live_daemons(pgrep_fn=lambda pat: "deckhand" in pat)
    assert daemons == ["deckhand"]


# ── CLI dry-run writes nothing (Codex MAJOR #4) ──────────────────────────────
def test_cli_managed_false_writes_nothing(tmp_path, monkeypatch):
    # minimal registry with a managed:false host → exits 0, no write
    reg = {"machines": {"win1": {"hostname": "win1", "harness_profile":
           {"roles": ["licensed-solver"], "managed": False}}}}
    monkeypatch.setattr(hr, "_load_yaml", lambda p: reg if "registry" in str(p)
                        else (ROLES if "roles" in str(p) else {}))
    settings = tmp_path / "settings.json"
    monkeypatch.setattr(hr, "SETTINGS", settings)
    rc = hr.main(["--apply", "--machine", "win1"])
    assert rc == 0
    assert not settings.exists()                # never wrote
    assert not (tmp_path / "settings.json.bak").exists()
