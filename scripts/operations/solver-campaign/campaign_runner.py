#!/usr/bin/env python3
"""Approval-gated campaign runner for resumable licensed-solver drivers."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath


STATE_WORDS = ("DONE", "FAILED", "HELD", "STOPPED", "pending", "running", "unapproved", "digest-mismatch")
CREDENTIAL_NAME_RE = re.compile(r"(TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|KEY)", re.IGNORECASE)
ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
FULL_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
LOCK_NAME = "runner.lock"
HEARTBEAT_NAME = "heartbeat.json"
DEFAULT_HEARTBEAT_SECONDS = 60.0
DEFAULT_HEARTBEAT_FRESH_SECONDS = 180.0
DEFAULT_STOP_GRACE_SECONDS = 20.0
DEFAULT_MIN_FREE_BYTES = 5 * 1024 * 1024 * 1024
DEFAULT_LICENCE_TRIES_PER_DAY = 3
LOG_LIMIT_BYTES = 1024 * 1024
LOG_ROTATIONS = 3
PROCESS_TREE_KILL_COMMAND = "taskkill"

REQUIRED_FIELDS = {
    "id",
    "title",
    "repo_dir",
    "ref",
    "driver",
    "cwd",
    "env",
    "expected_hours",
    "max_hours",
    "licence_exit_codes",
    "retry",
    "priority",
    "after",
}
OPTIONAL_FIELDS = {"progress"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def utc_text(moment: dt.datetime | None = None) -> str:
    return (moment or utc_now()).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def default_root() -> Path:
    return Path.home() / "solver-campaigns"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_declared_absolute(value: str) -> bool:
    return Path(value).is_absolute() or value.startswith("/") or PureWindowsPath(value).is_absolute()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> tuple[dict | None, list[str]]:
    try:
        data = read_json(path)
    except Exception as exc:  # noqa: BLE001
        return None, [f"{path.name}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{path.name}: manifest must be a JSON object"]
    errors = validate_manifest_data(data, path)
    return data, errors


def validate_manifest_data(data: dict, path: Path) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_FIELDS):
        if field not in data:
            errors.append(f"missing field: {field}")
    for field in sorted(set(data) - ALL_FIELDS):
        errors.append(f"unknown field: {field}")
    campaign_id = data.get("id")
    if not isinstance(campaign_id, str) or not ID_RE.fullmatch(campaign_id):
        errors.append("id must be a short safe token")
    elif path.name != f"{campaign_id}.json":
        errors.append("id must equal the manifest file name without .json")
    if not isinstance(data.get("title"), str) or not data.get("title"):
        errors.append("title must be a non-empty string")
    repo_dir = data.get("repo_dir")
    if not isinstance(repo_dir, str) or not is_declared_absolute(repo_dir):
        errors.append("repo_dir must be absolute")
    ref = data.get("ref")
    if not isinstance(ref, str) or not FULL_COMMIT_RE.fullmatch(ref):
        errors.append("ref must be a full commit id")
    driver = data.get("driver")
    if not isinstance(driver, list) or not driver or not all(isinstance(item, str) and item for item in driver):
        errors.append("driver must be a non-empty argument list of strings")
    cwd = data.get("cwd")
    if not isinstance(cwd, str) or not is_declared_absolute(cwd):
        errors.append("cwd must be absolute")
    env = data.get("env")
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in getattr(env, "items", lambda: [])()):
        errors.append("env must be an object of string names and string values")
    elif any(CREDENTIAL_NAME_RE.search(name) for name in env):
        errors.append("env name looks like a credential")
    expected = data.get("expected_hours")
    max_hours = data.get("max_hours")
    if not isinstance(expected, (int, float)) or expected <= 0:
        errors.append("expected_hours must be positive")
    if not isinstance(max_hours, (int, float)) or max_hours <= 0:
        errors.append("max_hours must be positive")
    if isinstance(expected, (int, float)) and isinstance(max_hours, (int, float)) and max_hours < expected:
        errors.append("max_hours must be greater than or equal to expected_hours")
    progress = data.get("progress")
    if progress is not None:
        if not isinstance(progress, dict):
            errors.append("progress must be an object")
        else:
            if not isinstance(progress.get("glob"), str) or not progress.get("glob"):
                errors.append("progress.glob must be a non-empty string")
            if not isinstance(progress.get("total"), int) or progress.get("total") <= 0:
                errors.append("progress.total must be a positive integer")
    licence_codes = data.get("licence_exit_codes")
    if not isinstance(licence_codes, list) or not all(isinstance(code, int) and code >= 0 for code in licence_codes):
        errors.append("licence_exit_codes must be a list of non-negative integers")
    retry = data.get("retry")
    if not isinstance(retry, dict):
        errors.append("retry must be an object")
    else:
        for field in ("max_attempts", "backoff_minutes"):
            if not isinstance(retry.get(field), (int, float)) or retry.get(field) < 0:
                errors.append(f"retry.{field} must be a non-negative number")
        if retry.get("max_attempts") == 0:
            errors.append("retry.max_attempts must be positive")
        if "licence_tries_per_day" in retry and (
            not isinstance(retry.get("licence_tries_per_day"), int) or retry.get("licence_tries_per_day") <= 0
        ):
            errors.append("retry.licence_tries_per_day must be a positive integer")
    if not isinstance(data.get("priority"), int):
        errors.append("priority must be an integer")
    after = data.get("after")
    if not isinstance(after, list) or not all(isinstance(item, str) and ID_RE.fullmatch(item) for item in after):
        errors.append("after must be a list of safe campaign ids")
    elif isinstance(campaign_id, str) and campaign_id in after:
        errors.append("after must not include the campaign id")
    return errors


def read_approvals(root: Path) -> tuple[dict[str, list[dict]], list[str]]:
    approvals: dict[str, list[dict]] = {}
    errors: list[str] = []
    path = root / "approvals.tsv"
    if not path.exists():
        return approvals, errors
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            stripped = line.rstrip("\n")
            if not stripped:
                continue
            parts = stripped.split("\t")
            if len(parts) != 4 or not ID_RE.fullmatch(parts[0]) or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[1]):
                errors.append(f"approvals.tsv line {number} is malformed")
                continue
            approvals.setdefault(parts[0], []).append(
                {"digest": parts[1].lower(), "approval_ref": parts[2], "date": parts[3]}
            )
    return approvals, errors


def campaign_state_dir(root: Path, campaign_id: str) -> Path:
    return root / "state" / campaign_id


def result_path(root: Path, campaign_id: str) -> Path:
    return root / "done" / f"{campaign_id}.result"


def write_result(root: Path, campaign_id: str, state: str, done: int, total: int, *lines: str) -> None:
    first = f"{state}\t{utc_text()}\t{done}\t{total}"
    atomic_write_text(result_path(root, campaign_id), "\n".join([first, *lines]) + "\n")


def read_result(root: Path, campaign_id: str) -> tuple[str, int, int, str] | None:
    path = result_path(root, campaign_id)
    if not path.exists():
        return None
    first = path.read_text(encoding="utf-8").splitlines()[0]
    parts = first.split("\t")
    if len(parts) < 4:
        return None
    return parts[0], int(parts[2]), int(parts[3]), parts[1]


def append_runner_log(root: Path, campaign_id: str, message: str) -> None:
    state = campaign_state_dir(root, campaign_id)
    state.mkdir(parents=True, exist_ok=True)
    log = state / "runner.log"
    rotate_log(log)
    with log.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{utc_text()}\t{message}\n")


def rotate_log(path: Path) -> None:
    if not path.exists() or path.stat().st_size < LOG_LIMIT_BYTES:
        return
    for index in range(LOG_ROTATIONS - 1, 0, -1):
        older = path.with_name(f"{path.name}.{index}")
        newer = path.with_name(f"{path.name}.{index + 1}")
        if older.exists():
            if index + 1 > LOG_ROTATIONS:
                older.unlink()
            else:
                older.replace(newer)
    path.replace(path.with_name(f"{path.name}.1"))


def count_progress(manifest: dict) -> tuple[int, int]:
    progress = manifest.get("progress")
    if not progress:
        return 0, 0
    pattern = progress["glob"]
    total = int(progress["total"])
    try:
        if is_declared_absolute(pattern):
            done = len(list(Path(pattern).parent.glob(Path(pattern).name)))
        else:
            done = len(list(Path(manifest["cwd"]).glob(pattern)))
    except (NotImplementedError, OSError):
        done = 0
    return done, total


def read_attempts(root: Path, campaign_id: str) -> int:
    path = campaign_state_dir(root, campaign_id) / "attempts.txt"
    if not path.exists():
        return 0
    with contextlib.suppress(ValueError):
        return int(path.read_text(encoding="utf-8").strip())
    return 0


def write_attempts(root: Path, campaign_id: str, attempts: int) -> None:
    atomic_write_text(campaign_state_dir(root, campaign_id) / "attempts.txt", f"{attempts}\n")


def read_next_try(root: Path, campaign_id: str) -> dt.datetime | None:
    path = campaign_state_dir(root, campaign_id) / "next_try.txt"
    if not path.exists():
        return None
    with contextlib.suppress(Exception):
        return parse_utc(path.read_text(encoding="utf-8").strip())
    return None


def write_next_try(root: Path, campaign_id: str, when: dt.datetime | None) -> None:
    path = campaign_state_dir(root, campaign_id) / "next_try.txt"
    if when is None:
        with contextlib.suppress(FileNotFoundError):
            path.unlink()
    else:
        atomic_write_text(path, utc_text(when) + "\n")


def boot_time() -> str:
    if sys.platform.startswith("linux"):
        with contextlib.suppress(OSError, ValueError):
            for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
                if line.startswith("btime "):
                    return line.split()[1]
    return str(int(time.time() - time.monotonic()))


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        if os.name == "nt":
            done = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, check=False)
            return str(pid) in done.stdout
        return False


class RunnerLock:
    def __init__(self, root: Path, fresh_seconds: float):
        self.root = root
        self.path = root / LOCK_NAME
        self.fresh_seconds = fresh_seconds
        self.held = False

    def acquire(self) -> tuple[bool, str]:
        self.root.mkdir(parents=True, exist_ok=True)
        while True:
            record = {"pid": os.getpid(), "boot_time": boot_time(), "created_at": utc_text()}
            try:
                handle = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                stale, reason = self._is_stale()
                if not stale:
                    return False, reason
                stale_path = self.path.with_name(f"{LOCK_NAME}.stale.{os.getpid()}")
                try:
                    os.replace(self.path, stale_path)
                except FileNotFoundError:
                    continue
                except OSError:
                    return False, "lock changed while replacing stale lock"
                with contextlib.suppress(OSError):
                    stale_path.unlink()
                continue
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(record, stream)
                stream.write("\n")
            self.held = True
            return True, "lock acquired"

    def _is_stale(self) -> tuple[bool, str]:
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return True, "lock unreadable"
        pid = int(record.get("pid", -1))
        if record.get("boot_time") != boot_time():
            return True, "lock boot time differs"
        if not process_alive(pid):
            return True, "lock process is gone"
        heartbeat = newest_heartbeat(self.root)
        if heartbeat and (utc_now() - heartbeat).total_seconds() <= self.fresh_seconds:
            return False, "another runner holds the lock with a fresh heartbeat"
        return False, "lock holder may still be alive; heartbeat is not fresh"

    def release(self) -> None:
        if self.held:
            with contextlib.suppress(FileNotFoundError):
                self.path.unlink()


def newest_heartbeat(root: Path) -> dt.datetime | None:
    newest = None
    for path in (root / "state").glob(f"*/{HEARTBEAT_NAME}"):
        with contextlib.suppress(Exception):
            beat = parse_utc(json.loads(path.read_text(encoding="utf-8"))["time"])
            if newest is None or beat > newest:
                newest = beat
    return newest


def read_checkout_head(repo_dir: Path) -> str | None:
    git_path = repo_dir / ".git"
    if git_path.is_file():
        text = git_path.read_text(encoding="utf-8").strip()
        if not text.startswith("gitdir:"):
            return None
        git_path = (repo_dir / text.split(":", 1)[1].strip()).resolve()
    if not git_path.is_dir():
        return None
    head_path = git_path / "HEAD"
    if not head_path.exists():
        return None
    head = head_path.read_text(encoding="utf-8").strip()
    if FULL_COMMIT_RE.fullmatch(head):
        return head.lower()
    if not head.startswith("ref:"):
        return None
    ref = head.split(":", 1)[1].strip()
    loose = git_path / ref
    if loose.exists():
        value = loose.read_text(encoding="utf-8").strip()
        return value.lower() if FULL_COMMIT_RE.fullmatch(value) else None
    packed = git_path / "packed-refs"
    if packed.exists():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or line.startswith("^") or not line.strip():
                continue
            parts = line.split(" ")
            if len(parts) == 2 and parts[1] == ref and FULL_COMMIT_RE.fullmatch(parts[0]):
                return parts[0].lower()
    return None


def discover_campaigns(root: Path) -> tuple[list[dict], list[str]]:
    approvals, approval_errors = read_approvals(root)
    campaigns: list[dict] = []
    for path in sorted((root / "approved").glob("*.json")):
        manifest, errors = load_manifest(path)
        campaign_id = path.stem if manifest is None else manifest.get("id", path.stem)
        digest = sha256_file(path)
        approved = False
        approval_date = "9999-99-99"
        if not errors:
            matches = approvals.get(str(campaign_id), [])
            approved = any(item["digest"] == digest for item in matches)
            if matches:
                approval_date = min(item["date"] for item in matches if item["digest"] == digest) if approved else matches[0]["date"]
        campaigns.append(
            {
                "path": path,
                "id": str(campaign_id),
                "manifest": manifest,
                "errors": errors,
                "digest": digest,
                "approved": approved,
                "approval_date": approval_date,
                "listed": bool(approvals.get(str(campaign_id))),
            }
        )
    return campaigns, approval_errors


def status_lines(root: Path) -> list[str]:
    campaigns, approval_errors = discover_campaigns(root)
    lines = []
    for error in approval_errors:
        lines.append(f"approvals.tsv\tmalformed\t0\t0\t-\t{error}")
    for item in campaigns:
        campaign_id = item["id"]
        done, total = (0, 0)
        manifest = item["manifest"]
        if manifest:
            done, total = count_progress(manifest)
        result = read_result(root, campaign_id)
        next_try = read_next_try(root, campaign_id)
        heartbeat_age = "-"
        beat_path = campaign_state_dir(root, campaign_id) / HEARTBEAT_NAME
        if beat_path.exists():
            with contextlib.suppress(Exception):
                heartbeat_age = str(int((utc_now() - parse_utc(json.loads(beat_path.read_text(encoding="utf-8"))["time"])).total_seconds()))
        if item["errors"]:
            state = "invalid"
        elif not item["listed"]:
            state = "unapproved"
        elif not item["approved"]:
            state = "digest-mismatch"
        elif result:
            state, done, total, _ = result
        else:
            state = "pending"
        lines.append(f"{campaign_id}\t{state}\t{done}\t{total}\t{heartbeat_age}" + (f"\t{utc_text(next_try)}" if next_try else ""))
    return lines


def eligible_campaigns(root: Path, min_free_bytes: int) -> tuple[list[dict], bool]:
    campaigns, approval_errors = discover_campaigns(root)
    for error in approval_errors:
        append_runner_log(root, "global", error)
    if (root / "STOP").exists():
        append_runner_log(root, "global", "global STOP file present")
        return [], True
    if shutil.disk_usage(root).free < min_free_bytes:
        append_runner_log(root, "global", "free disk below threshold")
        return [], True
    done_ids = {path.stem for path in (root / "done").glob("*.result") if path.read_text(encoding="utf-8").startswith("DONE\t")}
    now = utc_now()
    eligible = []
    for item in campaigns:
        campaign_id = item["id"]
        if item["errors"]:
            append_runner_log(root, campaign_id, "; ".join(item["errors"]))
            continue
        if not item["listed"]:
            append_runner_log(root, campaign_id, "manifest digest is not listed in approvals.tsv")
            continue
        if not item["approved"]:
            append_runner_log(root, campaign_id, "manifest digest differs from approvals.tsv")
            continue
        result = read_result(root, campaign_id)
        if result and result[0] in {"DONE", "FAILED", "STOPPED"}:
            continue
        if result and result[0] == "HELD" and any("max-hours" in line for line in result_path(root, campaign_id).read_text(encoding="utf-8").splitlines()[1:]):
            continue
        next_try = read_next_try(root, campaign_id)
        if next_try and next_try > now:
            continue
        manifest = item["manifest"]
        if any(dep not in done_ids for dep in manifest["after"]):
            continue
        if (campaign_state_dir(root, campaign_id) / "STOP").exists():
            append_runner_log(root, campaign_id, "per-campaign STOP file present")
            continue
        head = read_checkout_head(Path(manifest["repo_dir"]))
        if head != manifest["ref"].lower():
            append_runner_log(root, campaign_id, f"checkout HEAD mismatch: {head or 'unresolved'}")
            continue
        driver_file = Path(manifest["driver"][0])
        if not driver_file.exists() and not shutil.which(manifest["driver"][0]):
            append_runner_log(root, campaign_id, "driver file absent")
            continue
        eligible.append(item)
    eligible.sort(key=lambda item: (item["manifest"]["priority"], item["approval_date"], item["id"]))
    return eligible, False


def start_process(manifest: dict, stdout_path: Path, stderr_path: Path) -> subprocess.Popen:
    stdout = stdout_path.open("ab")
    stderr = stderr_path.open("ab")
    env = os.environ.copy()
    env.update(manifest.get("env", {}))
    kwargs = {
        "cwd": manifest["cwd"],
        "env": env,
        "stdout": stdout,
        "stderr": stderr,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    try:
        return subprocess.Popen(manifest["driver"], **kwargs)
    except Exception:
        stdout.close()
        stderr.close()
        raise


def terminate_process(process: subprocess.Popen, grace_seconds: float) -> str:
    if process.poll() is not None:
        return "already-exited"
    with contextlib.suppress(Exception):
        process.terminate()
    try:
        process.wait(timeout=grace_seconds)
        return "polite"
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run([PROCESS_TREE_KILL_COMMAND, "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False)
        else:
            with contextlib.suppress(Exception):
                os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=grace_seconds)
        return "forced"


def write_heartbeat(root: Path, campaign_id: str, process: subprocess.Popen, attempt: int, started: float, manifest: dict) -> None:
    done, total = count_progress(manifest)
    payload = {
        "time": utc_text(),
        "pid": process.pid,
        "attempt": attempt,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "cases_done": done,
        "cases_total": total,
    }
    atomic_write_text(campaign_state_dir(root, campaign_id) / HEARTBEAT_NAME, json.dumps(payload, sort_keys=True) + "\n")


def licence_try_count_path(root: Path, campaign_id: str) -> Path:
    return campaign_state_dir(root, campaign_id) / f"licence-tries-{utc_now().date().isoformat()}.txt"


def read_counter(path: Path) -> int:
    if not path.exists():
        return 0
    with contextlib.suppress(ValueError):
        return int(path.read_text(encoding="utf-8").strip())
    return 0


def run_campaign(root: Path, item: dict, args: argparse.Namespace) -> None:
    manifest = item["manifest"]
    campaign_id = item["id"]
    state_dir = campaign_state_dir(root, campaign_id)
    state_dir.mkdir(parents=True, exist_ok=True)
    attempts = read_attempts(root, campaign_id)
    attempt_for_heartbeat = attempts + 1
    stdout_path = state_dir / "driver.stdout.log"
    stderr_path = state_dir / "driver.stderr.log"
    rotate_log(stdout_path)
    rotate_log(stderr_path)
    process = start_process(manifest, stdout_path, stderr_path)
    atomic_write_text(
        state_dir / "driver.json",
        json.dumps({"pid": process.pid, "start_time": utc_text(), "attempt": attempt_for_heartbeat}, sort_keys=True) + "\n",
    )
    started = time.monotonic()
    append_runner_log(root, campaign_id, f"started driver pid {process.pid}")
    outcome_reason = None
    while True:
        try:
            returncode = process.wait(timeout=args.heartbeat_seconds)
            break
        except subprocess.TimeoutExpired:
            write_heartbeat(root, campaign_id, process, attempt_for_heartbeat, started, manifest)
            if (root / "STOP").exists() or (state_dir / "STOP").exists():
                method = terminate_process(process, args.stop_grace_seconds)
                done, total = count_progress(manifest)
                write_result(root, campaign_id, "STOPPED", done, total, f"reason: stop-file", f"termination: {method}")
                append_runner_log(root, campaign_id, f"stopped by STOP file using {method}")
                return
            if (time.monotonic() - started) / 3600.0 >= float(manifest["max_hours"]):
                method = terminate_process(process, args.stop_grace_seconds)
                done, total = count_progress(manifest)
                write_result(root, campaign_id, "HELD", done, total, "reason: max-hours", f"termination: {method}")
                append_runner_log(root, campaign_id, f"held at max_hours using {method}")
                return
    write_heartbeat(root, campaign_id, process, attempt_for_heartbeat, started, manifest)
    done, total = count_progress(manifest)
    if returncode == 0 and (not manifest.get("progress") or done >= total):
        write_attempts(root, campaign_id, attempt_for_heartbeat)
        write_result(root, campaign_id, "DONE", done, total)
        write_next_try(root, campaign_id, None)
        append_runner_log(root, campaign_id, "completed DONE")
        return
    if returncode == 0 and manifest.get("progress") and done < total:
        outcome_reason = "progress-incomplete"
    elif returncode in set(manifest["licence_exit_codes"]):
        counter_path = licence_try_count_path(root, campaign_id)
        tries = read_counter(counter_path) + 1
        atomic_write_text(counter_path, f"{tries}\n")
        cap = int(manifest["retry"].get("licence_tries_per_day", DEFAULT_LICENCE_TRIES_PER_DAY))
        delay = float(args.backoff_minutes if args.backoff_minutes is not None else manifest["retry"]["backoff_minutes"])
        next_try = utc_now() + dt.timedelta(minutes=delay)
        if tries >= cap:
            next_try = utc_now() + dt.timedelta(days=1)
        write_next_try(root, campaign_id, next_try)
        write_attempts(root, campaign_id, attempts)
        write_result(root, campaign_id, "HELD", done, total, "reason: licence-unavailable", f"next-try: {utc_text(next_try)}")
        append_runner_log(root, campaign_id, "held for licence-unavailable")
        return
    else:
        outcome_reason = f"driver-exit-{returncode}"
    attempts += 1
    write_attempts(root, campaign_id, attempts)
    if attempts >= int(manifest["retry"]["max_attempts"]):
        write_result(root, campaign_id, "FAILED", done, total, f"reason: {outcome_reason}")
        append_runner_log(root, campaign_id, f"failed after attempt {attempts}: {outcome_reason}")
        return
    delay = float(args.backoff_minutes if args.backoff_minutes is not None else manifest["retry"]["backoff_minutes"])
    next_try = utc_now() + dt.timedelta(minutes=delay)
    write_next_try(root, campaign_id, next_try)
    write_result(root, campaign_id, "HELD", done, total, f"reason: {outcome_reason}", f"next-try: {utc_text(next_try)}")
    append_runner_log(root, campaign_id, f"held for retry after attempt {attempts}: {outcome_reason}")


def command_validate(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    manifest, errors = load_manifest(path)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{manifest['id']}\t{sha256_file(path)}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = Path(args.root)
    for line in status_lines(root):
        print(line)
    return 0


def command_run_once(args: argparse.Namespace) -> int:
    root = Path(args.root)
    for folder in ("approved", "state", "done"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    lock = RunnerLock(root, args.heartbeat_fresh_seconds)
    acquired, reason = lock.acquire()
    if not acquired:
        append_runner_log(root, "global", reason)
        return 0
    try:
        campaigns, blocked = eligible_campaigns(root, args.min_free_bytes)
        if blocked or not campaigns:
            return 0
        digest_now = sha256_file(campaigns[0]["path"])
        if digest_now != campaigns[0]["digest"]:
            append_runner_log(root, campaigns[0]["id"], "manifest digest changed before start")
            return 0
        run_campaign(root, campaigns[0], args)
        return 0
    finally:
        lock.release()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run approved solver campaigns.")
    parser.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    sub = parser.add_subparsers(dest="command", required=True)
    run_once = sub.add_parser("run-once")
    run_once.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    run_once.add_argument("--heartbeat-seconds", type=float, default=DEFAULT_HEARTBEAT_SECONDS)
    run_once.add_argument("--heartbeat-fresh-seconds", type=float, default=DEFAULT_HEARTBEAT_FRESH_SECONDS)
    run_once.add_argument("--stop-grace-seconds", type=float, default=DEFAULT_STOP_GRACE_SECONDS)
    run_once.add_argument("--min-free-bytes", type=int, default=DEFAULT_MIN_FREE_BYTES)
    run_once.add_argument("--backoff-minutes", type=float, default=None)
    run_once.set_defaults(func=command_run_once)
    status = sub.add_parser("status")
    status.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    status.set_defaults(func=command_status)
    validate = sub.add_parser("validate")
    validate.add_argument("manifest")
    validate.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    validate.set_defaults(func=command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(f"runner fault: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
