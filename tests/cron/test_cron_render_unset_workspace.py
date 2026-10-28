"""Execute synthetic rendered commands without the workspace environment variable."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess

import pytest


@pytest.fixture
def synthetic_task(tmp_path, monkeypatch):
    monkeypatch.delenv("WORKSPACE_HUB", raising=False)
    root = tmp_path / "root with spaces"
    root.mkdir()
    renderer_path = (
        Path(__file__).resolve().parent.parent.parent
        / "scripts" / "cron" / "cron_render.py"
    )
    spec = importlib.util.spec_from_file_location("cron_render", renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    context = renderer.build_context(
        "target", registry={"machines": {}}, workspace_hub=root
    )
    task = {
        "schedule": "* * * * *",
        "command": (
            'cd "${WORKSPACE_HUB}" && printf marker > marker '
            '&& printf logged >> "$WORKSPACE_HUB/logs/task output/run.log"'
        ),
        "log": "logs/task output/run.log",
    }
    return renderer, context, task, root


def _run_rendered(rendered, cwd):
    assert "$WORKSPACE_HUB" not in rendered["line"]
    assert "${WORKSPACE_HUB}" not in rendered["line"]
    environment = os.environ.copy()
    environment.pop("WORKSPACE_HUB", None)
    return subprocess.run(
        ["sh", "-c", rendered["command"]],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_rendered_task_runs_without_workspace_environment(synthetic_task, tmp_path):
    renderer, context, task, root = synthetic_task
    rendered = renderer.render_task(task, context)

    completed = _run_rendered(rendered, tmp_path)

    assert completed.returncode == os.EX_OK, completed.stderr
    assert (root / "marker").read_text() == "marker"
    assert (root / "logs" / "task output").is_dir()
    assert (root / task["log"]).read_text() == "logged"
    # Expected shell arguments follow the synthetic task above, independently
    # of the renderer's internal template or expansion implementation.
    expected_command = (
        f'mkdir -p "{root}/logs/task output" && '
        f'cd "{root}" && printf marker > marker '
        f'&& printf logged >> "{root}/logs/task output/run.log"'
    )
    assert rendered["command"] == expected_command
    assert rendered["line"] == f"* * * * * {expected_command}"
    assert set(tmp_path.iterdir()) == {root}


def test_existing_log_directory(synthetic_task, tmp_path):
    renderer, context, task, root = synthetic_task
    log_file = root / task["log"]
    log_file.parent.mkdir(parents=True)
    log_file.write_text("existing ")
    rendered = renderer.render_task(task, context)

    completed = _run_rendered(rendered, tmp_path)

    assert completed.returncode == os.EX_OK, completed.stderr
    assert (root / "marker").read_text() == "marker"
    assert log_file.read_text() == "existing logged"
    assert set(tmp_path.iterdir()) == {root}


def test_no_log_task(synthetic_task, tmp_path):
    renderer, context, task, root = synthetic_task
    task.pop("log")
    task["command"] = 'cd "$WORKSPACE_HUB" && printf marker > marker'
    rendered = renderer.render_task(task, context)

    completed = _run_rendered(rendered, tmp_path)

    assert completed.returncode == os.EX_OK, completed.stderr
    assert rendered["command"] == f'cd "{root}" && printf marker > marker'
    assert rendered["line"] == f'* * * * * cd "{root}" && printf marker > marker'
    assert (root / "marker").read_text() == "marker"
    assert not (root / "logs").exists()
    assert set(tmp_path.iterdir()) == {root}
