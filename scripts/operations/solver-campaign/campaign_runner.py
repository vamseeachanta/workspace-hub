#!/usr/bin/env python3
"""Approval-gated campaign runner for resumable licensed-solver drivers."""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path, PureWindowsPath


CREDENTIAL_TOKENS = {"TOKEN", "SECRET", "PASSWORD", "PASSWD", "CREDENTIAL", "KEY", "PASS", "PWD", "AUTH", "COOKIE"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
FULL_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")
LOCK_NAME = "runner.lock"
HEARTBEAT_NAME = "heartbeat.json"
TASK_MODE_NAME = "task-mode.txt"
DEFAULT_HEARTBEAT_SECONDS = 60.0
DEFAULT_STOP_GRACE_SECONDS = 20.0
DEFAULT_MIN_FREE_BYTES = 5 * 1024 * 1024 * 1024
DEFAULT_LICENCE_TRIES_PER_DAY = 3
LOG_LIMIT_BYTES = 1024 * 1024
LOG_ROTATIONS = 3
TASK_NAMESPACE = "http://schemas.microsoft.com/windows/2004/02/mit/task"
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
OPTIONAL_FIELDS = {"progress", "workers", "driver_file"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_declared_absolute(value: str) -> bool:
    return Path(value).is_absolute() or value.startswith("/") or PureWindowsPath(value).is_absolute()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> tuple[dict | None, list[str], str]:
    try:
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, [f"{path.name}: invalid JSON: {exc}"], ""
    if not isinstance(data, dict):
        return None, [f"{path.name}: manifest must be a JSON object"], digest
    errors = validate_manifest_data(data, path)
    return data, errors, digest


def env_name_looks_like_credential(name: str) -> bool:
    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", name.upper()) if token]
    return any(token in CREDENTIAL_TOKENS for token in tokens)


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
    else:
        driver_program = Path(driver[0])
        if not driver_program.is_absolute() and driver_program.parent != Path("."):
            errors.append("driver program path must be absolute or resolved from PATH")
    cwd = data.get("cwd")
    if not isinstance(cwd, str) or not is_declared_absolute(cwd):
        errors.append("cwd must be absolute")
    env = data.get("env")
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in getattr(env, "items", lambda: [])()):
        errors.append("env must be an object of string names and string values")
    elif any(env_name_looks_like_credential(name) for name in env):
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
    workers = data.get("workers")
    if workers is not None and (not isinstance(workers, int) or workers <= 0):
        errors.append("workers must be a positive integer")
    driver_file = data.get("driver_file")
    if driver_file is not None:
        if not isinstance(driver_file, str) or is_declared_absolute(driver_file) or ".." in Path(driver_file).parts:
            errors.append("driver_file must be a relative path inside repo_dir")
        elif isinstance(driver, list) and driver_file not in driver:
            errors.append("driver_file must be one of the driver arguments")
    return errors


def read_approvals(root: Path) -> tuple[dict[str, list[dict]], list[str]]:
    approvals: dict[str, list[dict]] = {}
    errors: list[str] = []
    path = root / "approvals.tsv"
    if not path.exists():
        return approvals, errors
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for number, line in enumerate(stream, 1):
            stripped = line.rstrip("\r\n")
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


def safe_log_id(path: Path, manifest: dict | None = None) -> str:
    if ID_RE.fullmatch(path.stem):
        return path.stem
    return "invalid"


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


def _windows_process_creation_time(pid: int) -> float | None:
    if os.name != "nt":
        return None
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        exit_code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != 259:
            return None
        creation = ctypes.c_ulonglong()
        exit_time = ctypes.c_ulonglong()
        kernel = ctypes.c_ulonglong()
        user = ctypes.c_ulonglong()
        if not kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            return None
        return round((creation.value / 10_000_000) - 11644473600, 3)
    finally:
        kernel32.CloseHandle(handle)


def _windows_handle_creation_time(handle: int) -> float | None:
    if os.name != "nt":
        return None
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    creation = ctypes.c_ulonglong()
    exit_time = ctypes.c_ulonglong()
    kernel = ctypes.c_ulonglong()
    user = ctypes.c_ulonglong()
    if not kernel32.GetProcessTimes(
        int(handle),
        ctypes.byref(creation),
        ctypes.byref(exit_time),
        ctypes.byref(kernel),
        ctypes.byref(user),
    ):
        return None
    return round((creation.value / 10_000_000) - 11644473600, 3)


def process_identity(pid: int) -> dict | None:
    if pid <= 0:
        return None
    if os.name == "nt":
        created = _windows_process_creation_time(pid)
        if created is None:
            return None
        return {"pid": pid, "creation_time": created}
    if not process_alive(pid):
        return None
    return {"pid": pid, "creation_time": None}


def process_alive(pid: int, creation_time: float | None = None) -> bool:
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    if os.name == "nt":
        created = _windows_process_creation_time(pid)
        if created is None:
            return False
        return creation_time is not None and created == round(float(creation_time), 3)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


class RunnerLock:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / LOCK_NAME
        self.held = False
        self.stream = None

    def acquire(self) -> tuple[bool, str]:
        self.root.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+", encoding="utf-8", newline="\n")
        try:
            if os.name == "nt":
                import msvcrt

                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            self.stream = None
            return False, "another runner holds the operating-system lock"
        record = {"pid": os.getpid(), "created_at": utc_text()}
        self.stream.seek(0)
        self.stream.truncate()
        json.dump(record, self.stream)
        self.stream.write("\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.held = True
        return True, "lock acquired"

    def release(self) -> None:
        if self.held:
            if self.stream is not None:
                with contextlib.suppress(OSError):
                    if os.name == "nt":
                        import msvcrt

                        self.stream.seek(0)
                        msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
                self.stream.close()
                self.stream = None
            self.held = False


def read_task_mode(root: Path) -> str:
    path = root / TASK_MODE_NAME
    if not path.exists():
        return "unknown"
    mode = path.read_text(encoding="utf-8").strip()
    return mode if mode in {"batch", "batch-password", "desktop"} else "unknown"


def read_driver_record(root: Path, campaign_id: str) -> dict | None:
    path = campaign_state_dir(root, campaign_id) / "driver.json"
    if not path.exists():
        return None
    with contextlib.suppress(Exception):
        record = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and isinstance(record.get("pid"), int):
            return record
    return None


def read_checkout_head(repo_dir: Path) -> str | None:
    git_path = repo_dir / ".git"
    if git_path.is_file():
        text = git_path.read_text(encoding="utf-8").strip()
        if not text.startswith("gitdir:"):
            return None
        git_path = (repo_dir / text.split(":", 1)[1].strip()).resolve()
    if not git_path.is_dir():
        return None
    common_path = git_path
    common_file = git_path / "commondir"
    if common_file.exists():
        common_text = common_file.read_text(encoding="utf-8").strip()
        common_path = (git_path / common_text).resolve() if common_text else git_path
    head_path = git_path / "HEAD"
    if not head_path.exists():
        return None
    head = head_path.read_text(encoding="utf-8").strip()
    if FULL_COMMIT_RE.fullmatch(head):
        return head.lower()
    if not head.startswith("ref:"):
        return None
    ref = head.split(":", 1)[1].strip()
    for ref_root in (git_path, common_path):
        loose = ref_root / ref
        if loose.exists():
            value = loose.read_text(encoding="utf-8").strip()
            return value.lower() if FULL_COMMIT_RE.fullmatch(value) else None
    packed = common_path / "packed-refs"
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
    paths = sorted((root / "approved").glob("*.json"))
    loaded: list[dict] = []
    casefold_ids: dict[str, set[str]] = {}
    for path in paths:
        manifest, errors, digest = load_manifest(path)
        campaign_id = safe_log_id(path, manifest)
        loaded.append({"path": path, "manifest": manifest, "errors": errors, "digest": digest, "id": str(campaign_id)})
        if manifest is not None and isinstance(manifest.get("id"), str) and manifest["id"] == path.stem:
            casefold_ids.setdefault(manifest["id"].casefold(), set()).add(manifest["id"])
    colliding = {folded for folded, ids in casefold_ids.items() if len(ids) > 1}
    for item in loaded:
        errors = list(item["errors"])
        campaign_id = item["id"]
        if item["manifest"] is not None and isinstance(item["manifest"].get("id"), str) and item["manifest"]["id"].casefold() in colliding:
            errors.append("campaign id differs only by case from another manifest")
        matches = approvals.get(campaign_id, [])
        digest_matches = [match for match in matches if match["digest"] == item["digest"]]
        valid_matches = [match for match in digest_matches if match["approval_ref"] != "policy"]
        approved = bool(valid_matches) and not errors
        approval_date = min(match["date"] for match in valid_matches) if valid_matches else (matches[0]["date"] if matches else "9999-99-99")
        approval_ref = valid_matches[0]["approval_ref"] if valid_matches else (digest_matches[0]["approval_ref"] if digest_matches else "")
        campaigns.append(
            {
                "path": item["path"],
                "id": campaign_id,
                "manifest": item["manifest"],
                "display_id": item["path"].name if campaign_id == "invalid" else campaign_id,
                "errors": errors,
                "digest": item["digest"],
                "approved": approved,
                "approval_date": approval_date,
                "approval_ref": approval_ref,
                "listed": bool(matches),
            }
        )
    return campaigns, approval_errors


def status_lines(root: Path) -> list[str]:
    campaigns, approval_errors = discover_campaigns(root)
    lines = [f"task-mode\t{read_task_mode(root)}"]
    if (root / "policy.json").exists():
        lines.append("policy.json\tignored\t0\t0\t-\tstanding approval is not available in this release")
    for error in approval_errors:
        lines.append(f"approvals.tsv\tmalformed\t0\t0\t-\t{error}")
    for item in campaigns:
        campaign_id = item["id"]
        display_id = item.get("display_id", campaign_id)
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
        elif not item["approved"] and item.get("approval_ref") == "policy":
            state = "unapproved"
        elif not item["approved"]:
            state = "digest-mismatch"
        elif result:
            state, done, total, _ = result
        elif (record := read_driver_record(root, campaign_id)) and process_alive(
            int(record.get("pid", -1)), record.get("creation_time")
        ):
            state = "running"
        else:
            state = "pending"
        lines.append(f"{display_id}\t{state}\t{done}\t{total}\t{heartbeat_age}" + (f"\t{utc_text(next_try)}" if next_try else ""))
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
    failed_ids = {path.stem for path in (root / "done").glob("*.result") if path.read_text(encoding="utf-8").startswith("FAILED\t")}
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
            if item.get("approval_ref") == "policy":
                append_runner_log(root, campaign_id, "approval reference policy is not available in this release")
            else:
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
        failed_after = [dep for dep in manifest["after"] if dep in failed_ids]
        if failed_after:
            append_runner_log(root, campaign_id, f"after dependency failed: {', '.join(failed_after)}")
            continue
        if any(dep not in done_ids for dep in manifest["after"]):
            continue
        low_disk = False
        for disk_path in [Path(manifest["cwd"])] + [
            Path(manifest["progress"]["glob"]).parent for _ in [0] if manifest.get("progress") and is_declared_absolute(manifest["progress"]["glob"])
        ]:
            if disk_path.exists() and shutil.disk_usage(disk_path).free < min_free_bytes:
                append_runner_log(root, campaign_id, f"free disk below threshold for {disk_path}")
                low_disk = True
                break
        if low_disk:
            continue
        if (campaign_state_dir(root, campaign_id) / "STOP").exists():
            append_runner_log(root, campaign_id, "per-campaign STOP file present")
            continue
        head = read_checkout_head(Path(manifest["repo_dir"]))
        if head != manifest["ref"].lower():
            append_runner_log(root, campaign_id, f"checkout HEAD mismatch: {head or 'unresolved'}")
            continue
        driver_file = Path(manifest["driver"][0])
        declared_driver = manifest.get("driver_file")
        if declared_driver and not (Path(manifest["repo_dir"]) / declared_driver).exists():
            append_runner_log(root, campaign_id, "driver_file absent")
            continue
        if not driver_file.exists() and not shutil.which(manifest["driver"][0]):
            append_runner_log(root, campaign_id, "driver file absent")
            continue
        eligible.append(item)
    eligible.sort(key=lambda item: (item["manifest"]["priority"], item["approval_date"], item["id"]))
    return eligible, False



class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("cntUsage", ctypes.c_ulong),
        ("th32ThreadID", ctypes.c_ulong),
        ("th32OwnerProcessID", ctypes.c_ulong),
        ("tpBasePri", ctypes.c_long),
        ("tpDeltaPri", ctypes.c_long),
        ("dwFlags", ctypes.c_ulong),
    ]


def resume_windows_process_threads(pid: int) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, 0)
    if snapshot == -1:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")
    resumed = 0
    try:
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(entry)
        has_entry = kernel32.Thread32First(snapshot, ctypes.byref(entry))
        while has_entry:
            if entry.th32OwnerProcessID == pid:
                thread = kernel32.OpenThread(0x0002, False, entry.th32ThreadID)
                if not thread:
                    raise OSError(ctypes.get_last_error(), "OpenThread failed")
                try:
                    if kernel32.ResumeThread(thread) == 0xFFFFFFFF:
                        raise OSError(ctypes.get_last_error(), "ResumeThread failed")
                    resumed += 1
                finally:
                    kernel32.CloseHandle(thread)
            has_entry = kernel32.Thread32Next(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    if resumed == 0:
        raise OSError("no process thread was resumed")


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", ctypes.c_ulong),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_ulong),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_ulong),
        ("SchedulingClass", ctypes.c_ulong),
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def create_windows_job_for_process(process: subprocess.Popen) -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObjectW failed")
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = 0x00002000
    ok = kernel32.SetInformationJobObject(
        job,
        9,
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not ok:
        kernel32.CloseHandle(job)
        raise OSError(ctypes.get_last_error(), "SetInformationJobObject failed")
    if not kernel32.AssignProcessToJobObject(job, int(process._handle)):  # noqa: SLF001
        kernel32.CloseHandle(job)
        raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject failed")
    return job


def close_windows_job(job: int | None) -> None:
    if os.name == "nt" and job:
        ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(job)


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
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000004
    else:
        kwargs["start_new_session"] = True
    try:
        process = subprocess.Popen(manifest["driver"], **kwargs)
        if os.name == "nt":
            process._solver_job = create_windows_job_for_process(process)  # noqa: SLF001
            try:
                resume_windows_process_threads(process.pid)
            except Exception:
                ctypes.WinDLL("kernel32", use_last_error=True).TerminateJobObject(process._solver_job, 1)  # noqa: SLF001
                raise
        else:
            process._solver_job = None  # noqa: SLF001
        return process
    except Exception:
        stdout.close()
        stderr.close()
        raise


def terminate_process(process: subprocess.Popen, grace_seconds: float) -> str:
    if process.poll() is not None:
        return "already-exited"
    with contextlib.suppress(Exception):
        if os.name == "nt":
            ctypes.WinDLL("kernel32", use_last_error=True).GenerateConsoleCtrlEvent(1, process.pid)
        else:
            os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=grace_seconds)
        return "polite"
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            job = getattr(process, "_solver_job", None)
            if job:
                ctypes.WinDLL("kernel32", use_last_error=True).TerminateJobObject(job, 1)
            else:
                process.kill()
        else:
            with contextlib.suppress(Exception):
                os.killpg(process.pid, signal.SIGKILL)
        try:
            process.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(Exception):
                process.kill()
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
    try:
        process = start_process(manifest, stdout_path, stderr_path)
    except Exception as exc:  # noqa: BLE001
        write_attempts(root, campaign_id, attempt_for_heartbeat)
        outcome_reason = f"driver-start-failed: {exc}"
        if attempt_for_heartbeat >= int(manifest["retry"]["max_attempts"]):
            write_result(root, campaign_id, "FAILED", 0, 0, f"reason: {outcome_reason}")
            append_runner_log(root, campaign_id, f"failed after attempt {attempt_for_heartbeat}: {outcome_reason}")
            return "start-failed"
        delay = float(args.backoff_minutes if args.backoff_minutes is not None else manifest["retry"]["backoff_minutes"])
        next_try = utc_now() + dt.timedelta(minutes=delay)
        write_next_try(root, campaign_id, next_try)
        write_result(root, campaign_id, "HELD", 0, 0, f"reason: {outcome_reason}", f"next-try: {utc_text(next_try)}")
        append_runner_log(root, campaign_id, f"held for retry after attempt {attempt_for_heartbeat}: {outcome_reason}")
        return "start-failed"
    created_from_handle = _windows_handle_creation_time(process._handle) if os.name == "nt" else None  # noqa: SLF001
    identity = {"pid": process.pid, "creation_time": created_from_handle} if created_from_handle is not None else process_identity(process.pid)
    identity = identity or {"pid": process.pid, "creation_time": None}
    write_attempts(root, campaign_id, attempt_for_heartbeat)
    atomic_write_text(
        state_dir / "driver.json",
        json.dumps(
            {
                "pid": process.pid,
                "creation_time": identity.get("creation_time"),
                "start_time": utc_text(),
                "attempt": attempt_for_heartbeat,
            },
            sort_keys=True,
        )
        + "\n",
    )
    started = time.monotonic()
    append_runner_log(root, campaign_id, f"started driver pid {process.pid}")
    write_heartbeat(root, campaign_id, process, attempt_for_heartbeat, started, manifest)
    outcome_reason = None
    try:
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
    finally:
        close_windows_job(getattr(process, "_solver_job", None))
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
    manifest, errors, digest = load_manifest(path)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{manifest['id']}\t{digest}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = Path(args.root)
    for line in status_lines(root):
        print(line)
    return 0


def task_definition_xml(mode: str, account: str, wrapper: str, root: str) -> str:
    if mode not in {"batch", "batch-password", "desktop"}:
        raise ValueError("unknown mode")
    ET.register_namespace("", TASK_NAMESPACE)
    task = ET.Element(f"{{{TASK_NAMESPACE}}}Task", {"version": "1.4"})
    registration = ET.SubElement(task, f"{{{TASK_NAMESPACE}}}RegistrationInfo")
    ET.SubElement(registration, f"{{{TASK_NAMESPACE}}}Description").text = "Solver campaign runner"
    triggers = ET.SubElement(task, f"{{{TASK_NAMESPACE}}}Triggers")
    calendar = ET.SubElement(triggers, f"{{{TASK_NAMESPACE}}}CalendarTrigger")
    ET.SubElement(calendar, f"{{{TASK_NAMESPACE}}}StartBoundary").text = "2026-01-01T00:00:00"
    repetition = ET.SubElement(calendar, f"{{{TASK_NAMESPACE}}}Repetition")
    ET.SubElement(repetition, f"{{{TASK_NAMESPACE}}}Interval").text = "PT10M"
    schedule = ET.SubElement(calendar, f"{{{TASK_NAMESPACE}}}ScheduleByDay")
    ET.SubElement(schedule, f"{{{TASK_NAMESPACE}}}DaysInterval").text = "1"
    if mode == "desktop":
        logon_trigger = ET.SubElement(triggers, f"{{{TASK_NAMESPACE}}}LogonTrigger")
        ET.SubElement(logon_trigger, f"{{{TASK_NAMESPACE}}}UserId").text = account
    else:
        ET.SubElement(triggers, f"{{{TASK_NAMESPACE}}}BootTrigger")
    principals = ET.SubElement(task, f"{{{TASK_NAMESPACE}}}Principals")
    principal = ET.SubElement(principals, f"{{{TASK_NAMESPACE}}}Principal", {"id": "Author"})
    ET.SubElement(principal, f"{{{TASK_NAMESPACE}}}UserId").text = account
    logon = {"batch": "S4U", "batch-password": "Password", "desktop": "InteractiveToken"}[mode]
    ET.SubElement(principal, f"{{{TASK_NAMESPACE}}}LogonType").text = logon
    ET.SubElement(principal, f"{{{TASK_NAMESPACE}}}RunLevel").text = "LeastPrivilege"
    settings = ET.SubElement(task, f"{{{TASK_NAMESPACE}}}Settings")
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}MultipleInstancesPolicy").text = "IgnoreNew"
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}DisallowStartIfOnBatteries").text = "false"
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}StopIfGoingOnBatteries").text = "false"
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}RunOnlyIfIdle").text = "false"
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}Priority").text = "5"
    ET.SubElement(settings, f"{{{TASK_NAMESPACE}}}ExecutionTimeLimit").text = "PT0S"
    actions = ET.SubElement(task, f"{{{TASK_NAMESPACE}}}Actions", {"Context": "Author"})
    exec_action = ET.SubElement(actions, f"{{{TASK_NAMESPACE}}}Exec")
    ET.SubElement(exec_action, f"{{{TASK_NAMESPACE}}}Command").text = "cmd.exe"
    ET.SubElement(exec_action, f"{{{TASK_NAMESPACE}}}Arguments").text = f'/d /c ""{wrapper}" "{root}""'
    xml = ET.tostring(task, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-16"?>\n' + xml + "\n"


def command_task_definition(args: argparse.Namespace) -> int:
    xml = task_definition_xml(args.mode, args.account, args.wrapper, args.campaign_root)
    if args.output:
        Path(args.output).write_text(xml, encoding="utf-16", newline="\n")
    else:
        print(xml, end="")
    return 0


def command_run_once(args: argparse.Namespace) -> int:
    root = Path(args.root)
    for folder in ("approved", "state", "done"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    lock = RunnerLock(root)
    acquired, reason = lock.acquire()
    if not acquired:
        append_runner_log(root, "global", reason)
        return 0
    try:
        if (root / "policy.json").exists():
            append_runner_log(root, "global", "standing approval is not available in this release")
        for record_path in sorted((root / "state").glob("*/driver.json")):
            campaign_id = record_path.parent.name
            record = read_driver_record(root, campaign_id)
            if record and process_alive(int(record.get("pid", -1)), record.get("creation_time")):
                append_runner_log(root, campaign_id, "recorded driver is still running; no second driver started")
                return 0
        campaigns, blocked = eligible_campaigns(root, args.min_free_bytes)
        if blocked:
            return 0
        for campaign in campaigns:
            digest_now = sha256_file(campaign["path"])
            if digest_now != campaign["digest"]:
                append_runner_log(root, campaign["id"], "manifest digest changed before start")
                continue
            outcome = run_campaign(root, campaign, args)
            if outcome == "start-failed":
                continue
            return 0
        return 0
    finally:
        lock.release()


def parse_task_readback(path: Path) -> tuple[str | None, str | None]:
    data = path.read_bytes()
    last_error: Exception | None = None
    encodings = ["utf-16", "utf-8-sig", "utf-8"]
    encodings.append("mbcs" if os.name == "nt" else "cp1252")
    for encoding in encodings:
        try:
            root = ET.fromstring(data.decode(encoding))
            return find_task_text(root, "LogonType"), find_task_text(root, "UserId")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise ValueError(f"task readback XML could not be parsed: {last_error}")


def find_task_text(root: ET.Element, name: str) -> str | None:
    found = root.find(f".//{{{TASK_NAMESPACE}}}{name}")
    return found.text if found is not None else None


def command_task_readback(args: argparse.Namespace) -> int:
    try:
        logon, account = parse_task_readback(Path(args.xml))
    except Exception as exc:  # noqa: BLE001
        print(f"Task readback parse failed: {exc}")
        return 1
    print(f"Registered task readback LogonType: {logon or ''}")
    print(f"Registered task readback account: {account or ''}")
    if (logon or "").casefold() == args.expected_logon.casefold() and (account or "").casefold() == args.account.casefold():
        print("Registered task readback matches requested mode and account.")
        return 0
    print("Registered task readback did not match requested mode and account.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run approved solver campaigns.")
    parser.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    sub = parser.add_subparsers(dest="command", required=True)
    run_once = sub.add_parser("run-once")
    run_once.add_argument("--root", default=os.environ.get("SOLVER_CAMPAIGN_ROOT") or str(default_root()))
    run_once.add_argument("--heartbeat-seconds", type=float, default=DEFAULT_HEARTBEAT_SECONDS)
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
    task_definition = sub.add_parser("task-definition")
    task_definition.add_argument("mode", choices=("batch", "batch-password", "desktop"))
    task_definition.add_argument("--account", default="{ACCOUNT}")
    task_definition.add_argument("--wrapper", default="{WRAPPER}")
    task_definition.add_argument("--campaign-root", default="{CAMPAIGN_ROOT}")
    task_definition.add_argument("--output")
    task_definition.set_defaults(func=command_task_definition)
    task_readback = sub.add_parser("task-readback")
    task_readback.add_argument("xml")
    task_readback.add_argument("--expected-logon", required=True)
    task_readback.add_argument("--account", required=True)
    task_readback.set_defaults(func=command_task_readback)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001
        with contextlib.suppress(Exception):
            if hasattr(args, "root"):
                append_runner_log(Path(args.root), "global", f"runner fault: {exc}")
        print(f"runner fault: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
