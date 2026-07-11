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


# ── code-review MAJOR fixes (#2969 round 2) ──────────────────────────────────
def test_read_crontab_fails_closed_on_error(monkeypatch):
    # a REAL crontab -l error (not "no crontab") must raise, never return "" (#2 fix)
    class R:
        returncode = 1
        stdout = ""
        stderr = "crontab: permission denied"
    raised = False
    try:
        ca.read_crontab(_run=lambda *a, **k: R())
    except ca.CronReadError:
        raised = True
    assert raised   # must raise rather than silently yield empty


def test_read_crontab_empty_when_no_crontab(monkeypatch):
    class R:
        returncode = 1
        stdout = ""
        stderr = "no crontab for vamsee"
    assert ca.read_crontab(_run=lambda *a, **k: R()) == ""


def test_flock_is_real():
    # the lock context manager actually exists and acquires a lock (no exception)
    import tempfile, os
    p = Path(tempfile.mkdtemp()) / "lock"
    with ca._flock(p):
        assert p.exists()


def test_external_with_catalog_substring_preserved(monkeypatch, tmp_path):
    # a deckhand line that ALSO contains a catalog script path must be PRESERVED, not
    # pulled into the managed block (#1 classify ordering fix)
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    line = ("30 7 * * * cd /mnt/local-analysis/deckhand && python3 "
            "scripts/deckhand/member-audit-cron.py; scripts/x.sh >> /dev/null 2>&1")
    state = {"crontab": line + "\n"}
    _patch_configs(monkeypatch,
                   [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
                   ["control-plane"],
                   [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}])
    res = ca.run_cutover("m1", apply=True, ts="t",
                         _read=lambda: state["crontab"], _write=lambda t: state.update(crontab=t),
                         _daemons=lambda pat: False)
    assert res["status"] == "applied"
    assert line in state["crontab"]              # external line survived despite catalog substring


def _patch_configs(monkeypatch, tasks, roles, ext_fps, registry=None):
    if registry is None:
        registry = {"machines": {"m1": {"hostname": "m1", "harness_profile": {"roles": roles}}}}
    monkeypatch.setattr(ca, "_load", lambda p: (
        {"tasks": tasks} if "schedule-tasks" in str(p)
        else {"preserved_external": [
            fp if "fingerprint" in fp else {"fingerprint": fp} for fp in ext_fps
        ]} if "state-classes" in str(p)
        else registry))


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


def test_cron_apply_resolves_hostname_alias_before_role_selection(monkeypatch):
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "schedule_variant": "full",
                "harness_profile": {"roles": ["control-plane"]},
            }
        }
    }
    _patch_configs(
        monkeypatch,
        [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
        ["control-plane"],
        [],
        registry=registry,
    )
    res = ca.run_cutover("vamsee-linux1", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    assert res["machine"] == "dev-primary"
    assert res["selected"] == ["a"]


def test_cron_apply_alias_apply_uses_canonical_backup_name(monkeypatch, tmp_path):
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "schedule_variant": "full",
                "harness_profile": {"roles": ["control-plane"]},
            }
        }
    }
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    state = {"crontab": ""}
    _patch_configs(
        monkeypatch,
        [{"id": "a", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"]}],
        ["control-plane"],
        [],
        registry=registry,
    )

    res = ca.run_cutover(
        "vamsee-linux1",
        apply=True,
        ts="alias",
        _read=lambda: state["crontab"],
        _write=lambda txt: state.update(crontab=txt),
        _daemons=lambda pat: False,
    )

    assert res["status"] == "applied"
    assert res["machine"] == "dev-primary"
    assert res["backup"].endswith("dev-primary-alias.crontab")


def test_cron_apply_selects_machine_pinned_tasks_for_hostname_tokens(monkeypatch):
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "schedule_variant": "full",
                "harness_profile": {"roles": []},
            }
        }
    }
    _patch_configs(
        monkeypatch,
        [{"id": "machine-only", "schedule": "0 1 * * *", "command": "scripts/x.sh", "machines": ["ace-linux-1"]}],
        [],
        [],
        registry=registry,
    )
    res = ca.run_cutover("dev-primary", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    assert res["selected"] == ["machine-only"]


def test_cron_apply_does_not_select_machine_excluded_role_matches(monkeypatch):
    _patch_configs(
        monkeypatch,
        [{"id": "excluded", "schedule": "0 1 * * *", "command": "scripts/x.sh", "roles": ["control-plane"], "machines": ["other-host"]}],
        ["control-plane"],
        [],
    )
    res = ca.run_cutover("m1", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    assert res["selected"] == []
    assert res["conflicts"]


def test_cron_apply_filters_non_cron_schedulers_before_role_selection(monkeypatch):
    _patch_configs(
        monkeypatch,
        [
            {
                "id": "windows-only",
                "schedule": "daily 04:40",
                "scheduler": "windows-task-scheduler",
                "command": "bash.exe -c echo hi",
                "roles": ["control-plane"],
                "machines": ["m1"],
            }
        ],
        ["control-plane"],
        [],
    )
    res = ca.run_cutover("m1", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    assert res["selected"] == []


def test_run_cutover_renders_applied_new_text_without_unresolved_workspace_placeholders(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    state = {"crontab": ""}
    _patch_configs(
        monkeypatch,
        [
            {
                "id": "repo-sync",
                "schedule": "0 */4 * * *",
                "command": "cd $WORKSPACE_HUB && bash scripts/cron-repository-sync.sh >> $LOG 2>&1",
                "roles": ["control-plane"],
            }
        ],
        ["control-plane"],
        [],
    )
    res = ca.run_cutover(
        "m1",
        apply=True,
        ts="t",
        _read=lambda: state["crontab"],
        _write=lambda txt: state.update(crontab=txt),
        _daemons=lambda pat: False,
    )
    assert res["status"] == "applied"
    assert "$WORKSPACE_HUB" not in state["crontab"]
    assert "$LOG" not in state["crontab"]
    assert str(REPO) in state["crontab"]
    assert "/tmp/workspace-hub-cron.log" in state["crontab"]


def test_run_cutover_second_pass_is_idempotent_after_expansion(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    state = {"crontab": ""}
    _patch_configs(
        monkeypatch,
        [
            {
                "id": "repo-sync",
                "schedule": "0 */4 * * *",
                "command": "cd $WORKSPACE_HUB && bash scripts/cron-repository-sync.sh >> $LOG 2>&1",
                "roles": ["control-plane"],
            }
        ],
        ["control-plane"],
        [],
    )

    first = ca.run_cutover(
        "m1",
        apply=True,
        ts="first",
        _read=lambda: state["crontab"],
        _write=lambda txt: state.update(crontab=txt),
        _daemons=lambda pat: False,
    )
    after_first = state["crontab"]
    second = ca.run_cutover(
        "m1",
        apply=True,
        ts="second",
        _read=lambda: state["crontab"],
        _write=lambda txt: state.update(crontab=txt),
        _daemons=lambda pat: False,
    )
    assert first["status"] == "applied"
    assert second["status"] == "applied"
    assert state["crontab"] == after_first
    assert "$WORKSPACE_HUB" not in state["crontab"]


def test_json_dry_run_includes_actual_rendered_new_text(monkeypatch):
    _patch_configs(
        monkeypatch,
        [
            {
                "id": "repo-sync",
                "schedule": "0 */4 * * *",
                "command": "cd $WORKSPACE_HUB && bash scripts/cron-repository-sync.sh >> $LOG 2>&1",
                "roles": ["control-plane"],
            }
        ],
        ["control-plane"],
        [],
    )
    res = ca.run_cutover("m1", apply=False, ts="t", _read=lambda: "")
    encoded = __import__("json").loads(__import__("json").dumps(res))
    assert encoded["status"] == "dry-run"
    assert "new_text" in encoded
    assert "scripts/cron-repository-sync.sh" in encoded["new_text"]
    assert "$WORKSPACE_HUB" not in encoded["new_text"]


def test_real_dev_primary_cutover_selects_ace_linux_1_machine_pinned_tasks():
    res = ca.run_cutover("dev-primary", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    assert "solver-watch-results" in res["selected"]
    assert "solver-dashboard" in res["selected"]
    assert "scripts/solver/watch-results.sh" in res["new_text"]
    assert "scripts/cron/solver-dashboard-daily.sh" in res["new_text"]


def test_real_dev_primary_cutover_keeps_bridge_schedule_staggers():
    res = ca.run_cutover("dev-primary", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    lines = res["new_text"].splitlines()
    provider = next(line for line in lines if "bridge-providers-to-dream.sh" in line)
    hermes = next(line for line in lines if "bridge-hermes-claude.sh" in line)
    assert provider.startswith("5 4 * * * ")
    assert hermes.startswith("25 4 * * * ")


def test_real_cutover_replaces_stale_bridge_only_via_explicit_fingerprint():
    stale = (
        "25 4 * * * cd /mnt/local-analysis/workspace-hub && "  # abs-path-allowed
        "bash scripts/memory/bridge-hermes-claude.sh\n"
    )

    result = ca.run_cutover(
        "dev-primary", apply=False, ts="t", _read=lambda: stale
    )

    assert result["status"] == "dry-run"
    assert stale.strip() not in result["new_text"].splitlines()
    bridge = next(
        line for line in result["new_text"].splitlines()
        if "scripts/memory/bridge-hermes-claude.sh" in line
    )
    assert "--commit" in bridge


def test_fingerprinted_catalog_tasks_are_excluded_from_substring_keys():
    catalog = ca._load(ca.CATALOG)
    registry = ca._load(ca.REGISTRY)
    keys = ca.catalog_commands(catalog, registry=registry, machine_id="dev-primary")
    fingerprints = ca.catalog_fingerprints(catalog["tasks"])

    assert "scripts/memory/bridge-hermes-claude.sh" not in keys
    assert "scripts/cron-repository-sync.sh" not in keys
    assert {entry["catalog_task_id"] for entry in fingerprints} >= {
        "hermes-claude-bridge",
        "repository-sync",
    }


def test_real_dev_secondary_preview_does_not_use_ace_linux_1_bridge_staggers():
    res = ca.run_cutover("dev-secondary", apply=False, ts="t", _read=lambda: "")
    assert res["status"] == "dry-run"
    lines = res["new_text"].splitlines()
    provider = next(line for line in lines if "bridge-providers-to-dream.sh" in line)
    hermes = next(line for line in lines if "bridge-hermes-claude.sh" in line)
    assert provider.startswith("15 4 * * * ")
    assert hermes.startswith("35 4 * * * ")


def test_real_linux_cutover_filters_named_windows_scheduler_tasks_and_dev_secondary_solver_pins():
    primary = ca.run_cutover("dev-primary", apply=False, ts="t", _read=lambda: "")
    secondary = ca.run_cutover("dev-secondary", apply=False, ts="t", _read=lambda: "")
    windows_task_ids = {
        "provider-dream-bridge-win",
        "hermes-claude-bridge-win",
        "win-repository-sync",
        "win-session-state-commit",
    }

    assert primary["status"] == "dry-run"
    assert secondary["status"] == "dry-run"
    assert windows_task_ids.isdisjoint(primary["selected"])
    assert windows_task_ids.isdisjoint(secondary["selected"])
    assert "solver-watch-results" not in secondary["selected"]
    assert "solver-dashboard" not in secondary["selected"]
