#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Bounded singleton runtime state for opted-in scheduled tasks."""

from __future__ import annotations

import argparse
import errno
import fcntl
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml


CONTENTION_EXIT = 75


def resolve_controlled_path(workspace: Path, relative: str) -> Path:
    """Resolve a relative path beneath workspace without accepting traversal."""
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError(f"path must be controlled and repo-relative: {relative}")
    root = workspace.resolve()
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path escapes workspace: {relative}")
    return resolved


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"_invalid": True}
    return value if isinstance(value, dict) else {"_invalid": True}


def _process_identity(pid: int, proc_root: Path = Path("/proc")) -> dict[str, Any] | None:
    try:
        stat_text = (proc_root / str(pid) / "stat").read_text(encoding="utf-8").strip()
        tail = stat_text[stat_text.rfind(")") + 2 :].split()
        return {
            "state": tail[0],
            "start_token": int(tail[19]),
            "wait_channel": (proc_root / str(pid) / "wchan").read_text(encoding="utf-8").strip(),
        }
    except (FileNotFoundError, PermissionError, IndexError, ValueError, OSError):
        return None


def _base_result(status: str, active: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"status": status}
    if active:
        for key in ("supervisor_pid", "child_pid", "child_pgid", "started_at"):
            if key in active:
                result[key] = active[key]
    return result


def inspect_runtime(
    state_dir: Path,
    max_seconds: int,
    wait_channels: list[str],
    *,
    proc_root: Path = Path("/proc"),
    now: float | None = None,
) -> dict[str, Any]:
    """Classify one task from its bounded runtime evidence."""
    now = time.time() if now is None else now
    active = _read_json(state_dir / "active.json")
    contention = _read_json(state_dir / "contention.json")
    result = _read_json(state_dir / "last-result.json")
    if any(item and item.get("_invalid") for item in (active, contention, result)):
        return _base_result("invalid_state", active)
    if active:
        identity = _process_identity(int(active.get("child_pid", -1)), proc_root)
        if not identity or identity["start_token"] != active.get("child_start_token"):
            return _base_result("stale_or_reused_pid", active)
        output = _base_result("active_within_budget", active)
        output.update({"process_state": identity["state"], "wait_channel": identity["wait_channel"]})
        output["elapsed_seconds"] = max(0, int(now - float(active["started_at"])))
        if contention and contention.get("observed_at", 0) >= active.get("started_at", 0):
            output["status"] = "overlap"
        elif identity["state"] == "D" or identity["wait_channel"] in wait_channels:
            output["status"] = "filesystem_wait"
        elif output["elapsed_seconds"] > max_seconds:
            output["status"] = "excessive_runtime"
        return output
    if contention and (not result or contention.get("observed_at", 0) > result.get("finished_at", 0)):
        return _base_result("orphan_contention")
    if result:
        return _base_result("completed_success" if result.get("exit_code") == 0 else "completed_failure") | result
    return _base_result("never_started")


def _load_contract(schedule_file: Path, task_id: str) -> dict[str, Any]:
    data = yaml.safe_load(schedule_file.read_text(encoding="utf-8")) or {}
    task = next((item for item in data.get("tasks", []) if item.get("id") == task_id), None)
    if not task or not isinstance(task.get("runtime"), dict):
        raise ValueError(f"runtime contract missing for task: {task_id}")
    return task["runtime"]


def _open_lock(path: Path) -> int:
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path, flags, 0o600)


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _wait_for_group(pgid: int) -> None:
    while _group_exists(pgid):
        time.sleep(0.05)


def _execute_child(task_id: str, argv: list[str], workspace: Path, log_path: Path, state_dir: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_handle:
        child = subprocess.Popen(argv, cwd=workspace, stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True)
        identity = _process_identity(child.pid)
        if identity is None:
            child.terminate()
            child.wait()
            raise RuntimeError("child identity unavailable")
        active = {
            "task_id": task_id,
            "supervisor_pid": os.getpid(),
            "child_pid": child.pid,
            "child_pgid": os.getpgid(child.pid),
            "child_start_token": identity["start_token"],
            "started_at": time.time(),
        }
        _atomic_json(state_dir / "active.json", active)
        received: list[int] = []

        def forward(signum: int, _frame: object) -> None:
            received.append(signum)
            try:
                os.killpg(active["child_pgid"], signum)
            except ProcessLookupError:
                pass

        previous = {sig: signal.signal(sig, forward) for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
        try:
            child_code = child.wait()
            _wait_for_group(active["child_pgid"])
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        exit_code = 128 + received[-1] if received else child_code
    _atomic_json(state_dir / "last-result.json", {"task_id": task_id, "finished_at": time.time(), "exit_code": exit_code})
    (state_dir / "active.json").unlink(missing_ok=True)
    return exit_code


def run_task(*, task_id: str, argv: list[str], workspace: Path, log_path: Path, state_dir: Path) -> int:
    """Run argv under a task singleton and publish atomic lifecycle evidence."""
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_fd = _open_lock(state_dir / "runtime.lock")
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            _atomic_json(state_dir / "contention.json", {"task_id": task_id, "observed_at": time.time()})
            return CONTENTION_EXIT
        return _execute_child(task_id, argv, workspace, log_path, state_dir)
    finally:
        os.close(lock_fd)


def _run_command(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    contract = _load_contract(args.schedule_file, args.task_id)
    state_dir = resolve_controlled_path(workspace, contract["state_dir"])
    log_path = resolve_controlled_path(workspace, args.log)
    if not args.argv:
        raise ValueError("argv after -- is required")
    return run_task(task_id=args.task_id, argv=args.argv, workspace=workspace, log_path=log_path, state_dir=state_dir)


def _inspect_command(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    contract = _load_contract(args.schedule_file, args.task_id)
    state_dir = resolve_controlled_path(workspace, contract["state_dir"])
    result = inspect_runtime(
        state_dir,
        contract["max_seconds"],
        contract.get("filesystem_wait_wchans", []),
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--schedule-file", type=Path, required=True)
    run.add_argument("--workspace", type=Path, required=True)
    run.add_argument("--task-id", required=True)
    run.add_argument("--log", required=True)
    run.add_argument("argv", nargs=argparse.REMAINDER)
    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--schedule-file", type=Path, required=True)
    inspect.add_argument("--workspace", type=Path, required=True)
    inspect.add_argument("--task-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if getattr(args, "argv", None) and args.argv[0] == "--":
        args.argv = args.argv[1:]
    try:
        return _run_command(args) if args.command == "run" else _inspect_command(args)
    except (OSError, ValueError, RuntimeError, yaml.YAMLError) as exc:
        print(f"cron-runtime: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
