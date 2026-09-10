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


def test_registry_posix_workspace_root_stays_posix_on_windows(monkeypatch):
    monkeypatch.delenv("WORKSPACE_HUB", raising=False)
    render = _load_renderer()
    context = render.build_context(
        "linux-a",
        registry={
            "machines": {
                "linux-a": {
                    "hostname": "linux-a",
                    "os": "linux",
                    "workspace_root": "/canonical/workspace-hub",
                    "schedule_variant": "full",
                }
            }
        },
        workspace_hub="/canonical/workspace-hub",
    )

    assert context["workspace_hub"] == "/canonical/workspace-hub"
    assert context["log"] == "/canonical/workspace-hub/logs/quality/cron-wrapper.log"


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
    assert "bridge-hermes-claude.sh --commit" in hermes["line"]


def test_repository_sync_render_uses_wrapper_owned_log_contract(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB", str(REPO))
    render = _load_renderer()
    catalog = yaml.safe_load(SCHEDULE_PATH.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    task = next(item for item in catalog["tasks"] if item["id"] == "repository-sync")
    context = render.build_context("ace-linux-1", registry=registry)

    rendered = render.render_task(task, context)

    assert task["log"] == "logs/repository-sync-*.log"
    assert "scripts/cron-repository-sync.sh" in rendered["line"]
    assert "$LOG" not in rendered["line"]
    assert "logs/quality/cron-wrapper.log" not in rendered["line"]


def test_repository_sync_wrapper_delegates_mutation_through_runtime():
    wrapper = (REPO / "scripts" / "cron-repository-sync.sh").read_text(encoding="utf-8")
    assert "cron_runtime.py" in wrapper
    assert "run" in wrapper
    assert '"$WORKSPACE_ROOT/scripts/repository_sync"' in wrapper
    assert '\n"$WORKSPACE_ROOT/scripts/repository_sync" >>' not in wrapper


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


def test_build_context_exposes_registry_os_for_scheduler_routing():
    """#3507 gpu-claw incident: setup-cron.sh skipped Linux cron reconciliation for
    ANY contribute-minimal machine, equating the schedule variant with Windows.
    The discriminator must be the registry os field, exposed via build_context."""
    registry = {"machines": {
        "gpu-claw": {"hostname": "gpu-claw", "os": "linux",
                     "schedule_variant": "contribute-minimal"},
        "ace-win-1": {"hostname": "ace-win-1", "os": "windows",
                      "schedule_variant": "contribute-minimal"},
        "legacy-box": {"hostname": "legacy-box",
                       "schedule_variant": "contribute"},
    }}
    render = _load_renderer()
    assert render.build_context("gpu-claw", registry=registry)["os"] == "linux"
    assert render.build_context("ace-win-1", registry=registry)["os"] == "windows"
    # missing os defaults to linux — cron reconciliation must not silently skip
    assert render.build_context("legacy-box", registry=registry)["os"] == "linux"
