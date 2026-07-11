#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Bounded singleton runtime state for opted-in scheduled tasks."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
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
    cursor = root
    for part in candidate.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"path contains a symlink component: {relative}")
    resolved = (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path escapes workspace: {relative}")
    return resolved


def _atomic_json(path: Path, payload: dict[str, Any], *, dir_fd: int | None = None) -> None:
    if dir_fd is None:
        path.parent.mkdir(parents=True, exist_ok=True)
    temporary = f".{path.name}.{os.getpid()}.{time.time_ns()}"
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    parent_fd = os.dup(dir_fd) if dir_fd is not None else os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    fd = os.open(temporary, flags, 0o600, dir_fd=parent_fd)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        os.close(parent_fd)


def _open_dir_beneath(root: Path, relative: Path, *, create: bool) -> int:
    """Walk beneath root using directory descriptors and no-follow opens."""
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in relative.parts:
            if part in ("", ".", ".."):
                raise ValueError("unsafe directory component")
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            flags = os.O_RDONLY | os.O_DIRECTORY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def _open_append_beneath(root: Path, relative: Path) -> int:
    parent_fd = _open_dir_beneath(root, relative.parent, create=True)
    try:
        flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        return os.open(relative.name, flags, 0o600, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _read_json(path: Path, *, dir_fd: int | None = None) -> dict[str, Any] | None:
    try:
        if dir_fd is None:
            text = path.read_text(encoding="utf-8")
        else:
            flags = os.O_RDONLY | (os.O_NOFOLLOW if hasattr(os, "O_NOFOLLOW") else 0)
            fd = os.open(path.name, flags, dir_fd=dir_fd)
            with os.fdopen(fd, encoding="utf-8") as handle:
                text = handle.read()
        value = json.loads(text)
    except FileNotFoundError:
        return None
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


def _valid_active(active: dict[str, Any]) -> bool:
    integer_fields = ("supervisor_pid", "child_pid", "child_pgid", "child_start_token")
    if any(not isinstance(active.get(key), int) or isinstance(active.get(key), bool) for key in integer_fields):
        return False
    if not isinstance(active.get("started_at"), (int, float)) or isinstance(active.get("started_at"), bool):
        return False
    phase = active.get("phase", "child_running")
    if phase not in ("child_running", "group_draining"):
        return False
    return phase != "group_draining" or (
        isinstance(active.get("supervisor_start_token"), int)
        and not isinstance(active.get("supervisor_start_token"), bool)
    )


def _valid_event(event: dict[str, Any] | None, time_key: str, *, result: bool = False) -> bool:
    if event is None:
        return True
    timestamp = event.get(time_key)
    if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
        return False
    if result and (not isinstance(event.get("exit_code"), int) or isinstance(event.get("exit_code"), bool)):
        return False
    return True


def inspect_runtime(
    state_dir: Path,
    max_seconds: int,
    wait_channels: list[str],
    *,
    proc_root: Path = Path("/proc"),
    now: float | None = None,
    state_fd: int | None = None,
) -> dict[str, Any]:
    """Classify one task from its bounded runtime evidence."""
    now = time.time() if now is None else now
    active = _read_json(state_dir / "active.json", dir_fd=state_fd)
    contention = _read_json(state_dir / "contention.json", dir_fd=state_fd)
    result = _read_json(state_dir / "last-result.json", dir_fd=state_fd)
    invalid_json = any(item and item.get("_invalid") for item in (active, contention, result))
    if invalid_json or not _valid_event(contention, "observed_at") or not _valid_event(result, "finished_at", result=True):
        return _base_result("invalid_state", active)
    if active:
        if not _valid_active(active):
            return _base_result("invalid_state", active)
        draining = active.get("phase") == "group_draining"
        identity_pid = active["supervisor_pid"] if draining else active["child_pid"]
        expected_token = active["supervisor_start_token"] if draining else active["child_start_token"]
        identity = _process_identity(identity_pid, proc_root)
        if not identity or identity["start_token"] != expected_token:
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


def _open_lock(path: Path, *, dir_fd: int | None = None) -> int:
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path if dir_fd is None else path.name, flags, 0o600, dir_fd=dir_fd)


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


def _active_record(task_id: str, child: subprocess.Popen[Any]) -> dict[str, Any]:
    child_identity = _process_identity(child.pid)
    supervisor_identity = _process_identity(os.getpid())
    if child_identity is None or supervisor_identity is None:
        child.terminate()
        child.wait()
        raise RuntimeError("process identity unavailable")
    return {
        "task_id": task_id,
        "supervisor_pid": os.getpid(),
        "child_pid": child.pid,
        "child_pgid": os.getpgid(child.pid),
        "child_start_token": child_identity["start_token"],
        "supervisor_start_token": supervisor_identity["start_token"],
        "started_at": time.time(),
        "phase": "child_running",
    }


def _execute_child(
    task_id: str,
    argv: list[str],
    workspace: Path,
    log_fd: int,
    state_fd: int,
) -> int:
    with os.fdopen(log_fd, "a", encoding="utf-8") as log_handle:
        child = subprocess.Popen(argv, cwd=workspace, stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True)
        active = _active_record(task_id, child)
        _atomic_json(Path("active.json"), active, dir_fd=state_fd)
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
            active["phase"] = "group_draining"
            _atomic_json(Path("active.json"), active, dir_fd=state_fd)
            _wait_for_group(active["child_pgid"])
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        exit_code = 128 + received[-1] if received else child_code
    _atomic_json(
        Path("last-result.json"),
        {"task_id": task_id, "finished_at": time.time(), "exit_code": exit_code},
        dir_fd=state_fd,
    )
    try:
        os.unlink("active.json", dir_fd=state_fd)
    except FileNotFoundError:
        pass
    return exit_code


def run_task(*, task_id: str, argv: list[str], workspace: Path, log_path: Path, state_dir: Path) -> int:
    """Run argv under a task singleton and publish atomic lifecycle evidence."""
    state_relative = state_dir.relative_to(workspace)
    log_relative = log_path.relative_to(workspace)
    state_fd = _open_dir_beneath(workspace, state_relative, create=True)
    lock_fd = _open_lock(Path("runtime.lock"), dir_fd=state_fd)
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            _atomic_json(
                Path("contention.json"),
                {"task_id": task_id, "observed_at": time.time()},
                dir_fd=state_fd,
            )
            return CONTENTION_EXIT
        log_fd = _open_append_beneath(workspace, log_relative)
        return _execute_child(task_id, argv, workspace, log_fd, state_fd)
    finally:
        os.close(lock_fd)
        os.close(state_fd)


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
    state_relative = state_dir.relative_to(workspace)
    try:
        state_fd = _open_dir_beneath(workspace, state_relative, create=False)
    except FileNotFoundError:
        state_fd = None
    try:
        result = inspect_runtime(
            state_dir,
            contract["max_seconds"],
            contract.get("filesystem_wait_wchans", []),
            state_fd=state_fd,
        )
    finally:
        if state_fd is not None:
            os.close(state_fd)
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
    print(f"{result['status']}\t{encoded}" if args.format == "tsv" else encoded)
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
    inspect.add_argument("--format", choices=("json", "tsv"), default="json")
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
