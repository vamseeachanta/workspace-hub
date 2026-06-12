#!/usr/bin/env bash
# Read-only repo ecosystem hygiene audit. Writes local state only.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export REPO_ROOT
export UV_CACHE_DIR="${UV_CACHE_DIR:-${REPO_ROOT}/.claude/state/uv-cache}"

UV_BIN="${UV_BIN:-uv}"
TOTAL_TIMEOUT="${REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC:-480}"

set +e
PY_OUTPUT=$(timeout "$TOTAL_TIMEOUT" "${UV_BIN}" run --no-project python - "$@" <<'PY'
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TASK_ID = "repo-ecosystem-hygiene"
REPO_ROOT = Path(os.environ["REPO_ROOT"]).resolve()
REGISTRY_PATH = REPO_ROOT / "config" / "workstations" / "registry.yaml"
STAMPED_STASH_LIST = "git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s"
PROBE_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC", "10"))
REPO_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC", "45"))
TOTAL_TIMEOUT_SEC = int(os.environ.get("REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC", "480"))
START = time.monotonic()
TRIGGER_REPLACEMENTS = {
    "ERROR:": "ERR_MARKER",
    "fatal:": "git_failure",
    "Traceback": "python_stack",
    "Permission denied": "permission_failure",
    "command not found": "missing_command",
    "No such file or directory": "missing_path",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def sanitize(raw: str) -> str:
    text = raw.strip().replace("\n", " | ")
    for needle, replacement in TRIGGER_REPLACEMENTS.items():
        text = text.replace(needle, replacement)
    return text[:500] if text else "none"


def status_rank(status: str) -> int:
    return {"OK": 0, "INFO": 0, "UNKNOWN": 1, "WARN": 2, "ERROR": 3}.get(status, 0)


def max_status(statuses: list[str]) -> str:
    if not statuses:
        return "OK"
    return max(statuses, key=status_rank)


def seconds_left() -> float:
    return max(0.0, TOTAL_TIMEOUT_SEC - (time.monotonic() - START))


def deadline_reached() -> bool:
    return seconds_left() <= 0


def probe_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_days(value: str) -> int | None:
    parsed = parse_iso(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int((datetime.now(timezone.utc) - parsed).total_seconds() // 86400)


def run_bounded(
    command: list[str],
    cwd: Path | None,
    *,
    git_env: bool = False,
    timeout_sec: float | None = None,
) -> dict[str, Any]:
    if not command:
        return {"ok": False, "code": 2, "stdout": "", "stderr": "empty_command"}
    if deadline_reached():
        return {"ok": False, "code": 124, "stdout": "", "stderr": "total_deadline_reached"}
    if shutil.which("timeout") is None:
        return {"ok": False, "code": 127, "stdout": "", "stderr": "timeout_unavailable"}
    allowed_timeout = min(PROBE_TIMEOUT_SEC, seconds_left(), timeout_sec if timeout_sec is not None else PROBE_TIMEOUT_SEC)
    if allowed_timeout <= 0:
        return {"ok": False, "code": 124, "stdout": "", "stderr": "probe_deadline_reached"}
    env = probe_env() if git_env else os.environ.copy()
    try:
        result = subprocess.run(
            ["timeout", str(allowed_timeout), *command],
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return {"ok": False, "code": 127, "stdout": "", "stderr": sanitize(str(exc))}
    return {
        "ok": result.returncode == 0,
        "code": result.returncode,
        "stdout": result.stdout,
        "stderr": sanitize(result.stderr),
    }


def git_readonly(operation: str, repo: Path, arg: str | None = None, timeout_sec: float | None = None) -> dict[str, Any]:
    commands: dict[str, list[str]] = {
        "branch-current": ["git", "branch", "--show-current"],
        "status-short": ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        "upstream-ref": ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        "ahead-behind": ["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"],
        "worktree-list": ["git", "worktree", "list", "--porcelain"],
        "default-branch": ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        "remote-worktree-like-refs": [
            "git",
            "for-each-ref",
            "--format=%(refname:short)",
            "refs/remotes",
        ],
        "local-branches": [
            "git",
            "for-each-ref",
            "--format=%(refname:short)%1f%(committerdate:iso-strict)%1f%(objectname:short)",
            "refs/heads",
        ],
        "stash-list": ["git", "stash", "list", "--date=iso-strict", "--format=%gd%x1f%ci%x1f%s"],
        "recent-local-log": ["git", "log", "-1", "--format=%cI"],
    }
    if operation == "commit-date-by-sha":
        if not arg or not re.fullmatch(r"[0-9a-f]{7,40}", arg):
            return {"ok": False, "code": 2, "stdout": "", "stderr": "invalid_sha"}
        command = ["git", "show", "-s", "--format=%cI", arg]
    else:
        command = commands.get(operation)
    if command is None:
        return {"ok": False, "code": 2, "stdout": "", "stderr": "operation_not_allowed"}
    return run_bounded(command, repo, git_env=True, timeout_sec=timeout_sec)


def gh_readonly(operation: str) -> dict[str, Any]:
    if operation != "daily-cleanup-issue-signal":
        return {"status": "UNKNOWN", "finding": "operation_not_allowed"}
    if os.environ.get("REPO_ECOSYSTEM_HYGIENE_SKIP_GH") == "1":
        return {"status": "UNKNOWN", "finding": "gh_skipped_for_test"}
    if shutil.which("gh") is None:
        return {"status": "UNKNOWN", "finding": "gh_unavailable"}

    first = run_bounded(
        ["gh", "api", "--include", "repos/vamseeachanta/workspace-hub/issues/2652/comments?per_page=1"],
        REPO_ROOT,
    )
    if not first["ok"]:
        return {"status": "UNKNOWN", "finding": "gh_query_unavailable", "detail": first["stderr"]}
    page = "1"
    link_match = re.search(r"[?&]page=(\d+)>;\s*rel=\"last\"", first["stdout"])
    if link_match:
        page = link_match.group(1)
    second = run_bounded(
        ["gh", "api", f"repos/vamseeachanta/workspace-hub/issues/2652/comments?per_page=30&page={page}"],
        REPO_ROOT,
    )
    if not second["ok"]:
        return {"status": "UNKNOWN", "finding": "gh_query_unavailable", "detail": second["stderr"]}
    marker = "_Posted by daily-cleanup.sh"
    found = False
    marker_age_hours = None
    try:
        comments = json.loads(second["stdout"])
    except json.JSONDecodeError:
        comments = []
    for comment in reversed(comments if isinstance(comments, list) else []):
        if marker not in str(comment.get("body", "")):
            continue
        found = True
        created = parse_iso(str(comment.get("created_at", "")))
        if created:
            marker_age_hours = int((datetime.now(timezone.utc) - created).total_seconds() // 3600)
        break
    if not found:
        found = marker in second["stdout"]
    return {
        "status": "UNKNOWN",
        "finding": "known_path_model_mismatch" if found else "marker_not_in_recent_window",
        "marker_freshness": "fresh" if marker_age_hours is not None and marker_age_hours <= 36 else ("stale" if marker_age_hours is not None else ("recent_window_unparsed" if found else "unknown")),
        "marker_age_hours": marker_age_hours,
        "source_issue": 2652,
        "design_issue": 2752,
    }


def output_dir() -> Path:
    configured = os.environ.get("REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return (REPO_ROOT / ".claude" / "state" / "repo-ecosystem-hygiene").resolve()


OUTPUT_DIR = output_dir()


def within_output(path: Path) -> Path:
    resolved = path.resolve()
    if not (resolved == OUTPUT_DIR or OUTPUT_DIR in resolved.parents):
        raise RuntimeError("output_path_escape")
    return resolved


def fs_write(operation: str, target: Path, content: str | None = None) -> Path:
    if operation == "mkdir-output-dir":
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return OUTPUT_DIR
    target = within_output(target)
    if operation == "write-temp-output":
        if content is None or not target.name.startswith(".tmp-"):
            raise RuntimeError("invalid_temp_write")
        target.write_text(content)
        return target
    if operation == "replace-output":
        raise RuntimeError("replace_requires_atomic_write")
    raise RuntimeError("write_operation_not_allowed")


def atomic_write(name: str, content: str) -> Path:
    if "/" in name or name.startswith(".tmp-"):
        raise RuntimeError("invalid_output_name")
    final = within_output(OUTPUT_DIR / name)
    suffix = ".json" if name.endswith(".json") else ".md"
    temp = within_output(OUTPUT_DIR / f".tmp-{name}.{os.getpid()}")
    fs_write("write-temp-output", temp, content)
    if suffix not in {".json", ".md"}:
        raise RuntimeError("invalid_output_suffix")
    os.replace(temp, final)
    return final


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise RuntimeError("configuration_error_registry_missing")
    return yaml.safe_load(REGISTRY_PATH.read_text()) or {}


def resolve_machine(registry: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    host = os.environ.get("REPO_ECOSYSTEM_HYGIENE_HOSTNAME")
    if not host:
        host = socket.gethostname().split(".")[0]
    host = host.lower()
    for name, machine in registry.get("machines", {}).items():
        candidates = [name, machine.get("hostname", ""), *machine.get("hostname_aliases", [])]
        if host in {str(candidate).lower() for candidate in candidates}:
            return name, machine, host
    raise RuntimeError("configuration_error_machine_unknown")


def governed_repo_names(baseline: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    classes: dict[str, str] = {}
    ordered: list[str] = []
    buckets = [
        ("required", baseline.get("required", [])),
        ("optional", baseline.get("optional", [])),
        ("non_tier1_machine_access_current", baseline.get("non_tier1_machine_access_current", [])),
    ]
    for cls, names in buckets:
        for name in names or []:
            if name not in classes:
                classes[name] = cls
                ordered.append(name)
    return ordered, classes


def fallback_default_branch(repo: Path, timeout_sec: float | None = None) -> str:
    branches = git_readonly("local-branches", repo, timeout_sec=timeout_sec)
    if branches["ok"]:
        names = [line.split("\x1f", 1)[0] for line in branches["stdout"].splitlines() if line.strip()]
        if "main" in names:
            return "main"
        if "master" in names:
            return "master"
        if names:
            return names[0]
    return "main"


def default_branch(repo: Path, timeout_sec: float | None = None) -> str:
    result = git_readonly("default-branch", repo, timeout_sec=timeout_sec)
    if result["ok"]:
        branch = result["stdout"].strip()
        if branch.startswith("origin/"):
            return branch.removeprefix("origin/")
        if branch:
            return branch
    return fallback_default_branch(repo, timeout_sec=timeout_sec)


def parse_ahead_behind(result: dict[str, Any]) -> tuple[int, int]:
    if not result["ok"]:
        return (0, 0)
    parts = result["stdout"].strip().split()
    if len(parts) != 2:
        return (0, 0)
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return (0, 0)


def parse_branch_inventory(repo: Path, current: str, default: str, timeout_sec: float | None = None) -> list[dict[str, Any]]:
    result = git_readonly("local-branches", repo, timeout_sec=timeout_sec)
    branches: list[dict[str, Any]] = []
    if not result["ok"]:
        return branches
    for line in result["stdout"].splitlines():
        fields = line.split("\x1f")
        if not fields or not fields[0] or fields[0] == default:
            continue
        days = age_days(fields[1] if len(fields) > 1 else "")
        stale = days is not None and days >= 14 and fields[0] != current
        branches.append(
            {
                "name": fields[0],
                "is_current": fields[0] == current,
                "last_commit": fields[1] if len(fields) > 1 else "",
                "age_days": days,
                "finding": "current_non_default_branch" if fields[0] == current else ("stale_branch" if stale else "branch_inventory"),
                "status": "WARN" if fields[0] == current or stale else "INFO",
            }
        )
    return branches


def parse_worktrees(repo: Path, primary_path: Path, timeout_sec: float | None = None) -> dict[str, Any]:
    result = git_readonly("worktree-list", repo, timeout_sec=timeout_sec)
    summary = {"count": 0, "linked_count": 0, "stale_count": 0, "broken_count": 0, "orphan_count": 0}
    if not result["ok"]:
        return summary
    current: dict[str, str] = {}
    entries: list[dict[str, str]] = []
    for line in result["stdout"].splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        entries.append(current)
    summary["count"] = len(entries)
    for entry in entries:
        path = Path(entry.get("worktree", ""))
        if path.resolve() == primary_path.resolve():
            continue
        summary["linked_count"] += 1
        if not path.exists():
            summary["orphan_count"] += 1
        if "prunable" in entry:
            summary["broken_count"] += 1
        head = entry.get("HEAD", "")
        commit_date = git_readonly("commit-date-by-sha", repo, head, timeout_sec=timeout_sec)
        if commit_date["ok"]:
            days = age_days(commit_date["stdout"].strip())
            if days is not None and days >= 14:
                summary["stale_count"] += 1
    return summary


def parse_stashes(repo: Path, timeout_sec: float | None = None) -> list[dict[str, Any]]:
    result = git_readonly("stash-list", repo, timeout_sec=timeout_sec)
    stashes: list[dict[str, Any]] = []
    if not result["ok"]:
        return stashes
    for line in result["stdout"].splitlines():
        fields = line.split("\x1f")
        if len(fields) < 2:
            continue
        days = age_days(fields[1])
        stashes.append(
            {
                "ref": fields[0],
                "date": fields[1],
                "subject": fields[2] if len(fields) > 2 else "",
                "age_days": days,
                "stale": days is not None and days >= 14,
            }
        )
    return stashes


def remote_worktree_like_refs(repo: Path, timeout_sec: float | None = None) -> list[str]:
    result = git_readonly("remote-worktree-like-refs", repo, timeout_sec=timeout_sec)
    if not result["ok"]:
        return []
    pattern = re.compile(r"(^|/)(worktree|worktree-agent|codex|agent)[/-]", re.IGNORECASE)
    return [line.strip() for line in result["stdout"].splitlines() if pattern.search(line.strip())]


def check_repo(name: str, cls: str, path: Path, policies: dict[str, Any], timeout_sec: float | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if not (path / ".git").exists():
        code = "missing_required_checkout" if cls == "required" else "missing_checkout"
        severity = "ERROR" if cls == "required" else "WARN"
        return {
            "name": name,
            "class": cls,
            "path": str(path),
            "status": severity,
            "findings": [{"code": code, "severity": severity}],
        }

    repo_deadline = time.monotonic() + (timeout_sec if timeout_sec is not None else REPO_TIMEOUT_SEC)

    def remaining_repo_timeout() -> float:
        return max(0.0, repo_deadline - time.monotonic())

    current = git_readonly("branch-current", path, timeout_sec=remaining_repo_timeout())
    current_branch = current["stdout"].strip() if current["ok"] else ""
    default = default_branch(path, timeout_sec=remaining_repo_timeout())
    if current_branch and current_branch != default:
        findings.append({"code": "current_non_default_branch", "severity": "WARN"})

    status_short = git_readonly("status-short", path, timeout_sec=remaining_repo_timeout())
    dirty_count = len([line for line in status_short["stdout"].splitlines() if line.strip()]) if status_short["ok"] else 0
    if not status_short["ok"]:
        findings.append(
            {
                "code": "git_probe_timeout" if status_short["code"] == 124 else "git_probe_failed",
                "severity": "ERROR",
            }
        )
    if dirty_count:
        findings.append({"code": "dirty_worktree", "severity": "WARN"})

    upstream = git_readonly("upstream-ref", path, timeout_sec=remaining_repo_timeout())
    ahead, behind = (0, 0)
    if upstream["ok"]:
        ahead, behind = parse_ahead_behind(git_readonly("ahead-behind", path, timeout_sec=remaining_repo_timeout()))
        if ahead:
            findings.append({"code": "ahead_of_upstream", "severity": "WARN"})
        if behind:
            findings.append({"code": "behind_upstream", "severity": "WARN"})
    else:
        severity = "ERROR" if cls == "required" else "WARN"
        findings.append({"code": "missing_upstream", "severity": severity})

    worktrees = parse_worktrees(path, path, timeout_sec=remaining_repo_timeout())
    if worktrees["orphan_count"] or worktrees["broken_count"]:
        findings.append({"code": "worktree_drift", "severity": "WARN"})
    if worktrees["stale_count"]:
        findings.append({"code": "stale_worktree", "severity": "WARN"})

    branches = parse_branch_inventory(path, current_branch, default, timeout_sec=remaining_repo_timeout())
    stale_branch_count = len([branch for branch in branches if branch["finding"] == "stale_branch"])
    for branch in branches:
        if branch["status"] == "WARN" and not any(f["code"] == branch["finding"] for f in findings):
            findings.append({"code": branch["finding"], "severity": "WARN"})

    stashes = parse_stashes(path, timeout_sec=remaining_repo_timeout())
    stash_count = len(stashes)
    stale_stash_count = len([stash for stash in stashes if stash["stale"]])
    if stash_count:
        findings.append({"code": "stash_inventory", "severity": "WARN"})
    if stale_stash_count and not any(f["code"] == "stale_stash" for f in findings):
        findings.append({"code": "stale_stash", "severity": "WARN"})

    remote_refs = remote_worktree_like_refs(path, timeout_sec=remaining_repo_timeout())

    repo_status = max_status([finding["severity"] for finding in findings])
    return {
        "name": name,
        "class": cls,
        "path": str(path),
        "status": repo_status,
        "current_branch": current_branch,
        "default_branch": default,
        "dirty_count": dirty_count,
        "ahead": ahead,
        "behind": behind,
        "worktrees": worktrees,
        "branch_inventory": branches,
        "stale_branch_count": stale_branch_count,
        "stash_count": stash_count,
        "stale_stash_count": stale_stash_count,
        "stashes": stashes,
        "remote_worktree_like_ref_count": len(remote_refs),
        "remote_worktree_like_refs": remote_refs,
        "findings": findings,
    }


def historical_findings(ecosystem_root: Path, historical: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, meta in sorted((historical or {}).items()):
        exists = (ecosystem_root / name).exists()
        latest_probe = meta.get("latest_probe")
        mismatch = (latest_probe == "absent" and exists) or (latest_probe == "present" and not exists)
        rows.append(
            {
                "name": name,
                "status": "WARN",
                "finding": meta.get("warning", "historical_state_changed_since_prior_comment"),
                "source_issue": meta.get("source_issue"),
                "source_comment": meta.get("source_comment"),
                "prior_claim": meta.get("prior_claim"),
                "latest_probe": latest_probe,
                "latest_probe_mismatch": mismatch,
            }
        )
    return rows


def scan_residue(ecosystem_root: Path, configured: set[str], historical: set[str], infrastructure: set[str]) -> list[dict[str, Any]]:
    if not ecosystem_root.exists():
        return []
    runtime_names = {
        ".agents",
        ".claude",
        ".codex",
        ".planning",
        ".pnpm-store",
        ".Trash-1000",
        ".cleanup-lock",
        ".cleanup-trash",
        ".daily-cleanup-lock",
    }
    residue: list[dict[str, Any]] = []
    for entry in sorted(ecosystem_root.iterdir(), key=lambda p: p.name.lower()):
        name = entry.name
        if name in configured or name in historical:
            continue
        if name in infrastructure or name in runtime_names or name.startswith("session-summary"):
            residue.append({"name": name, "status": "INFO", "finding": "known_unclassified", "path": str(entry)})
            continue
        if (entry / ".git").exists():
            residue.append(
                {
                    "name": name,
                    "status": "WARN",
                    "finding": "registry_disposition_required",
                    "class": "unknown_config",
                    "path": str(entry),
                }
            )
        else:
            residue.append({"name": name, "status": "WARN", "finding": "unknown_sibling_residue", "path": str(entry)})
    return residue


def cron_health_links(workspace_root: Path) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = [
        {
            "id": "repository-sync",
            "status": "UNKNOWN",
            "finding": "schedule_metadata_mismatch",
            "issue": 2572,
        }
    ]
    health_dir = workspace_root / ".claude" / "state" / "cron-health"
    newest = None
    if health_dir.exists():
        candidates = sorted(health_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        newest = candidates[0] if candidates else None
    if newest and (time.time() - newest.stat().st_mtime) <= 36 * 3600:
        try:
            data = json.loads(newest.read_text())
            for task in data.get("tasks", []):
                if task.get("id") == "daily-today":
                    links.append(
                        {
                            "id": "daily-today",
                            "status": task.get("status", "UNKNOWN"),
                            "finding": "cron_health_state",
                            "issue": 2652,
                        }
                    )
                    break
        except json.JSONDecodeError:
            links.append({"id": "daily-today", "status": "UNKNOWN", "finding": "cron_health_json_invalid", "issue": 2652})
    else:
        links.append({"id": "daily-today", "status": "UNKNOWN", "finding": "cron_health_state_missing_or_stale", "issue": 2652})

    cleanup = gh_readonly("daily-cleanup-issue-signal")
    cleanup["id"] = "daily-cleanup"
    cleanup.setdefault("issue", 2652)
    links.append(cleanup)
    return links


def markdown_report(state: dict[str, Any]) -> str:
    lines = [
        "# Repo Ecosystem Hygiene",
        "",
        f"- Generated: {state['generated_at']}",
        f"- Host: {state['hostname']} ({state['machine']})",
        f"- Status: {state['status']}",
        "",
        "## Repos",
    ]
    for repo in state["repos"]:
        finding_codes = ", ".join(f["code"] for f in repo.get("findings", [])) or "none"
        lines.append(f"- {repo['status']} {repo['name']} ({repo['class']}): {finding_codes}")
    lines.append("")
    lines.append("## Residue")
    for item in state["residue"]:
        lines.append(f"- {item['status']} {item['name']}: {item['finding']}")
    lines.append("")
    lines.append("## Historical")
    for item in state["historical"]:
        mismatch = " mismatch" if item.get("latest_probe_mismatch") else ""
        lines.append(f"- {item['status']} {item['name']}: {item['finding']}{mismatch}")
    lines.append("")
    lines.append("## Health Links")
    for link in state["health_links"]:
        lines.append(f"- {link.get('status', 'UNKNOWN')} {link['id']}: {link.get('finding', 'unknown')}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    registry = load_registry()
    machine_name, machine, host = resolve_machine(registry)
    baseline = machine.get("tier1_baseline")
    if not baseline:
        raise RuntimeError("configuration_error_missing_tier1_baseline")
    if machine_name != "dev-primary" and machine.get("hostname") != "ace-linux-1":
        raise RuntimeError("configuration_error_v1_machine_not_supported")
    if baseline.get("layout") != "sibling" and machine.get("repo_layout") != "sibling":
        raise RuntimeError("configuration_error_layout_not_supported")

    ecosystem_root_value = os.environ.get("REPO_ECOSYSTEM_ROOT") or machine.get("tier1_repo_root")
    if not ecosystem_root_value:
        raise RuntimeError("configuration_error_missing_ecosystem_root")
    ecosystem_root = Path(ecosystem_root_value).expanduser().resolve()
    workspace_root = Path(os.environ.get("WORKSPACE_HUB") or machine.get("workspace_root") or REPO_ROOT).expanduser().resolve()

    fs_write("mkdir-output-dir", OUTPUT_DIR)

    names, classes = governed_repo_names(baseline)
    historical = baseline.get("historically_moved_not_currently_present", {}) or {}
    policies = baseline.get("placement_rules", {}) or {}
    repos: list[dict[str, Any]] = []
    incomplete = False
    for name in names:
        if deadline_reached():
            incomplete = True
            break
        path = workspace_root if name == "workspace-hub" else ecosystem_root / name
        repo_deadline = time.monotonic() + REPO_TIMEOUT_SEC
        repo_timeout = max(0.0, min(REPO_TIMEOUT_SEC, repo_deadline - time.monotonic()))
        repos.append(check_repo(name, classes[name], path, policies, timeout_sec=repo_timeout))
        if time.monotonic() >= repo_deadline:
            repos[-1]["findings"].append({"code": "repo_probe_timeout", "severity": "WARN"})
            repos[-1]["status"] = max_status([repos[-1]["status"], "WARN"])

    historical_rows = historical_findings(ecosystem_root, historical)
    residue = scan_residue(
        ecosystem_root,
        set(names),
        set(historical.keys()),
        set(baseline.get("infrastructure_dirs", []) or []),
    )
    registry_gaps = []
    governed = set(names)
    for raw_name in machine.get("repos", []) or []:
        if raw_name not in governed:
            registry_gaps.append({"name": raw_name, "status": "WARN", "finding": "registry_policy_gap"})

    health_links = cron_health_links(workspace_root)
    all_statuses = [repo["status"] for repo in repos]
    all_statuses.extend(item["status"] for item in residue if item["status"] != "INFO")
    all_statuses.extend(item["status"] for item in historical_rows)
    all_statuses.extend(item["status"] for item in registry_gaps)
    status = max_status(all_statuses)
    if incomplete and status_rank(status) < status_rank("WARN"):
        status = "WARN"

    dated = today()
    state = {
        "task": TASK_ID,
        "status": status,
        "generated_at": now_iso(),
        "hostname": host,
        "machine": machine_name,
        "ecosystem_root": str(ecosystem_root),
        "workspace_root": str(workspace_root),
        "repo_count": len(repos),
        "incomplete_due_to_deadline": incomplete,
        "repos": repos,
        "historical": historical_rows,
        "residue": residue,
        "registry_gaps": registry_gaps,
        "health_links": health_links,
    }
    json_text = json.dumps(state, indent=2, sort_keys=True) + "\n"
    md_text = markdown_report(state)
    dated_json = atomic_write(f"{dated}.json", json_text)
    latest_json = atomic_write("latest.json", json_text)
    dated_md = atomic_write(f"{dated}.md", md_text)
    latest_md = atomic_write("latest.md", md_text)
    state["outputs"] = {
        "dated_json": str(dated_json),
        "latest_json": str(latest_json),
        "dated_markdown": str(dated_md),
        "latest_markdown": str(latest_md),
    }
    atomic_write(f"{dated}.json", json.dumps(state, indent=2, sort_keys=True) + "\n")
    atomic_write("latest.json", json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"task={TASK_ID} status={status} artifact={latest_md} state={latest_json} ts={state['generated_at']}")
    return 0


try:
    raise SystemExit(main())
except SystemExit:
    raise
except Exception as exc:
    print(f"ERROR: repo-ecosystem-hygiene execution_failed code=1 reason={sanitize(str(exc))}")
    raise SystemExit(1)
PY
)
PY_RC=$?
set -e
if [[ -n "$PY_OUTPUT" ]]; then
  printf '%s\n' "$PY_OUTPUT"
fi
if [[ "$PY_RC" -ne 0 ]]; then
  if ! grep -q "repo-ecosystem-hygiene execution_failed" <<<"$PY_OUTPUT"; then
    echo "ERROR: repo-ecosystem-hygiene execution_failed code=${PY_RC} reason=python_or_uv_failure"
  fi
  exit "$PY_RC"
fi
