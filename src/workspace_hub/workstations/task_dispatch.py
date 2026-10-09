from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import yaml


REQUIRED_ROUTE_CHECKS = frozenset(
    {
        "ssh_auth",
        "provider_auth",
        "repo_rules_loaded",
        "headless_disconnect_completion",
        "exit_status",
        "artifact_receipt",
        "duplicate_rejection",
    }
)

CLIENT_NAME_MARKERS = ("client-",)
DISPATCH_ORDER = ("dev-primary", "dev-secondary", "gpu-claw", "ace-win-1", "ace-win-2")


@dataclass(frozen=True)
class DispatchRecord:
    machine: str
    hostname: str
    os: str
    ssh_alias: str
    providers: tuple[str, ...]
    shell: str
    scheduled_task_path: str | None


@dataclass(frozen=True)
class DirectedRoute:
    source: str
    target: str


def load_registry(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    machines = payload.get("machines")
    if not isinstance(machines, dict):
        raise ValueError("registry must contain a machines mapping")
    return machines


def dispatch_records(registry: dict[str, Any]) -> list[DispatchRecord]:
    records: list[DispatchRecord] = []
    for machine, raw in registry.items():
        if not isinstance(raw, dict):
            continue
        task_dispatch = raw.get("task_dispatch") or {}
        if task_dispatch.get("enabled") is not True:
            continue
        ssh_alias = task_dispatch.get("ssh_alias")
        providers = tuple(task_dispatch.get("providers") or ())
        shell = task_dispatch.get("shell")
        if not isinstance(ssh_alias, str) or not ssh_alias:
            raise ValueError(f"{machine} task_dispatch.ssh_alias missing")
        if not providers:
            raise ValueError(f"{machine} task_dispatch.providers missing")
        if shell not in {"bash", "git-bash"}:
            raise ValueError(f"{machine} task_dispatch.shell invalid")
        os_name = str(raw.get("os") or "")
        scheduled_task_path = task_dispatch.get("scheduled_task_path")
        if os_name == "windows" and not scheduled_task_path:
            raise ValueError(f"{machine} Windows task_dispatch.scheduled_task_path missing")
        records.append(
            DispatchRecord(
                machine=machine,
                hostname=str(raw.get("hostname") or machine),
                os=os_name,
                ssh_alias=ssh_alias,
                providers=providers,
                shell=shell,
                scheduled_task_path=scheduled_task_path,
            )
        )
    order = {machine: index for index, machine in enumerate(DISPATCH_ORDER)}
    return sorted(records, key=lambda record: order.get(record.machine, len(order)))


def directed_routes(records: Iterable[DispatchRecord]) -> list[DirectedRoute]:
    machines = [record.machine for record in records]
    return [
        DirectedRoute(source=source, target=target)
        for source in machines
        for target in machines
        if source != target
    ]


def validate_fleet_ssh_hosts(fleet: dict[str, Any], registry: dict[str, Any]) -> None:
    aliases = {record.ssh_alias for record in dispatch_records(registry)}
    ssh_hosts = set(fleet.get("ssh_hosts") or [])
    manual_hosts = set(fleet.get("manual_hosts") or [])
    unknown = sorted((ssh_hosts | manual_hosts) - aliases)
    if unknown:
        raise ValueError(f"fleet ssh hosts not declared in registry task_dispatch: {unknown}")
    overlap = sorted(ssh_hosts & manual_hosts)
    if overlap:
        raise ValueError(f"fleet ssh hosts cannot be both ssh and manual scope: {overlap}")


def validate_harness_config(harness: dict[str, Any], registry: dict[str, Any]) -> None:
    workstations = harness.get("workstations") or {}
    records = {record.machine: record for record in dispatch_records(registry)}
    for machine, record in records.items():
        entry = workstations.get(machine)
        if not isinstance(entry, dict):
            raise ValueError(f"harness-config missing workstation {machine}")
        registry_root = (registry[machine] or {}).get("workspace_root")
        if entry.get("ws_hub_path") != registry_root:
            raise ValueError(f"{machine} harness ws_hub_path does not match registry workspace_root")
        if entry.get("ssh_target") != record.ssh_alias:
            raise ValueError(f"{machine} harness ssh_target does not match task_dispatch.ssh_alias")
        baseline = entry.get("providers_baseline") or {}
        for provider in ("claude", "codex"):
            if provider in record.providers and baseline.get(provider) != "present":
                raise ValueError(f"{machine} harness providers_baseline.{provider} must be present")


def route_verdicts(
    records: Iterable[DispatchRecord],
    evidence: dict[tuple[str, str], dict[str, Any]],
    *,
    now: datetime | None = None,
    max_age_hours: float = 24.0,
) -> dict[tuple[str, str], str]:
    now = now or datetime.now(UTC)
    verdicts: dict[tuple[str, str], str] = {}
    for route in directed_routes(records):
        key = (route.source, route.target)
        verdicts[key] = route_verdict(evidence.get(key), now=now, max_age_hours=max_age_hours)
    return verdicts


def route_verdict(
    evidence: dict[str, Any] | None,
    *,
    now: datetime | None = None,
    max_age_hours: float = 24.0,
) -> str:
    if not isinstance(evidence, dict):
        return "MISSING-EVIDENCE"
    status = evidence.get("status")
    if status == "blocked":
        return "BLOCKED"
    if status != "pass":
        return "NOT-READY"
    stamp = _parse_timestamp(evidence.get("generated_at"))
    if stamp is None:
        return "MISSING-EVIDENCE"
    now = now or datetime.now(UTC)
    age_h = (now - stamp).total_seconds() / 3600.0
    if age_h < 0:
        return "MISSING-EVIDENCE"
    if age_h > max_age_hours:
        return "STALE-EVIDENCE"
    checks = evidence.get("checks")
    if not isinstance(checks, dict):
        return "MISSING-EVIDENCE"
    if any(checks.get(name) is not True for name in REQUIRED_ROUTE_CHECKS):
        return "MISSING-EVIDENCE"
    return "READY"


def task_dispatch_summary(
    registry: dict[str, Any],
    evidence: dict[tuple[str, str], dict[str, Any]],
    *,
    now: datetime | None = None,
    max_age_hours: float = 24.0,
) -> dict[str, Any]:
    records = dispatch_records(registry)
    verdicts = route_verdicts(records, evidence, now=now, max_age_hours=max_age_hours)
    total = len(verdicts)
    ready = sum(1 for verdict in verdicts.values() if verdict == "READY")
    blocked = _routes_with(verdicts, "BLOCKED")
    stale = _routes_with(verdicts, "STALE-EVIDENCE")
    missing = [route for route, verdict in verdicts.items() if verdict == "MISSING-EVIDENCE"]
    return {
        "status": "ready" if total and ready == total else "not-ready",
        "ready_routes": ready,
        "total_routes": total,
        "blocked_routes": _format_routes(blocked),
        "stale_routes": _format_routes(stale),
        "missing_routes": _format_routes(missing),
    }


def load_route_evidence_dir(path: str | Path) -> dict[tuple[str, str], dict[str, Any]]:
    evidence_dir = Path(path)
    evidence: dict[tuple[str, str], dict[str, Any]] = {}
    if not evidence_dir.exists():
        return evidence
    for route_file in sorted(evidence_dir.glob("*.yaml")) + sorted(evidence_dir.glob("*.yml")):
        _load_route_file(route_file, evidence)
    return evidence


def find_public_repo_forbidden_names(registry: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for record in dispatch_records(registry):
        for value in (record.hostname, record.ssh_alias, *record.providers):
            lower = value.lower()
            if any(marker in lower for marker in CLIENT_NAME_MARKERS):
                findings.append(f"{record.machine}:{value}")
    return findings


def _load_route_file(path: Path, evidence: dict[tuple[str, str], dict[str, Any]]) -> None:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return
    source = payload.get("source")
    target = payload.get("target")
    if isinstance(source, str) and isinstance(target, str):
        evidence[(source, target)] = payload


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _routes_with(verdicts: dict[tuple[str, str], str], wanted: str) -> list[tuple[str, str]]:
    return [route for route, verdict in verdicts.items() if verdict == wanted]


def _format_routes(routes: Iterable[tuple[str, str]]) -> list[str]:
    return [f"{source}->{target}" for source, target in routes]
