"""Policy primitives for Telegram-driven Hermes dispatch (#2720).

This module is intentionally side-effect free. It translates a parsed Telegram
request plus GitHub issue/readiness evidence into an accept/block decision; Git
remote-ref lease creation is performed by the eventual runner.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
from pathlib import Path
from typing import Any

import yaml

SECRET_KEY_RE = re.compile(r"(token|secret|api[_-]?key|password|credential)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"\b(?:\d{6,}:[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]+)\b")
ENV_POINTER_FIELDS = {"bot_token_env", "allowed_user_ids_env"}
ALLOWED_TELEGRAM_MODES = {"coordinator", "worker", "desktop-status-only", "disabled"}
DISPATCH_TELEGRAM_MODES = {"coordinator", "worker"}
ALLOWED_HOST_ROLES = {
    "primary-dev",
    "secondary-dev",
    "simulation-license-host",
    "simulation-secondary",
    "portable-dev",
    "gpu-compute",
}


class DispatchPolicyError(ValueError):
    """Fail-closed dispatch policy validation error."""


@dataclasses.dataclass(frozen=True)
class HostRecord:
    host_id: str
    hostname: str
    os: str
    role: str
    workspace_root: str | None
    dispatch_enabled: bool
    telegram_mode: str
    hermes_profile: str
    sync_policy: str
    repos: tuple[str, ...]
    data_repos: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class TelegramCommand:
    command: str
    command_type: str
    issue_number: int | None = None
    mode: str = "implementation"
    host_selector: str = "auto"


@dataclasses.dataclass(frozen=True)
class DispatchRequest:
    command: str
    issue_number: int
    mode: str = "implementation"
    host_selector: str = "auto"


@dataclasses.dataclass(frozen=True)
class IssueState:
    number: int
    labels: list[str]
    url: str


@dataclasses.dataclass(frozen=True)
class HostReadiness:
    host_id: str
    status: str
    dirty: bool
    ahead: int = 0
    behind: int = 0
    missing_data: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class DispatchLease:
    issue_number: int
    mode: str
    host_id: str
    job_id: str
    lease_ref: str
    active: bool = True


@dataclasses.dataclass(frozen=True)
class LeaseSnapshot:
    fetched_ok: bool
    source: str
    leases: list[DispatchLease] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class DispatchDecision:
    accepted: bool
    reason_code: str
    message: str
    host_id: str | None = None
    lease_ref: str | None = None
    idempotency_key: str | None = None


def _walk_for_secrets(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if SECRET_KEY_RE.search(key_text) and key_text not in ENV_POINTER_FIELDS:
                raise DispatchPolicyError(f"registry contains secret-like value at field {child_path}")
            _walk_for_secrets(child, child_path)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            _walk_for_secrets(child, f"{path}[{idx}]")
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        raise DispatchPolicyError(f"registry contains secret-like value at field {path}")


def load_registry(path: str | Path) -> dict[str, HostRecord]:
    """Load dispatch metadata from the canonical workstation registry."""
    registry_path = Path(path)
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("machines"), dict):
        raise DispatchPolicyError("registry must contain machines mapping")
    _walk_for_secrets(data)

    hosts: dict[str, HostRecord] = {}
    for host_id, raw in data["machines"].items():
        if not isinstance(raw, dict):
            raise DispatchPolicyError(f"machine {host_id} must be a mapping")
        for required in ("hostname", "os", "role", "workspace_root", "capabilities", "repos"):
            if required not in raw:
                raise DispatchPolicyError(f"machine {host_id} missing required field {required}")
        role = str(raw["role"])
        if role not in ALLOWED_HOST_ROLES:
            raise DispatchPolicyError(f"machine {host_id} has unknown role {role}")
        tg = raw.get("telegram_hermes") or {}
        if not isinstance(tg, dict):
            raise DispatchPolicyError(f"machine {host_id} telegram_hermes must be a mapping")
        dispatch_enabled = bool(tg.get("dispatch_enabled", False))
        mode = str(tg.get("telegram_mode", "disabled"))
        if mode not in ALLOWED_TELEGRAM_MODES:
            raise DispatchPolicyError(f"machine {host_id} has invalid telegram_mode {mode}")
        if dispatch_enabled and mode not in DISPATCH_TELEGRAM_MODES:
            raise DispatchPolicyError(f"machine {host_id} dispatch_enabled requires telegram_mode coordinator or worker")
        if dispatch_enabled:
            if "storage" not in raw:
                raise DispatchPolicyError(f"machine {host_id} dispatch_enabled missing storage")
            for required in ("telegram_mode", "hermes_profile", "sync_policy", "data_access_profile", "readiness_freshness_thresholds"):
                if required not in tg:
                    raise DispatchPolicyError(f"machine {host_id} dispatch_enabled missing {required}")
        dap = tg.get("data_access_profile") or {}
        hosts[str(host_id)] = HostRecord(
            host_id=str(host_id),
            hostname=str(raw["hostname"]),
            os=str(raw["os"]),
            role=role,
            workspace_root=raw.get("workspace_root"),
            dispatch_enabled=dispatch_enabled,
            telegram_mode=mode,
            hermes_profile=str(tg.get("hermes_profile", "manual")),
            sync_policy=str(tg.get("sync_policy", "manual-status-only")),
            repos=tuple(raw.get("repos") or []),
            data_repos=tuple((dap.get("repos") or [])),
        )
    return hosts


def parse_dispatch_command(command: str) -> DispatchRequest:
    """Parse `/dispatch <issue> [--mode plan|implementation] [--host X]`."""
    parsed = parse_telegram_command(command)
    if parsed.command_type != "dispatch" or parsed.issue_number is None:
        raise DispatchPolicyError("usage: /dispatch <issue> [--mode plan|implementation] [--host host|auto]")
    return DispatchRequest(command=command, issue_number=parsed.issue_number, mode=parsed.mode, host_selector=parsed.host_selector)


def _positive_issue_number(value: str) -> int:
    try:
        issue_number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("issue must be a positive integer") from exc
    if issue_number <= 0:
        raise argparse.ArgumentTypeError("issue must be a positive integer")
    return issue_number


def parse_telegram_command(command: str) -> TelegramCommand:
    """Parse the supported Telegram command surface without executing side effects."""
    parts = command.split()
    if not parts:
        raise DispatchPolicyError("usage: /status|/dispatch|/jobs|/sync")
    verb = parts[0]
    if verb == "/dispatch":
        parser = argparse.ArgumentParser(prog="/dispatch", add_help=False)
        parser.add_argument("issue", type=_positive_issue_number)
        parser.add_argument("--mode", choices=["plan", "implementation"], default="implementation")
        parser.add_argument("--host", default="auto")
        try:
            ns = parser.parse_args(parts[1:])
        except SystemExit as exc:
            raise DispatchPolicyError("usage: /dispatch <issue> [--mode plan|implementation] [--host host|auto]") from exc
        return TelegramCommand(command=command, command_type="dispatch", issue_number=ns.issue, mode=ns.mode, host_selector=ns.host)
    if verb in {"/status", "/sync"}:
        parser = argparse.ArgumentParser(prog=verb, add_help=False)
        parser.add_argument("--host", default="auto")
        try:
            ns = parser.parse_args(parts[1:])
        except SystemExit as exc:
            raise DispatchPolicyError(f"usage: {verb} [--host host|auto]") from exc
        return TelegramCommand(command=command, command_type=verb.removeprefix("/"), host_selector=ns.host)
    if verb == "/jobs":
        if len(parts) != 1:
            raise DispatchPolicyError("usage: /jobs")
        return TelegramCommand(command=command, command_type="jobs")
    raise DispatchPolicyError("usage: /status|/dispatch|/jobs|/sync")


def _approval_marker_exists(marker_dir: Path, issue_number: int) -> bool:
    return (marker_dir / f"{issue_number}.md").exists()


def _select_host(hosts: dict[str, HostRecord], selector: str, readiness: dict[str, HostReadiness]) -> str | None:
    if selector != "auto":
        return selector if selector in hosts else None
    for host_id, host in hosts.items():
        state = readiness.get(host_id)
        if (
            host.dispatch_enabled
            and host.telegram_mode in DISPATCH_TELEGRAM_MODES
            and state
            and state.status == "pass"
            and not state.dirty
            and state.ahead == 0
            and state.behind == 0
            and not state.missing_data
        ):
            return host_id
    return None


def evaluate_dispatch_request(
    request: DispatchRequest,
    issue: IssueState,
    registry_path: str | Path,
    approval_marker_dir: str | Path,
    readiness: dict[str, HostReadiness],
    lease_snapshot: LeaseSnapshot,
) -> DispatchDecision:
    """Evaluate whether a Telegram dispatch request can launch work."""
    hosts = load_registry(registry_path)
    labels = set(issue.labels)
    marker_dir = Path(approval_marker_dir)

    if request.issue_number != issue.number:
        return DispatchDecision(False, "issue_mismatch", f"Dispatch request issue {request.issue_number} did not match resolved issue {issue.number}")
    if not lease_snapshot.fetched_ok:
        return DispatchDecision(False, "lease_state_unknown", f"Lease state could not be verified from {lease_snapshot.source}")

    if request.mode == "implementation":
        if "status:plan-approved" not in labels:
            return DispatchDecision(False, "approval_required", "Implementation requires status:plan-approved and local approval marker")
        if not _approval_marker_exists(marker_dir, issue.number):
            return DispatchDecision(False, "approval_marker_missing", f"Implementation requires .planning/plan-approved/{issue.number}.md")
    elif request.mode == "plan" and not ({"status:needs-plan", "status:plan-review"} & labels):
        return DispatchDecision(False, "planning_status_required", "Plan-only dispatch requires status:needs-plan or status:plan-review")

    host_id = _select_host(hosts, request.host_selector, readiness)
    if host_id is None:
        return DispatchDecision(False, "no_dispatchable_host", "No dispatchable host matched request")
    host = hosts[host_id]
    if not host.dispatch_enabled:
        return DispatchDecision(False, "host_status_only", f"Host {host_id} is status-only, not dispatch-enabled")
    if host.telegram_mode not in DISPATCH_TELEGRAM_MODES:
        return DispatchDecision(False, "host_status_only", f"Host {host_id} mode {host.telegram_mode} is not dispatch-capable")
    state = readiness.get(host_id)
    if state is None or state.status != "pass":
        return DispatchDecision(False, "host_not_ready", f"Host {host_id} readiness is not pass")
    if state.dirty or state.ahead or state.behind:
        return DispatchDecision(False, "repo_not_clean", f"Host {host_id} repo is not clean or synced")
    if state.missing_data:
        return DispatchDecision(False, "missing_data_access", f"Host {host_id} missing data access: {', '.join(state.missing_data)}")

    for lease in lease_snapshot.leases:
        if lease.active and lease.issue_number == issue.number and lease.mode == request.mode:
            return DispatchDecision(False, "duplicate_lease", f"Existing active lease/job {lease.job_id}: {lease.lease_ref}")

    mode_slug = request.mode
    lease_ref = f"refs/heads/dispatch/leases/{issue.number}-{mode_slug}"
    key = f"{issue.number}:{request.mode}:{host_id}"
    return DispatchDecision(True, "accepted", "Dispatch accepted", host_id=host_id, lease_ref=lease_ref, idempotency_key=key)
