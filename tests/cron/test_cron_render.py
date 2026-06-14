"""Tests for the shared cron renderer used by setup-cron and cron_apply."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[2]
RENDER_PATH = REPO / "scripts" / "cron" / "cron_render.py"
SCHEDULE_PATH = REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
REGISTRY_PATH = REPO / "config" / "workstations" / "registry.yaml"


def _load_renderer():
    spec = importlib.util.spec_from_file_location("cron_render", RENDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cron_render_is_leaf_module_no_cron_transaction_import():
    assert RENDER_PATH.exists(), "shared renderer module must exist"
    source = RENDER_PATH.read_text(encoding="utf-8")
    assert "cron_transaction" not in source


def test_render_task_resolves_alias_schedule_and_placeholders(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    render = _load_renderer()
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "hostname_aliases": ["vamsee-linux1"],
                "schedule_variant": "full",
            }
        }
    }
    task = {
        "id": "harness-update",
        "schedule_by_machine": {
            "ace-linux-1": "15 1 * * *",
            "dev-primary": "99 9 * * *",
        },
        "schedule": "0 0 * * *",
        "command": "cd $WORKSPACE_HUB && echo ok >> $LOG 2>&1",
    }

    context = render.build_context("vamsee-linux1", registry=registry)
    rendered = render.render_task(task, context)

    assert rendered["machine_id"] == "dev-primary"
    assert rendered["schedule"] == "15 1 * * *"
    assert rendered["line"] == (
        f"15 1 * * * cd {REPO} && echo ok >> "
        f"{REPO}/logs/quality/cron-wrapper.log 2>&1"
    )
    assert "$WORKSPACE_HUB" not in rendered["line"]
    assert "$LOG" not in rendered["line"]


def test_render_task_keeps_current_ace_linux_1_bridge_schedule_values(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    render = _load_renderer()
    catalog = yaml.safe_load(SCHEDULE_PATH.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    tasks = {task["id"]: task for task in catalog["tasks"]}
    context = render.build_context("ace-linux-1", registry=registry)

    provider = render.render_task(tasks["provider-dream-bridge"], context)
    hermes = render.render_task(tasks["hermes-claude-bridge"], context)

    assert provider["schedule"] == "5 4 * * *"
    assert hermes["schedule"] == "25 4 * * *"


def test_render_task_cross_machine_preview_uses_requested_machine_schedule(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    render = _load_renderer()
    catalog = yaml.safe_load(SCHEDULE_PATH.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    tasks = {task["id"]: task for task in catalog["tasks"]}
    context = render.build_context("dev-secondary", registry=registry)

    provider = render.render_task(tasks["provider-dream-bridge"], context)
    hermes = render.render_task(tasks["hermes-claude-bridge"], context)

    assert provider["schedule"] == "15 4 * * *"
    assert hermes["schedule"] == "35 4 * * *"
    assert provider["schedule"] != "5 4 * * *"
    assert hermes["schedule"] != "25 4 * * *"


def test_render_cron_line_separator_is_one_ascii_space():
    render = _load_renderer()
    assert render.render_cron_line("0 1 * * *", "echo ok") == "0 1 * * * echo ok"


def test_expand_command_only_replaces_exact_workspace_and_log_variables(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    render = _load_renderer()
    context = render.build_context(
        "m1",
        registry={
            "machines": {
                "m1": {
                    "hostname": "m1",
                    "schedule_variant": "contribute",
                }
            }
        },
    )

    expanded = render.expand_command(
        "echo $LOG ${LOG} $LOGDIR $LOGNAME "
        "$WORKSPACE_HUB ${WORKSPACE_HUB} $WORKSPACE_HUB_BACKUP ${WORKSPACE_HUB_BACKUP}",
        context,
    )

    assert "$LOGDIR" in expanded
    assert "$LOGNAME" in expanded
    assert "$WORKSPACE_HUB_BACKUP" in expanded
    assert "${WORKSPACE_HUB_BACKUP}" in expanded
    assert "/tmp/workspace-hub-cron.logDIR" not in expanded
    assert "/tmp/workspace-hub-cron.logNAME" not in expanded
    assert f"{REPO}_BACKUP" not in expanded
    assert f"echo /tmp/workspace-hub-cron.log /tmp/workspace-hub-cron.log" in expanded
    assert f" {REPO} {REPO} " in expanded
