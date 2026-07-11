from __future__ import annotations

import json
import inspect
import subprocess
import sys
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "scripts" / "cron" / "cron_runtime.py"


def _load_runtime():
    assert RUNTIME.exists(), "cron_runtime.py must provide the runtime contract"
    import importlib.util

    spec = importlib.util.spec_from_file_location("cron_runtime_test", RUNTIME)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_proc(proc_root: Path, pid: int, *, start_token: int, state: str, wchan: str):
    pid_dir = proc_root / str(pid)
    pid_dir.mkdir(parents=True)
    # /proc/<pid>/stat: starttime is field 22, index 19 after the comm field.
    trailing = [state, *(["0"] * 18), str(start_token), *(["0"] * 8)]
    (pid_dir / "stat").write_text(f"{pid} (worker name) {' '.join(trailing)}\n")
    (pid_dir / "wchan").write_text(f"{wchan}\n")


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def test_completed_success_failure_and_never_started_are_distinct(tmp_path):
    runtime = _load_runtime()
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    never = runtime.inspect_runtime(state_dir, 60, [], proc_root=tmp_path / "proc", now=100)
    assert never["status"] == "never_started"

    _write_json(state_dir / "last-result.json", {"finished_at": 90, "exit_code": 0})
    success = runtime.inspect_runtime(state_dir, 60, [], proc_root=tmp_path / "proc", now=100)
    assert success["status"] == "completed_success"

    _write_json(state_dir / "last-result.json", {"finished_at": 95, "exit_code": 7})
    failure = runtime.inspect_runtime(state_dir, 60, [], proc_root=tmp_path / "proc", now=100)
    assert failure["status"] == "completed_failure"


def test_runtime_rejects_reused_child_pid(tmp_path):
    runtime = _load_runtime()
    state_dir = tmp_path / "state"
    proc_root = tmp_path / "proc"
    _write_json(
        state_dir / "active.json",
        {"started_at": 10, "child_pid": 321, "child_pgid": 321, "child_start_token": 111},
    )
    _write_proc(proc_root, 321, start_token=222, state="S", wchan="do_wait")

    result = runtime.inspect_runtime(state_dir, 60, [], proc_root=proc_root, now=20)

    assert result["status"] == "stale_or_reused_pid"
    assert result["child_pid"] == 321


def test_runtime_classifies_configured_filesystem_wait_from_child(tmp_path):
    runtime = _load_runtime()
    state_dir = tmp_path / "state"
    proc_root = tmp_path / "proc"
    _write_json(
        state_dir / "active.json",
        {
            "started_at": 10,
            "supervisor_pid": 100,
            "child_pid": 654,
            "child_pgid": 654,
            "child_start_token": 333,
        },
    )
    _write_proc(proc_root, 654, start_token=333, state="S", wchan="request_wait_answer")

    result = runtime.inspect_runtime(
        state_dir,
        60,
        ["request_wait_answer"],
        proc_root=proc_root,
        now=20,
    )

    assert result["status"] == "filesystem_wait"
    assert result["child_pid"] == 654
    assert result["wait_channel"] == "request_wait_answer"


def test_second_runner_reports_contention_without_running_command(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    schedule = workspace / "schedule.yaml"
    schedule.write_text(
        "tasks:\n"
        "  - id: repository-sync\n"
        "    runtime:\n"
        "      singleton: true\n"
        "      max_seconds: 60\n"
        "      state_dir: .state/repository-sync\n"
    )
    marker = workspace / "marker"
    command = [
        sys.executable,
        "-c",
        f"from pathlib import Path; import time; Path({str(marker)!r}).open('a').write('x'); time.sleep(1.5)",
    ]
    base = [
        sys.executable,
        str(RUNTIME),
        "run",
        "--schedule-file",
        str(schedule),
        "--workspace",
        str(workspace),
        "--task-id",
        "repository-sync",
        "--log",
        "logs/repository-sync-test.log",
        "--",
        *command,
    ]

    first = subprocess.Popen(base)
    active = workspace / ".state" / "repository-sync" / "active.json"
    deadline = time.monotonic() + 3
    while not active.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert active.exists(), "first runner did not publish active evidence"

    second = subprocess.run(base, capture_output=True, text=True, timeout=3)
    assert second.returncode == 75
    assert (active.parent / "contention.json").exists()
    assert marker.read_text() == "x"

    assert first.wait(timeout=4) == 0
    assert not active.exists()
    result = json.loads((active.parent / "last-result.json").read_text())
    assert result["exit_code"] == 0


def test_signal_keeps_lock_until_child_exits(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    schedule = workspace / "schedule.yaml"
    schedule.write_text(
        "tasks:\n"
        "  - id: repository-sync\n"
        "    runtime:\n"
        "      singleton: true\n"
        "      max_seconds: 60\n"
        "      state_dir: .state/repository-sync\n"
    )
    ready = workspace / "ready"
    child_code = (
        "import signal,time; from pathlib import Path; "
        "signal.signal(signal.SIGTERM, lambda *_: time.sleep(0.8)); "
        f"Path({str(ready)!r}).write_text('ready'); "
        "time.sleep(3)"
    )
    base = [
        sys.executable,
        str(RUNTIME),
        "run",
        "--schedule-file",
        str(schedule),
        "--workspace",
        str(workspace),
        "--task-id",
        "repository-sync",
        "--log",
        "logs/repository-sync-test.log",
        "--",
        sys.executable,
        "-c",
        child_code,
    ]

    first = subprocess.Popen(base)
    active = workspace / ".state" / "repository-sync" / "active.json"
    deadline = time.monotonic() + 3
    while not active.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert active.exists()
    deadline = time.monotonic() + 2
    while not ready.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert ready.exists(), "child did not install its signal handler"

    first.terminate()
    contender = subprocess.run(base, capture_output=True, text=True, timeout=3)
    assert contender.returncode == 75
    first.wait(timeout=4)
    assert not active.exists()


def test_group_wait_has_no_timeout_that_can_release_live_mutator():
    runtime = _load_runtime()
    signature = inspect.signature(runtime._wait_for_group)
    assert "timeout" not in signature.parameters


@pytest.mark.parametrize("path", ["/tmp/state", "../state", ".state/../escape"])
def test_state_dir_must_be_controlled_repo_relative(tmp_path, path):
    runtime = _load_runtime()
    with pytest.raises(ValueError):
        runtime.resolve_controlled_path(tmp_path, path)


def test_controlled_path_rejects_symlink_component(tmp_path):
    runtime = _load_runtime()
    real = tmp_path / "real"
    real.mkdir()
    (tmp_path / "linked").symlink_to(real, target_is_directory=True)

    with pytest.raises(ValueError):
        runtime.resolve_controlled_path(tmp_path, "linked/task")
