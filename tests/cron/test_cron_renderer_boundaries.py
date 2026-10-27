"""Synthetic leaf-renderer boundaries; refs #3647.

Contract sources: scripts/cron/cron_render.py::build_context,
effective_schedule, expand_command and render_task; exact-variable examples in
tests/cron/test_cron_render.py. The schedule literals come from that test's
fallback example and config/scheduled-tasks/schedule-tasks.yaml::harness-update.
They are distinct fixture markers, not new scheduling policy. Expected schedules
are hand-selected from the first matching token, or the generic fallback.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def renderer():
    path = Path(__file__).resolve().parents[2] / "scripts/cron/cron_render.py"
    spec = importlib.util.spec_from_file_location("boundary_cron_render", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def workspace(tmp_path):
    return tmp_path / "workspace with spaces"


@pytest.fixture
def context(renderer, workspace):
    # Synthetic tokens only. build_context orders hostname, canonical identity,
    # requested token, then remaining aliases, independently of mapping order.
    return renderer.build_context(
        "requested",
        registry={
            "machines": {
                "worker": {
                    "hostname": "primary",
                    "hostname_aliases": ["requested", "alternate"],
                    "schedule_variant": "full",
                }
            }
        },
        workspace_hub=workspace,
    )


@pytest.mark.parametrize(
    ("task", "expected"),
    [
        pytest.param({"schedule": "0 0 * * *"}, "0 0 * * *", id="generic"),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": None},
            "0 0 * * *", id="null-overrides",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {}},
            "0 0 * * *", id="empty-overrides",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {"other": "45 1 * * *"}},
            "0 0 * * *", id="absent-token",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {"primary": "15 1 * * *"}},
            "15 1 * * *", id="hostname-override",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {"worker": "45 1 * * *"}},
            "45 1 * * *", id="canonical-override",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {"requested": "15 2 * * *"}},
            "15 2 * * *", id="requested-override",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {"alternate": "45 1 * * *"}},
            "45 1 * * *", id="alias-override",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {
                "alternate": "15 2 * * *", "requested": "15 2 * * *",
                "worker": "45 1 * * *", "primary": "15 1 * * *",
            }},
            "15 1 * * *", id="hostname-before-canonical",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {
                "alternate": "15 2 * * *", "requested": "15 2 * * *",
                "worker": "45 1 * * *",
            }},
            "45 1 * * *", id="canonical-before-requested",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {
                "alternate": "45 1 * * *", "requested": "15 2 * * *",
            }},
            "15 2 * * *", id="requested-before-alias",
        ),
        pytest.param(
            {"schedule": "0 0 * * *", "schedule_by_machine": {" PRIMARY ": " 15 1 * * * "}},
            "15 1 * * *", id="normalized-key-and-value",
        ),
        pytest.param({"schedule": " 0 0 * * * "}, "0 0 * * *", id="trimmed-fallback"),
        pytest.param({}, "", id="absent-fallback"),
    ],
)
def test_schedule_override_precedence_table(renderer, context, task, expected):
    before = deepcopy(task)
    assert renderer.effective_schedule(task, context) == expected
    assert task == before


@pytest.mark.parametrize(
    "command",
    [
        "$LOGDIR", "$LOGNAME", "$LOG_", "$LOG9", "$LOGa",
        "${LOGDIR}", "${LOGNAME}", "${LOG_}", "${LOG9}", "${LOGa}",
        "$WORKSPACE_HUB_BACKUP", "$WORKSPACE_HUB9", "$WORKSPACE_HUBa",
        "${WORKSPACE_HUB_BACKUP}", "${WORKSPACE_HUB9}", "${WORKSPACE_HUBa}",
        "${LOG", "${WORKSPACE_HUB",
    ],
)
def test_placeholder_prefix_is_not_rewritten(renderer, context, command):
    assert renderer.expand_command(command, context) == command


def test_complete_placeholder_boundaries(renderer, context, workspace):
    # Literal expected text is assembled independently from the fixture root.
    root = workspace.as_posix()
    log = f"{root}/logs/quality/cron-wrapper.log"
    cases = [
        ("$WORKSPACE_HUB", root),
        ("${WORKSPACE_HUB}", root),
        ("$LOG", log),
        ("${LOG}", log),
        ('  cd "$WORKSPACE_HUB" >> "${LOG}"  ', f'cd "{root}" >> "{log}"'),
        ("$WORKSPACE_HUB/scripts/check.sh:$LOG", f"{root}/scripts/check.sh:{log}"),
        ("${WORKSPACE_HUB}_BACKUP ${LOG}DIR", f"{root}_BACKUP {log}DIR"),
        ("$LOG/$LOG-${LOG}.$WORKSPACE_HUB", f"{log}/{log}-{log}.{root}"),
    ]
    for command, expected in cases:
        assert renderer.expand_command(command, context) == expected, command


def test_render_is_stable_for_spaced_root(renderer, context, workspace):
    task = {
        "id": "sample-task",
        "schedule": "0 0 * * *",
        "schedule_by_machine": {"primary": "15 1 * * *"},
        "command": 'cd "$WORKSPACE_HUB" && printf ready >> "${LOG}"',
    }
    task_before = deepcopy(task)
    context_before = deepcopy(context)
    root = workspace.as_posix()
    command = f'cd "{root}" && printf ready >> "{root}/logs/quality/cron-wrapper.log"'
    expected = {
        **task_before,
        "schedule": "15 1 * * *",
        "command": command,
        "line": f"15 1 * * * {command}",
        "machine_id": "worker",
    }

    assert renderer.render_task(task, context) == expected
    assert renderer.render_task(task, context) == expected
    assert renderer.render_task(deepcopy(task), deepcopy(context)) == expected
    assert task == task_before
    assert context == context_before
