"""Probe parsing and readiness classification for Hermes preflight."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
import socket
from typing import Any

from .redact import redact_text
from .schema import CORE_TOOLS, ENGINEERING_TOOLS, SCHEMA_VERSION


def parse_probe_output(raw: str) -> dict[str, Any]:
    """Parse the line-oriented shell probe format into a dictionary."""

    probe: dict[str, Any] = {
        "tools": {},
        "tool_versions": {},
        "engineering": {},
        "raw": redact_text(raw),
    }
    for line in raw.splitlines():
        line = line.strip()
        if not line or line == "PREFLIGHT_PROBE_V1" or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = redact_text(value.strip())
        if key.startswith("tool.") and key.endswith(".path"):
            tool = key.removeprefix("tool.").removesuffix(".path")
            probe["tools"][tool] = value
        elif key.startswith("tool.") and key.endswith(".version"):
            tool = key.removeprefix("tool.").removesuffix(".version")
            probe["tool_versions"][tool] = value
        elif key.startswith("engineering.") and key.endswith(".version"):
            tool = key.removeprefix("engineering.").removesuffix(".version")
            probe["engineering"][tool] = value
        else:
            probe[key.replace(".", "_")] = value

    for int_key in ("git_dirty_count", "git_ahead", "git_behind", "gh_auth_exit", "gh_api_exit"):
        if int_key in probe:
            try:
                probe[int_key] = int(str(probe[int_key]).strip() or 0)
            except ValueError:
                probe[int_key] = 1
    if "disk_free_gb" in probe:
        try:
            probe["disk_free_gb"] = float(str(probe["disk_free_gb"]).strip() or 0)
        except ValueError:
            probe["disk_free_gb"] = 0.0
    probe["workspace_exists"] = str(probe.get("workspace_exists", "")).lower() == "true"
    return probe


def _check(
    name: str,
    category: str,
    status: str,
    detail: str,
    *,
    blocks: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "category": category,
        "status": status,
        "detail": redact_text(detail),
        "blocks": blocks or [],
    }


def _is_control_plane(role: str) -> bool:
    return role in {"primary-dev", "control-plane"}


def build_report(
    probe: dict[str, Any],
    *,
    target: dict[str, Any],
    from_host: str | None = None,
    invocation: dict[str, Any] | None = None,
    run_ts: str | None = None,
) -> dict[str, Any]:
    """Build a schema-v1 readiness report from parsed probe data."""

    role = str(target.get("role") or "")
    control_plane = _is_control_plane(role)
    checks: list[dict[str, Any]] = []

    checks.append(
        _check(
            "host.reachability",
            "host",
            "pass",
            f"probe collected from {probe.get('hostname', target.get('hostname', 'unknown'))}",
        )
    )
    expected_hostname = str(target.get("hostname") or target.get("name") or "")
    actual_hostname = str(probe.get("hostname") or "")
    checks.append(
        _check(
            "host.hostname_match",
            "host",
            "pass" if not expected_hostname or actual_hostname == expected_hostname else "warn",
            f"expected={expected_hostname or 'unknown'} actual={actual_hostname or 'unknown'}",
        )
    )
    workspace_root = str(target.get("workspace_root") or probe.get("workspace_root") or "")
    checks.append(
        _check(
            "host.canonical_workspace_root",
            "host",
            "pass" if probe.get("workspace_exists") else "block",
            f"{workspace_root or 'workspace root unknown'} exists={probe.get('workspace_exists')}",
        )
    )
    disk_free = float(probe.get("disk_free_gb") or 0)
    disk_status = "pass"
    if disk_free < 2:
        disk_status = "block"
    elif disk_free < 20:
        disk_status = "warn"
    checks.append(_check("host.disk_free_gb", "host", disk_status, f"{disk_free:g} GB free"))

    remote_url = str(probe.get("git_remote_url") or "")
    dirty_count = int(probe.get("git_dirty_count") or 0)
    repo_status = "pass"
    repo_detail = f"branch={probe.get('git_branch', 'unknown')} dirty={dirty_count}"
    if remote_url and "github.com/vamseeachanta/workspace-hub" not in remote_url:
        repo_status = "block"
        repo_detail += " wrong origin remote"
    elif dirty_count:
        repo_status = "warn"
        repo_detail += " dirty worktree"
    checks.append(_check("repo.tier1_branch_status", "repo", repo_status, repo_detail))

    behind = int(probe.get("git_behind") or 0)
    ahead = int(probe.get("git_ahead") or 0)
    checks.append(
        _check(
            "repo.ahead_behind",
            "repo",
            "warn" if behind >= 10 else "pass",
            f"ahead={ahead} behind={behind}",
        )
    )

    tools: dict[str, str] = dict(probe.get("tools") or {})
    for tool in CORE_TOOLS:
        path = tools.get(tool, "")
        status = "pass" if path else "warn"
        if tool in {"git", "uv"} and not path:
            status = "block"
        if tool == "gh" and not path:
            status = "block" if control_plane else "warn"
        if tool == "hermes" and not path and control_plane:
            status = "block"
        checks.append(
            _check(
                f"tool.path.{tool}",
                "tool",
                status,
                path or f"{tool} not found in login shell PATH",
            )
        )
        version = str((probe.get("tool_versions") or {}).get(tool) or "")
        if version:
            checks.append(_check(f"tool.version.{tool}", "tool", "pass", version))

    auth_exit = int(probe.get("gh_auth_exit") or 0)
    auth_ok = auth_exit == 0
    auth_status = "pass" if auth_ok else ("block" if control_plane else "warn")
    auth_blocks = [] if auth_ok else ["github_mutation"]
    checks.append(
        _check(
            "auth.gh_status",
            "auth",
            auth_status,
            str(probe.get("gh_auth_output") or "gh auth status failed"),
            blocks=auth_blocks,
        )
    )

    api_exit = int(probe.get("gh_api_exit") or 0)
    api_ok = api_exit == 0 and bool(probe.get("gh_api_login"))
    checks.append(
        _check(
            "auth.gh_api_user_login",
            "auth",
            "pass" if api_ok else ("block" if control_plane else "warn"),
            f"login={probe.get('gh_api_login') or 'unavailable'}",
            blocks=[] if api_ok else ["github_mutation"],
        )
    )

    model = str(probe.get("hermes_model") or "")
    checks.append(
        _check(
            "provider.hermes_default_model",
            "provider",
            "pass" if model == "openai-codex/gpt-5.5" else "warn",
            model or "Hermes default model not detected",
        )
    )
    shebang = str(probe.get("hermes_shebang") or "")
    checks.append(
        _check(
            "provider.hermes_shebang_health",
            "provider",
            "pass" if shebang in {"ok", "skip"} else "warn",
            shebang or "Hermes shebang health unknown",
        )
    )

    engineering = dict(probe.get("engineering") or {})
    configured_tools = set((target.get("capabilities") or {}).get("tools") or [])
    for tool in ENGINEERING_TOOLS:
        if tool in engineering or tool in configured_tools:
            version = engineering.get(tool, "")
            checks.append(
                _check(
                    f"engineering.{tool}_version",
                    "engineering",
                    "pass" if version else "warn",
                    version or f"{tool} version unavailable",
                )
            )

    counts = Counter(check["status"] for check in checks)
    github_mutation_allowed = not any(
        "github_mutation" in check["blocks"] for check in checks if check["status"] != "pass"
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "run_ts": run_ts or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "from_host": from_host or socket.gethostname().split(".", 1)[0],
        "target": {
            "name": target.get("name") or target.get("hostname") or actual_hostname,
            "hostname": expected_hostname or actual_hostname,
            "role": role or "unknown",
            "workspace_root": workspace_root,
        },
        "invocation": invocation or {},
        "checks": checks,
        "summary": {
            "pass": counts.get("pass", 0),
            "warn": counts.get("warn", 0),
            "block": counts.get("block", 0),
            "machine_ready": counts.get("block", 0) == 0,
            "github_mutation_allowed": github_mutation_allowed,
        },
    }
    return report
