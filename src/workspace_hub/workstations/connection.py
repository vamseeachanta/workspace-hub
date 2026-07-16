from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from workspace_hub.workstations.resolver import (
    MachineRecord,
    WorkstationPathResolver,
    load_unique_yaml_bytes,
)


_REFERENCE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DNS_LABEL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_UTC_SECONDS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_EVIDENCE_RE = re.compile(
    r"^https://github\.com/vamseeachanta/workspace-hub/issues/([1-9]\d*)"
    r"#issuecomment-([1-9]\d*)$"
)
# Tailscale protocol address space; tests use synthetic values only.
_TAILSCALE_NETWORKS = (
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("fd7a:115c:a1e0::/48"),
)


class ConnectionResolverError(ValueError):
    def __init__(self, field_path: str, error_class: str, exit_code: int) -> None:
        self.field_path = field_path
        self.error_class = error_class
        self.exit_code = exit_code
        super().__init__(f"{field_path}: {error_class}")


class ConnectionPolicyError(ConnectionResolverError):
    def __init__(self, field_path: str, error_class: str) -> None:
        super().__init__(field_path, error_class, 3)


class FallbackUnavailableError(ConnectionResolverError):
    def __init__(self, field_path: str, error_class: str) -> None:
        super().__init__(field_path, error_class, 4)


class OverlayIntegrityError(ConnectionResolverError):
    def __init__(self, field_path: str, error_class: str) -> None:
        super().__init__(field_path, error_class, 5)


@dataclass(frozen=True)
class ConnectionPolicy:
    machine: str
    ssh: str
    schema_version: int
    preferred_route: str
    fallback_kind: str
    fallback_reference: str
    attestation_issue: int
    max_age_seconds: int
    canonical_bytes: bytes
    sha256: str


@dataclass(frozen=True)
class VerifiedFallback:
    machine: str
    reference: str
    address: ipaddress.IPv4Address | ipaddress.IPv6Address
    verified_at: datetime
    expires_at: datetime


def _require_exact_keys(
    value: Any, expected: set[str], field_path: str, *, exit_code: int = 3
) -> dict[str, Any]:
    if not isinstance(value, dict):
        error = ConnectionPolicyError if exit_code == 3 else FallbackUnavailableError
        raise error(field_path, "invalid_type")
    actual = set(value)
    if actual != expected:
        error = ConnectionPolicyError if exit_code == 3 else FallbackUnavailableError
        error_class = "unknown_field" if actual - expected else "missing_field"
        raise error(field_path, error_class)
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_dns_hostname(value: Any, field_path: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 253:
        raise ConnectionPolicyError(field_path, "invalid_hostname")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ConnectionPolicyError(field_path, "invalid_hostname") from exc
    labels = value.split(".")
    if any(not _DNS_LABEL_RE.fullmatch(label) for label in labels):
        raise ConnectionPolicyError(field_path, "invalid_hostname")
    return value


def _validate_connection_fields(connection: Any) -> tuple[str, int, int]:
    base = "registry.machines[].connection"
    connection = _require_exact_keys(
        connection, {"schema_version", "preferred_route", "fallback"}, base
    )
    if connection["schema_version"] != 1 or not _is_int(connection["schema_version"]):
        raise ConnectionPolicyError(f"{base}.schema_version", "invalid_value")
    if connection["preferred_route"] != "ssh":
        raise ConnectionPolicyError(f"{base}.preferred_route", "invalid_value")
    fallback = _require_exact_keys(
        connection["fallback"],
        {"kind", "reference", "attestation_issue", "max_age_seconds"},
        f"{base}.fallback",
    )
    if fallback["kind"] != "tailscale_ip":
        raise ConnectionPolicyError(f"{base}.fallback.kind", "invalid_value")
    reference = fallback["reference"]
    if not isinstance(reference, str) or not _REFERENCE_RE.fullmatch(reference):
        raise ConnectionPolicyError(f"{base}.fallback.reference", "invalid_value")
    issue = fallback["attestation_issue"]
    if not _is_int(issue) or issue <= 0:
        raise ConnectionPolicyError(
            f"{base}.fallback.attestation_issue", "invalid_value"
        )
    max_age = fallback["max_age_seconds"]
    if not _is_int(max_age) or not 300 <= max_age <= 2_592_000:
        raise ConnectionPolicyError(f"{base}.fallback.max_age_seconds", "invalid_value")
    return reference, issue, max_age


def _validate_machine_policy(machine: MachineRecord) -> ConnectionPolicy | None:
    connection = machine.raw.get("connection")
    if connection is None:
        return None
    reference, issue, max_age = _validate_connection_fields(connection)
    ssh = _validate_dns_hostname(machine.ssh, "registry.machines[].ssh")
    projection = {
        "connection": {
            "fallback": {
                "attestation_issue": issue,
                "kind": "tailscale_ip",
                "max_age_seconds": max_age,
                "reference": reference,
            },
            "preferred_route": "ssh",
            "schema_version": 1,
        },
        "format": "workspace-hub-connection-policy-v1",
        "machine": machine.key,
        "ssh": ssh,
    }
    canonical = json.dumps(
        projection, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return ConnectionPolicy(
        machine=machine.key,
        ssh=ssh,
        schema_version=1,
        preferred_route="ssh",
        fallback_kind="tailscale_ip",
        fallback_reference=reference,
        attestation_issue=issue,
        max_age_seconds=max_age,
        canonical_bytes=canonical,
        sha256=hashlib.sha256(canonical).hexdigest(),
    )


def resolve_connection_policy(
    resolver: WorkstationPathResolver, identifier: str
) -> ConnectionPolicy:
    policies: dict[str, ConnectionPolicy] = {}
    for machine in resolver.machines:
        policy = _validate_machine_policy(machine)
        if policy is not None:
            policies[machine.key] = policy
    selected = resolver.resolve_machine(identifier)
    if selected is None:
        raise ConnectionResolverError("registry.machine", "unknown_machine", 2)
    policy = policies.get(selected.key)
    if policy is None:
        raise ConnectionPolicyError("registry.machines[].connection", "missing_field")
    return policy


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _read_secure_overlay(path: Path, repo_root: Path) -> bytes:
    parent = path.parent
    try:
        parent_stat = parent.lstat()
    except OSError as exc:
        raise FallbackUnavailableError("overlay.parent", "unavailable") from exc
    if not stat.S_ISDIR(parent_stat.st_mode) or parent.is_symlink():
        raise OverlayIntegrityError("overlay.parent", "invalid_type")
    if parent_stat.st_uid != os.getuid():
        raise OverlayIntegrityError("overlay.parent", "wrong_owner")
    if stat.S_IMODE(parent_stat.st_mode) & 0o022:
        raise OverlayIntegrityError("overlay.parent", "unsafe_mode")
    resolved_parent = parent.resolve()
    resolved_path = resolved_parent / path.name
    if _is_within(resolved_path, repo_root.resolve()):
        raise OverlayIntegrityError("overlay.file", "repository_internal")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as exc:
        raise FallbackUnavailableError("overlay.file", "unavailable") from exc
    except OSError as exc:
        raise OverlayIntegrityError("overlay.file", "invalid_type") from exc
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise OverlayIntegrityError("overlay.file", "invalid_type")
        if file_stat.st_uid != os.getuid():
            raise OverlayIntegrityError("overlay.file", "wrong_owner")
        if stat.S_IMODE(file_stat.st_mode) & ~0o600:
            raise OverlayIntegrityError("overlay.file", "unsafe_mode")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(descriptor)


def _parse_timestamp(value: Any, field_path: str) -> datetime:
    if not isinstance(value, str) or not _UTC_SECONDS_RE.fullmatch(value):
        raise FallbackUnavailableError(field_path, "invalid_timestamp")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise FallbackUnavailableError(field_path, "invalid_timestamp") from exc


def _parse_tailscale_address(
    value: Any, field_path: str
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    try:
        address = ipaddress.ip_address(value) if isinstance(value, str) else None
    except ValueError as exc:
        raise FallbackUnavailableError(field_path, "invalid_address") from exc
    if address is None or not any(address in network for network in _TAILSCALE_NETWORKS):
        raise FallbackUnavailableError(field_path, "invalid_range")
    return address


def _validate_overlay_record(
    reference: Any, record: Any, policy: ConnectionPolicy | None
) -> tuple[ipaddress.IPv4Address | ipaddress.IPv6Address, datetime, datetime]:
    base = "overlay.records[]"
    if not isinstance(reference, str) or not _REFERENCE_RE.fullmatch(reference):
        raise FallbackUnavailableError("overlay.records", "invalid_reference")
    record = _require_exact_keys(
        record,
        {
            "machine",
            "address",
            "status",
            "evidence",
            "verified_at",
            "expires_at",
            "connection_policy_sha256",
        },
        base,
        exit_code=4,
    )
    if not isinstance(record["machine"], str):
        raise FallbackUnavailableError(f"{base}.machine", "invalid_type")
    if record["status"] != "verified":
        raise FallbackUnavailableError(f"{base}.status", "unverified")
    evidence = record["evidence"]
    match = _EVIDENCE_RE.fullmatch(evidence) if isinstance(evidence, str) else None
    if match is None:
        raise FallbackUnavailableError(f"{base}.evidence", "invalid_evidence")
    digest = record["connection_policy_sha256"]
    if not isinstance(digest, str) or not _DIGEST_RE.fullmatch(digest):
        raise OverlayIntegrityError(f"{base}.connection_policy_sha256", "invalid_digest")
    address = _parse_tailscale_address(record["address"], f"{base}.address")
    verified_at = _parse_timestamp(record["verified_at"], f"{base}.verified_at")
    expires_at = _parse_timestamp(record["expires_at"], f"{base}.expires_at")
    if policy is not None:
        if reference != policy.fallback_reference:
            raise FallbackUnavailableError("overlay.records", "reference_mismatch")
        if record["machine"] != policy.machine:
            raise FallbackUnavailableError(f"{base}.machine", "machine_mismatch")
        if int(match.group(1)) != policy.attestation_issue:
            raise FallbackUnavailableError(f"{base}.evidence", "issue_mismatch")
        if digest != policy.sha256:
            raise OverlayIntegrityError(
                f"{base}.connection_policy_sha256", "digest_mismatch"
            )
    return address, verified_at, expires_at


def load_verified_fallback(
    overlay_path: Path,
    policy: ConnectionPolicy,
    *,
    now: datetime,
    repo_root: Path,
    platform_name: str | None = None,
) -> VerifiedFallback:
    if (platform_name or os.name) == "nt":
        raise FallbackUnavailableError("overlay", "unsupported_platform")
    raw = _read_secure_overlay(Path(overlay_path), Path(repo_root))
    try:
        payload = load_unique_yaml_bytes(raw, context="overlay") or {}
    except ValueError as exc:
        raise FallbackUnavailableError("overlay", str(exc).split(": ")[-1]) from exc
    payload = _require_exact_keys(payload, {"schema_version", "records"}, "overlay", exit_code=4)
    if payload["schema_version"] != 1 or not _is_int(payload["schema_version"]):
        raise FallbackUnavailableError("overlay.schema_version", "invalid_value")
    records = payload["records"]
    if not isinstance(records, dict):
        raise FallbackUnavailableError("overlay.records", "invalid_type")
    selected = None
    for reference, record in records.items():
        candidate_policy = policy if reference == policy.fallback_reference else None
        parsed = _validate_overlay_record(reference, record, candidate_policy)
        if candidate_policy is not None:
            selected = parsed
    if selected is None:
        raise FallbackUnavailableError("overlay.records", "reference_missing")
    address, verified_at, expires_at = selected
    if now.tzinfo is None or now.utcoffset() != timezone.utc.utcoffset(now):
        raise FallbackUnavailableError("overlay.now", "invalid_timestamp")
    now = now.astimezone(timezone.utc)
    if verified_at > now:
        raise FallbackUnavailableError("overlay.records[].verified_at", "future")
    if expires_at <= verified_at:
        raise FallbackUnavailableError("overlay.records[].expires_at", "invalid_order")
    if expires_at - verified_at > timedelta(seconds=policy.max_age_seconds):
        raise FallbackUnavailableError("overlay.records[].expires_at", "overlong")
    if now >= expires_at:
        raise FallbackUnavailableError("overlay.records[].expires_at", "expired")
    return VerifiedFallback(
        machine=policy.machine,
        reference=policy.fallback_reference,
        address=address,
        verified_at=verified_at,
        expires_at=expires_at,
    )
