#!/usr/bin/env python3
"""Permit one digest-bound Read during an ephemeral Claude native probe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys
from typing import Any


MAX_INPUT_BYTES = 65_536
MAX_FIXTURE_BYTES = 1_048_576
REPARSE_ATTRIBUTE = 0x400


class GuardError(Exception):
    """A fail-closed request or filesystem condition."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def is_link_or_reparse(path: Path, metadata: os.stat_result | None = None) -> bool:
    details = metadata or path.lstat()
    return path.is_symlink() or bool(
        getattr(details, "st_file_attributes", 0) & REPARSE_ATTRIBUTE
    )


def require_absolute_clean(value: str, label: str) -> Path:
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    path = Path(value)
    if (
        not value
        or not path.is_absolute()
        or any(part in {".", ".."} for part in (*posix.parts, *windows.parts))
    ):
        raise GuardError(f"{label}_path_invalid")
    return path


def regular_path(path: Path, label: str) -> tuple[os.stat_result, bytes]:
    chain = list(reversed(path.parents)) + [path]
    for entry in chain:
        try:
            details = entry.lstat()
        except OSError as exc:
            raise GuardError(f"{label}_path_unavailable") from exc
        if is_link_or_reparse(entry, details):
            raise GuardError(f"{label}_path_linked")
    details = path.lstat()
    if not stat.S_ISREG(details.st_mode) or details.st_size > MAX_FIXTURE_BYTES:
        raise GuardError(f"{label}_not_bounded_regular_file")
    data = path.read_bytes()
    after = path.lstat()
    if (
        (details.st_dev, details.st_ino, details.st_size, details.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    ):
        raise GuardError(f"{label}_changed_during_read")
    return after, data


def safe_directory(path: Path, label: str) -> None:
    for entry in list(reversed(path.parents)) + [path]:
        try:
            details = entry.lstat()
        except OSError as exc:
            raise GuardError(f"{label}_path_unavailable") from exc
        if is_link_or_reparse(entry, details) or not stat.S_ISDIR(details.st_mode):
            raise GuardError(f"{label}_path_unsafe")


def parse_event() -> tuple[dict[str, Any] | None, str | None]:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        return None, "input_too_large"
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "malformed_json"
    if not isinstance(value, dict):
        return None, "input_not_object"
    return value, None


def evaluate(
    event: dict[str, Any] | None,
    parse_error: str | None,
    allowed_file: Path,
    expected_sha256: str,
) -> tuple[str, str, str | None, str | None, str | None]:
    if parse_error:
        return "deny", parse_error, None, None, None
    assert event is not None
    raw_tool_name = event.get("tool_name")
    raw_tool_use_id = event.get("tool_use_id")
    tool_input = event.get("tool_input")
    raw_requested = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if (
        (raw_tool_name is not None and not isinstance(raw_tool_name, str))
        or (raw_tool_use_id is not None and not isinstance(raw_tool_use_id, str))
        or (raw_requested is not None and not isinstance(raw_requested, str))
    ):
        raise GuardError("event_field_type_invalid")
    tool_name = raw_tool_name if isinstance(raw_tool_name, str) else None
    tool_use_id = raw_tool_use_id if isinstance(raw_tool_use_id, str) else None
    requested = raw_requested if isinstance(raw_requested, str) else None
    if event.get("hook_event_name") != "PreToolUse":
        return "deny", "event_not_pretooluse", tool_name, tool_use_id, requested
    if raw_tool_name != "Read":
        return "deny", "tool_not_read", tool_name, tool_use_id, requested
    if not tool_use_id:
        return "deny", "tool_use_id_missing", tool_name, None, requested
    if requested is None:
        return "deny", "file_path_missing", tool_name, tool_use_id, None
    try:
        requested_path = require_absolute_clean(requested, "requested")
        allowed_metadata, allowed_bytes = regular_path(allowed_file, "allowed")
    except GuardError as exc:
        return "deny", str(exc), tool_name, tool_use_id, requested
    if os.path.normcase(os.path.abspath(requested_path)) != os.path.normcase(
        os.path.abspath(allowed_file)
    ):
        return "deny", "path_not_allowed", tool_name, tool_use_id, requested
    if sha256_bytes(allowed_bytes) != expected_sha256:
        return "deny", "allowed_digest_mismatch", tool_name, tool_use_id, requested
    if allowed_metadata.st_size != len(allowed_bytes):
        return "deny", "allowed_size_mismatch", tool_name, tool_use_id, requested
    return "allow", "exact_pinned_probe_fixture", tool_name, tool_use_id, str(allowed_file)


def append_audit(
    audit_file: Path,
    decision: str,
    reason: str,
    tool_name: str | None,
    tool_use_id: str | None,
    requested: str | None,
) -> None:
    parent = audit_file.parent
    safe_directory(parent, "audit")
    if os.path.lexists(audit_file):
        details = audit_file.lstat()
        if is_link_or_reparse(audit_file, details) or not stat.S_ISREG(details.st_mode):
            raise GuardError("audit_file_unsafe")
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_use_id": tool_use_id,
        "tool_name": tool_name,
        "requested_path": requested,
        "requested_path_sha256": sha256_bytes(requested.encode()) if requested else None,
        "decision": decision,
        "reason": reason,
    }
    data = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(audit_file, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise GuardError("audit_write_failed")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def output(decision: str, reason: str) -> None:
    value = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(value, separators=(",", ":")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allowed-file", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--audit-file", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        allowed = require_absolute_clean(args.allowed_file, "allowed")
        audit = require_absolute_clean(args.audit_file, "audit")
        if re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_sha256) is None:
            raise GuardError("expected_digest_invalid")
        if os.path.normcase(os.path.abspath(allowed)) == os.path.normcase(
            os.path.abspath(audit)
        ) or (os.path.lexists(audit) and os.path.samefile(allowed, audit)):
            raise GuardError("audit_aliases_allowed_file")
        event, parse_error = parse_event()
        decision, reason, tool, tool_id, requested = evaluate(
            event, parse_error, allowed, args.expected_sha256.lower()
        )
        append_audit(audit, decision, reason, tool, tool_id, requested)
        output(decision, reason)
        return 0
    except Exception:
        print("guard audit unavailable", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
