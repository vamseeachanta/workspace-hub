"""TDD for cron_apply.py — transactional crontab cutover (#2969, F2).

Tests the IO transaction (dry-run safety, CAS abort, uncataloged abort, preserved-line
zero-net-removal rollback, live-daemon gate) using injected crontab read/write seams.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("cron_apply", REPO / "scripts" / "cron" / "cron_apply.py")
ca = importlib.util.module_from_spec(spec)
sys.modules["cron_apply"] = ca
spec.loader.exec_module(ca)

DECKHAND = ("30 7 * * * cd /mnt/local-analysis/deckhand && uv run --with telethon python3 "
            "scripts/deckhand/member-audit-cron.py >> $HOME/.hermes/logs/member-audit.log 2>&1")


def _patch_configs(monkeypatch, tasks, roles, ext_fps):
    monkeypatch.setattr(ca, "_load", lambda p: (
        {"tasks": tasks} if "schedule-tasks" in str(p)
        else {"preserved_external": [{"fingerprint": fp} for fp in ext_fps]} if "state-classes" in str(p)
        else {"machines": {"m1": {"hostname": "m1", "harness_profile": {"roles": roles}}}}))


def test_dry_run_writes_nothing(monkeypatch):
    writes = []
    _patch_configs(monkeypatch, [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"],
                   [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}])
    res = ca.run_cutover("m1", apply=False, ts="t", _read=lambda: DECKHAND + "\n",
                         _write=lambda txt: writes.append(txt))
    assert res["status"] == "dry-run"
    assert writes == []                      # never wrote


def test_dry_run_surfaces_uncataloged(monkeypatch):
    # dry-run over a crontab with an unknown line reports the abort (does not write)
    writes = []
    _patch_configs(monkeypatch, [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"], [])   # no fingerprints → deckhand line uncataloged
    res = ca.run_cutover("m1", apply=False, ts="t", _read=lambda: DECKHAND + "\n",
                         _write=lambda txt: writes.append(txt))
    assert res["status"] == "abort" and "uncataloged" in res["reason"].lower()
    assert writes == []


def test_uncataloged_aborts(monkeypatch):
    _patch_configs(monkeypatch, [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"], [])   # no fingerprints → deckhand line is uncataloged
    res = ca.run_cutover("m1", apply=True, ts="t", _read=lambda: DECKHAND + "\n",
                         _write=lambda txt: None, _daemons=lambda pat: False)
    assert res["status"] == "abort"
    assert "uncataloged" in res["reason"].lower()


def test_preserved_external_survives_apply(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    state = {"crontab": DECKHAND + "\n"}
    def _read(): return state["crontab"]
    def _write(txt): state["crontab"] = txt
    _patch_configs(monkeypatch,
                   [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"],
                   [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}])
    res = ca.run_cutover("m1", apply=True, ts="t", _read=_read, _write=_write, _daemons=lambda pat: False)
    assert res["status"] == "applied"
    assert DECKHAND in state["crontab"]          # deckhand line preserved verbatim
    assert "scripts/x.sh" in state["crontab"]    # catalog task installed


def test_cas_abort_on_concurrent_change(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    reads = [DECKHAND + "\n", DECKHAND + "\n# someone else added this\n"]  # changes between A and B
    _patch_configs(monkeypatch,
                   [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"],
                   [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}])
    res = ca.run_cutover("m1", apply=True, ts="t",
                         _read=lambda: reads.pop(0), _write=lambda txt: None, _daemons=lambda pat: False)
    assert res["status"] == "abort" and "CAS" in res["reason"]


def test_live_daemon_blocks_without_override(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    _patch_configs(monkeypatch,
                   [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"],
                   [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}])
    res = ca.run_cutover("m1", apply=True, ts="t", _read=lambda: DECKHAND + "\n",
                         _write=lambda txt: None, _daemons=lambda pat: "deckhand" in pat)
    assert res["status"] == "abort" and "daemon" in res["reason"].lower()


def test_skip_when_no_roles(monkeypatch):
    monkeypatch.setattr(ca, "_load", lambda p: (
        {"tasks": []} if "schedule-tasks" in str(p)
        else {} if "state-classes" in str(p)
        else {"machines": {"m1": {"hostname": "m1"}}}))   # no harness_profile
    res = ca.run_cutover("m1", apply=True, ts="t", _read=lambda: "", _write=lambda txt: None)
    assert res["status"] == "skip"
