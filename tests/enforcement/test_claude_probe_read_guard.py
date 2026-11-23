"""Tests for the ephemeral Claude Read probe guard."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


GUARD = Path(__file__).parents[2] / "scripts/agents/claude_probe_read_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("read_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload(path: str, tool: str = "Read", tool_use_id: str = "tool-123") -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_use_id": tool_use_id,
        "tool_input": {"file_path": path},
    }


def _run(
    allowed: Path,
    audit: Path,
    payload: dict | str,
    *,
    digest: str | None = None,
) -> subprocess.CompletedProcess[str]:
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(GUARD),
            "--allowed-file",
            str(allowed),
            "--expected-sha256",
            digest or _sha256(allowed),
            "--audit-file",
            str(audit),
        ],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def _decision(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"]


def _audit(audit: Path) -> list[dict]:
    return [json.loads(line) for line in audit.read_text().splitlines()]


@pytest.fixture
def fixture(tmp_path: Path) -> tuple[Path, Path]:
    allowed = tmp_path / "probe-fixture.md"
    allowed.write_text("harmless read canary\n")
    audit = tmp_path / "private/audit.jsonl"
    audit.parent.mkdir()
    return allowed, audit


def test_allows_only_exact_digest_bound_read_and_audits_tool_id(fixture) -> None:
    allowed, audit = fixture

    result = _run(allowed, audit, _payload(str(allowed), tool_use_id="read-7"))

    output = _decision(result)
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "allow"
    records = _audit(audit)
    assert records[0]["tool_use_id"] == "read-7"
    assert records[0]["requested_path"] == str(allowed.resolve())
    assert records[0]["decision"] == "allow"
    assert "harmless read canary" not in audit.read_text()


@pytest.mark.parametrize("tool", ["Write", "Edit", "Bash"])
def test_denies_every_other_tool(fixture, tool: str) -> None:
    allowed, audit = fixture

    output = _decision(_run(allowed, audit, _payload(str(allowed), tool=tool)))

    assert output["permissionDecision"] == "deny"
    assert _audit(audit)[0]["reason"] == "tool_not_read"


def test_denies_other_path_and_lexical_traversal(fixture) -> None:
    allowed, audit = fixture
    other = allowed.parent / "other.md"
    other.write_text("other\n")
    traversing = str(allowed.parent / "unused" / ".." / allowed.name)

    other_result = _decision(_run(allowed, audit, _payload(str(other))))
    traversal_result = _decision(_run(allowed, audit, _payload(traversing)))

    assert other_result["permissionDecision"] == "deny"
    assert traversal_result["permissionDecision"] == "deny"
    assert [row["decision"] for row in _audit(audit)] == ["deny", "deny"]


def test_denies_symlinked_allowed_file_or_parent(fixture, tmp_path: Path) -> None:
    allowed, audit = fixture
    link = tmp_path / "linked-fixture.md"
    linked_parent = tmp_path / "linked-parent"
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    nested = real_parent / "probe.md"
    nested.write_text("nested\n")
    try:
        link.symlink_to(allowed)
        linked_parent.symlink_to(real_parent, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    direct = _decision(_run(link, audit, _payload(str(link))))
    parent = _decision(
        _run(linked_parent / "probe.md", audit, _payload(str(linked_parent / "probe.md")))
    )

    assert direct["permissionDecision"] == "deny"
    assert parent["permissionDecision"] == "deny"


def test_denies_digest_drift(fixture) -> None:
    allowed, audit = fixture

    output = _decision(
        _run(allowed, audit, _payload(str(allowed)), digest="0" * 64)
    )

    assert output["permissionDecision"] == "deny"
    assert _audit(audit)[0]["reason"] == "allowed_digest_mismatch"


@pytest.mark.parametrize("malformed", ["{", "[]", "null", "{}"])
def test_malformed_input_fails_closed_with_audit(fixture, malformed: str) -> None:
    allowed, audit = fixture

    output = _decision(_run(allowed, audit, malformed))

    assert output["permissionDecision"] == "deny"
    assert _audit(audit)[0]["decision"] == "deny"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_use_id": {"invalid": True},
            "tool_input": {"file_path": 123},
        },
        {
            "hook_event_name": "PreToolUse",
            "tool_name": 42,
            "tool_use_id": ["invalid"],
            "tool_input": {"file_path": ["invalid"]},
        },
    ],
)
def test_malformed_field_types_exit_two_without_traceback(fixture, payload: dict) -> None:
    allowed, audit = fixture

    result = _run(allowed, audit, payload)

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() == "guard audit unavailable"


def test_zero_progress_audit_write_fails_closed(fixture, monkeypatch) -> None:
    allowed, audit = fixture
    module = _load_guard()
    calls = 0

    def zero_then_fail(_descriptor, _view):
        nonlocal calls
        calls += 1
        if calls == 1:
            return 0
        raise AssertionError("write retried after zero progress")

    monkeypatch.setattr(module.os, "write", zero_then_fail)
    with pytest.raises(module.GuardError, match="audit_write_failed"):
        module.append_audit(
            audit, "deny", "test", "Read", "tool-1", str(allowed)
        )
    assert calls == 1


def test_audit_append_refuses_symlink(fixture, tmp_path: Path) -> None:
    allowed, _ = fixture
    real_audit = tmp_path / "real-audit.jsonl"
    real_audit.write_text("")
    audit_link = tmp_path / "audit-link.jsonl"
    try:
        audit_link.symlink_to(real_audit)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    result = _run(allowed, audit_link, _payload(str(allowed)))

    assert result.returncode != 0
    assert real_audit.read_text() == ""


def test_audit_cannot_alias_allowed_fixture(fixture) -> None:
    allowed, _ = fixture
    before = allowed.read_bytes()

    result = _run(allowed, allowed, _payload(str(allowed)))

    assert result.returncode != 0
    assert allowed.read_bytes() == before


def test_audit_rejects_linked_ancestor(fixture, tmp_path: Path) -> None:
    allowed, _ = fixture
    real_root = tmp_path / "real-audit-root"
    nested = real_root / "nested"
    nested.mkdir(parents=True)
    linked_root = tmp_path / "linked-audit-root"
    try:
        linked_root.symlink_to(real_root, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")
    audit = linked_root / "nested/audit.jsonl"

    result = _run(allowed, audit, _payload(str(allowed)))

    assert result.returncode != 0
    assert not (nested / "audit.jsonl").exists()
