#!/usr/bin/env python3
"""Dry-run-first Linux cron issue orchestrator for GitHub-label dispatch (#2740)."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

TOKEN_RE = re.compile(r"\b(?:\d{6,}:[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]+)\b")
PRIVATE_METADATA_RE = re.compile(r"(?i)(allowed[_ -]?users?|chat[_ -]?id|user[_ -]?ids?)\s*[:=]\s*[^\s;,]+")
REDACTION = "[REDACTED]"

STATUS_LABELS = {"status:needs-plan", "status:plan-review", "status:plan-approved"}
PRIORITY_RANK = {
    "priority:critical": 0,
    "priority:P1": 1,
    "priority:high": 2,
    "priority:medium": 3,
    "priority:low": 4,
}


def _label_names(issue: dict[str, Any]) -> list[str]:
    labels = issue.get("labels") or []
    names: list[str] = []
    for label in labels:
        if isinstance(label, dict) and isinstance(label.get("name"), str):
            names.append(label["name"])
        elif isinstance(label, str):
            names.append(label)
    return names


def _priority_key(issue: dict[str, Any]) -> tuple[int, str, int]:
    labels = set(_label_names(issue))
    rank = min((PRIORITY_RANK[label] for label in labels if label in PRIORITY_RANK), default=99)
    updated = str(issue.get("updatedAt") or issue.get("updated_at") or "")
    try:
        number = int(issue.get("number") or 0)
    except (TypeError, ValueError):
        number = 0
    return rank, updated, number


def _redact(text: str) -> str:
    redacted = TOKEN_RE.sub(REDACTION, text)
    redacted = re.sub(r"\*{3,}", REDACTION, redacted)
    redacted = PRIVATE_METADATA_RE.sub(lambda match: match.group(0).split("=", 1)[0].split(":", 1)[0] + f"={REDACTION}", redacted)
    redacted = re.sub(r"\b\d{5,}\b", REDACTION, redacted)
    return redacted


def _redact_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_payload(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_redact_payload(child) for child in value]
    if isinstance(value, str):
        return _redact(value)
    return value


def _machine_labels(labels: list[str]) -> list[str]:
    return [label for label in labels if label.startswith("machine:")]


def _agent_labels(labels: list[str]) -> list[str]:
    return [label for label in labels if label.startswith("agent:")]


def _status_labels(labels: list[str]) -> list[str]:
    return [label for label in labels if label in STATUS_LABELS]


def _base_action(issue: dict[str, Any], labels: list[str]) -> dict[str, Any]:
    return {
        "issue": issue.get("number"),
        "title": issue.get("title"),
        "url": issue.get("url"),
        "labels": labels,
        "execute_provider": False,
    }


def _blocked(issue: dict[str, Any], labels: list[str], reason: str) -> dict[str, Any]:
    action = _base_action(issue, labels)
    action.update({"decision": "blocked", "reason": reason})
    return action


def _eligible_status_action(issue: dict[str, Any], labels: list[str], marker_dir: Path, lease_acquired: bool | None, worktree_clean: bool) -> dict[str, Any]:
    status = _status_labels(labels)
    if len(status) != 1:
        return _blocked(issue, labels, "expected exactly one status label")

    action = _base_action(issue, labels)
    if status[0] == "status:needs-plan":
        action.update({"decision": "report_only", "mode": "planning_candidate"})
        return action
    if status[0] == "status:plan-review":
        action.update({"decision": "report_only", "mode": "review_candidate"})
        return action

    marker = marker_dir / f"{issue.get('number')}.md"
    if not marker.exists():
        return _blocked(issue, labels, "missing local plan approval marker")

    issue_number = issue.get("number")
    lease_ref = f"refs/heads/dispatch/leases/{issue_number}-implementation"
    action.update({"mode": "implementation", "lease_ref": lease_ref})
    if not worktree_clean:
        action.update({"decision": "blocked", "reason": "execution worktree is not clean"})
        return action
    if lease_acquired is not True:
        action.update({"decision": "awaiting_lease"})
        return action
    action.update({"decision": "ready_to_execute", "execute_provider": True})
    return action


def plan_tick(
    issues: list[dict[str, Any]],
    *,
    host_machine_label: str,
    plan_marker_dir: str | Path,
    readiness: dict[str, Any] | None = None,
    lease_acquired: bool | None = None,
    worktree_clean: bool = True,
) -> list[dict[str, Any]]:
    """Return fail-closed dry-run actions for this host's issue queue."""
    readiness = readiness or {"status": "pass"}
    if readiness.get("status") != "pass":
        return [
            {
                "issue": None,
                "decision": "blocked",
                "reason": "host readiness failed",
                "failures": readiness.get("failures", []),
                "execute_provider": False,
            }
        ]

    marker_dir = Path(plan_marker_dir)
    actions: list[dict[str, Any]] = []
    for issue in sorted(issues, key=_priority_key):
        labels = _label_names(issue)
        machine_labels = _machine_labels(labels)
        agent_labels = _agent_labels(labels)

        if len(machine_labels) != 1:
            actions.append(_blocked(issue, labels, "expected exactly one machine label"))
            continue
        if machine_labels[0] != host_machine_label:
            continue
        if len(agent_labels) != 1:
            actions.append(_blocked(issue, labels, "expected exactly one agent label"))
            continue
        actions.append(_eligible_status_action(issue, labels, marker_dir, lease_acquired, worktree_clean))
    return actions


def format_status_comment(action: dict[str, Any]) -> str:
    """Format a redacted issue status comment for a single action."""
    issue = action.get("issue")
    decision = action.get("decision", "unknown")
    reason = action.get("reason") or action.get("mode") or "no additional detail"
    lines = ["Linux cron issue orchestrator status (#2740).", "", f"- Issue: {issue}", f"- Decision: {decision}", f"- Detail: {reason}", f"- Provider execution: {bool(action.get('execute_provider'))}"]
    return _redact("\n".join(lines))


@contextlib.contextmanager
def no_overlap_lock(lock_path: str | Path) -> Iterator[None]:
    """Hold an exclusive non-blocking flock for one cron tick."""
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def try_no_overlap_lock(lock_path: str | Path) -> bool:
    """Return whether the lock can be acquired right now."""
    try:
        with no_overlap_lock(lock_path):
            return True
    except BlockingIOError:
        return False


def _load_issues(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("issues JSON must be a list")
    return [item for item in payload if isinstance(item, dict)]


def _load_readiness(path: str | Path | None) -> dict[str, Any]:
    """Load a redacted host-readiness summary for this cron tick."""
    if path is None:
        return {"status": "fail", "failures": ["readiness evidence missing"]}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("readiness JSON must be an object")
    if "status" in payload:
        return payload
    # Accept the broader readiness-tool shape for single-host reports.
    if payload.get("overall_status") == "pass":
        return {"status": "pass"}
    if payload.get("overall_status"):
        failures: list[str] = []
        for host in (payload.get("hosts") or {}).values():
            if isinstance(host, dict):
                failures.extend(str(item) for item in host.get("failures") or [])
        return {"status": "fail", "failures": failures or [f"readiness overall_status={payload.get('overall_status')}"]}
    return {"status": "fail", "failures": ["readiness status missing"]}


def _load_registered_machine_labels(path: str | Path | None) -> set[str]:
    """Load canonical machine labels from config/workstations/registry.yaml."""
    if path is None:
        return set()
    registry_path = Path(path)
    if not registry_path.exists():
        return set()
    machine_labels: set[str] = set()
    in_machines = False
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^machines:\s*(?:#.*)?$", line):
            in_machines = True
            continue
        if not in_machines:
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*(?:#.*)?$", line)
        if match:
            machine_labels.add(f"machine:{match.group(1)}")
    return machine_labels


def _unregistered_host_action(host_machine_label: str) -> dict[str, Any]:
    return {
        "issue": None,
        "decision": "blocked",
        "reason": "host machine label is not registered",
        "host_machine_label": host_machine_label,
        "execute_provider": False,
    }


def _git_worktree_clean(repo_root: str | Path | None) -> bool:
    """Return whether repo_root is clean and not ahead/behind its upstream."""
    if repo_root is None:
        return True
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--branch"],
        cwd=Path(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        return False
    lines = completed.stdout.splitlines()
    if not lines:
        return True
    branch_line = lines[0]
    if "ahead" in branch_line or "behind" in branch_line:
        return False
    return not any(line.strip() for line in lines[1:])


def _print_payload(*, mode: str, host_machine_label: str, actions: list[dict[str, Any]]) -> None:
    payload = {
        "schema_version": 1,
        "mode": mode,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "host_machine_label": host_machine_label,
        "summary": "provider execution disabled unless approval marker, lease, and clean worktree are present",
        "actions": actions,
    }
    print(json.dumps(_redact_payload(payload), indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run-first Linux cron issue orchestrator")
    parser.add_argument("--host-machine-label", required=True)
    parser.add_argument("--plan-marker-dir", default=".planning/plan-approved")
    parser.add_argument("--issues-json", required=True, help="JSON list from gh issue list --json ...")
    parser.add_argument("--readiness-json", help="Host-local readiness JSON summary")
    parser.add_argument("--repo-root", help="Execution checkout to verify with git status --porcelain")
    parser.add_argument("--registry-yaml", default="config/workstations/registry.yaml", help="Machine registry with canonical dispatch IDs")
    parser.add_argument("--lock-path", help="Local flock path for no-overlap cron ticks")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true", default=False, help="Opt in to future provider execution mode after all gates pass")
    parser.add_argument("--lease-acquired", action="store_true", default=False)
    args = parser.parse_args(argv)

    mode = "execute" if args.execute else "dry-run"
    try:
        lock_manager = no_overlap_lock(args.lock_path) if args.lock_path is not None else contextlib.nullcontext()
        with lock_manager:
            registered_machine_labels = _load_registered_machine_labels(args.registry_yaml)
            if args.host_machine_label not in registered_machine_labels:
                actions = [_unregistered_host_action(args.host_machine_label)]
            else:
                actions = plan_tick(
                    _load_issues(args.issues_json),
                    host_machine_label=args.host_machine_label,
                    plan_marker_dir=args.plan_marker_dir,
                    readiness=_load_readiness(args.readiness_json),
                    lease_acquired=True if args.lease_acquired else None,
                    worktree_clean=_git_worktree_clean(args.repo_root),
                )
    except BlockingIOError:
        actions = [{"issue": None, "decision": "blocked", "reason": "cron tick already running", "execute_provider": False}]
        _print_payload(mode=mode, host_machine_label=args.host_machine_label, actions=actions)
        return 75

    if mode == "dry-run":
        for action in actions:
            action["execute_provider"] = False
    _print_payload(mode=mode, host_machine_label=args.host_machine_label, actions=actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
