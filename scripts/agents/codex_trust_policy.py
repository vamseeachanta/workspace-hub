"""Fail-closed trusted-repository policy consumed by Codex launchers."""

from __future__ import annotations

import ntpath
import os
import posixpath
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

Platform = Literal["posix", "windows"]
CHECKOUT_STATES = {"LIVE", "ABSENT", "DIVERGES", "MISSING-EVIDENCE"}
SAFE_POLICY = {
    "authorization_match": "exact-machine-root-identity-origin",
    "live_discovery_authorizes": False,
    "organization_prefix_authorizes": False,
    "directory_parent_authorizes": False,
    "unverified_roots_authorize": False,
    "root_normalization": {
        "resolve_symlinks_and_junctions": True,
        "normalize_windows_drive_and_unc_spelling": True,
        "casefold_windows_paths": True,
        "require_existing_root": True,
    },
}


class TrustPolicyError(ValueError):
    """The trust policy or candidate root cannot be evaluated safely."""


@dataclass(frozen=True)
class AuthorizationDecision:
    authorized: bool
    reason: str
    canonical_root: str | None = None


def _platform(platform: Platform | None) -> Platform:
    selected = platform or ("windows" if os.name == "nt" else "posix")
    if selected not in {"posix", "windows"}:
        raise TrustPolicyError(f"unsupported platform: {selected}")
    return selected


def normalize_path_spelling(path: str | os.PathLike[str], *, platform: Platform) -> str:
    """Normalize an absolute path lexically for exact policy comparison."""
    value = os.fspath(path)
    if platform == "posix":
        if not posixpath.isabs(value):
            raise TrustPolicyError("root must be absolute")
        return posixpath.normpath(value)
    value = value.replace("/", "\\")
    lowered = value.casefold()
    if lowered.startswith("\\\\?\\unc\\"):
        value = "\\\\" + value[8:]
    elif lowered.startswith("\\\\?\\"):
        value = value[4:]
    normalized = ntpath.normpath(value)
    drive, _ = ntpath.splitdrive(normalized)
    if not drive or not ntpath.isabs(normalized):
        raise TrustPolicyError("Windows root must use an absolute drive or UNC path")
    normalized = normalized.rstrip("\\")
    if normalized.endswith(":"):
        normalized += "\\"
    return normalized.casefold()


def normalize_root(
    root: str | os.PathLike[str], *, platform: Platform | None = None
) -> str:
    """Resolve an existing directory and return deterministic platform spelling."""
    selected = _platform(platform)
    try:
        resolved = Path(root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise TrustPolicyError(f"root does not exist: {root}") from exc
    if not resolved.is_dir():
        raise TrustPolicyError(f"root is not a directory: {root}")
    return normalize_path_spelling(resolved, platform=selected)


def _parse_expiry(value: object) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TrustPolicyError("expires_at must be ISO-8601 or null")
    try:
        expiry = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TrustPolicyError("expires_at must be ISO-8601 or null") from exc
    if expiry.tzinfo is None:
        raise TrustPolicyError("expires_at must include a timezone")
    return expiry


def _required_errors(value: object, fields: set[str], prefix: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{prefix} must be a mapping"]
    return [f"{prefix} missing {key}" for key in sorted(fields - value.keys())]


def _checkout_errors(checkout: object, prefix: str) -> list[str]:
    required = {"repository", "canonical_root", "verification", "origin"}
    errors = _required_errors(checkout, required, prefix)
    if errors or not isinstance(checkout, dict):
        return errors
    state = checkout["verification"]
    origin = checkout["origin"]
    detail = checkout.get("detail")
    if state not in CHECKOUT_STATES:
        return [f"{prefix} invalid verification state {state!r}"]
    if state == "LIVE" and not origin:
        errors.append(f"{prefix} LIVE requires an origin")
    if state == "ABSENT" and origin is not None:
        errors.append(f"{prefix} ABSENT requires null origin")
    if state == "DIVERGES" and not origin:
        errors.append(f"{prefix} DIVERGES requires an origin")
    if state in {"DIVERGES", "MISSING-EVIDENCE"} and not detail:
        errors.append(f"{prefix} {state} requires detail")
    return errors


def _transport_errors(row: dict, prefix: str) -> list[str]:
    transport = row.get("transport")
    errors = _required_errors(transport, {"kind", "endpoint"}, f"{prefix}.transport")
    if errors or not isinstance(transport, dict):
        return errors
    kind = transport["kind"]
    endpoint = transport["endpoint"]
    if kind not in {"local", "ssh", "none"}:
        errors.append(f"{prefix} invalid transport kind {kind!r}")
    if kind == "ssh" and not isinstance(endpoint, str):
        errors.append(f"{prefix} ssh transport requires an endpoint")
    if kind in {"local", "none"} and endpoint is not None:
        errors.append(f"{prefix} {kind} transport requires a null endpoint")
    if kind == "none" and row.get("reachability") != "UNREACHABLE":
        errors.append(f"{prefix} transport kind none requires UNREACHABLE")
    return errors


def _probe_errors(row: dict, prefix: str) -> list[str]:
    probe = row.get("codex_probe")
    errors = _required_errors(probe, {"status", "version"}, f"{prefix}.codex_probe")
    if errors or not isinstance(probe, dict):
        return errors
    reachability = row.get("reachability")
    status = probe["status"]
    classification = row.get("classification")
    if reachability == "UNREACHABLE":
        if status != "UNREACHABLE":
            errors.append(f"{prefix} UNREACHABLE requires an UNREACHABLE probe")
        if classification != "UNREACHABLE":
            errors.append(f"{prefix} UNREACHABLE requires UNREACHABLE classification")
        if probe["version"] is not None:
            errors.append(f"{prefix} UNREACHABLE probe requires null version")
    elif status == "INSTALLED":
        if classification != "CODEX-TARGET":
            errors.append(f"{prefix} INSTALLED requires CODEX-TARGET")
        if not isinstance(probe["version"], str):
            errors.append(f"{prefix} INSTALLED requires a version")
    elif status == "NOT-INSTALLED":
        if classification != "NOT-CODEX-TARGET":
            errors.append(f"{prefix} NOT-INSTALLED requires NOT-CODEX-TARGET")
        if probe["version"] is not None:
            errors.append(f"{prefix} NOT-INSTALLED requires null version")
    else:
        errors.append(f"{prefix} reachable row requires an installed-state probe")
    return errors


def _fleet_row_errors(alias: str, row: object, declared_clis: object) -> list[str]:
    prefix = f"codex_fleet.machines.{alias}"
    required = {
        "transport", "reachability", "declared_agent_clis", "codex_probe",
        "classification", "checkouts",
    }
    errors = _required_errors(row, required, prefix)
    if errors or not isinstance(row, dict):
        return errors
    if row["reachability"] not in {"REACHABLE", "UNREACHABLE"}:
        errors.append(f"{prefix} invalid reachability")
    if row["declared_agent_clis"] != declared_clis:
        errors.append(f"{prefix} declared_agent_clis differs from machine registry")
    errors.extend(_transport_errors(row, prefix))
    errors.extend(_probe_errors(row, prefix))
    if not isinstance(row["checkouts"], list):
        return errors + [f"{prefix}.checkouts must be a list"]
    for index, checkout in enumerate(row["checkouts"]):
        errors.extend(_checkout_errors(checkout, f"{prefix}.checkouts[{index}]"))
        if (
            row["reachability"] == "UNREACHABLE"
            and isinstance(checkout, dict)
            and checkout.get("verification") != "MISSING-EVIDENCE"
        ):
            errors.append(f"{prefix} unreachable checkout requires MISSING-EVIDENCE")
    return errors


def validate_registry_fleet(registry: object) -> list[str]:
    """Return fail-closed denominator schema and relational errors."""
    errors = _required_errors(registry, {"machines", "codex_fleet"}, "registry")
    if errors or not isinstance(registry, dict):
        return errors
    codex_fleet = registry["codex_fleet"]
    machines = registry["machines"]
    if not isinstance(codex_fleet, dict) or not isinstance(machines, dict):
        return ["registry machines and codex_fleet must be mappings"]
    fleet = codex_fleet.get("machines")
    if not isinstance(fleet, dict):
        return ["registry machines and codex_fleet.machines must be mappings"]
    if any(not isinstance(row, dict) for row in machines.values()):
        return ["registry machine entries must be mappings"]
    by_hostname = {row.get("hostname"): row for row in machines.values()}
    if set(fleet) != set(by_hostname):
        errors.append("codex_fleet must enumerate every registry hostname exactly")
    for alias, row in fleet.items():
        machine = by_hostname.get(alias, {})
        declared = machine.get("capabilities", {}).get("agent_clis")
        errors.extend(_fleet_row_errors(alias, row, declared))
    return errors


def _origin_identity(origin: object) -> str | None:
    if not isinstance(origin, str):
        return None
    parsed = urlparse(origin)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    repo_path = parsed.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    return f"{parsed.hostname.casefold()}/{repo_path}"


def _entry_errors(entry: object, index: int, fleet: dict) -> list[str]:
    prefix = f"repositories[{index}]"
    required = {
        "repository_identity", "origin", "machine_alias", "canonical_root", "revoked",
    }
    errors = _required_errors(entry, required, prefix)
    if errors or not isinstance(entry, dict):
        return errors
    alias = entry["machine_alias"]
    row = fleet.get(alias)
    if not isinstance(row, dict):
        return [f"{prefix} unknown machine_alias"]
    checkout = next(
        (
            item for item in row.get("checkouts", [])
            if item.get("canonical_root") == entry["canonical_root"]
        ),
        None,
    )
    if not checkout or checkout.get("verification") != "LIVE":
        errors.append(f"{prefix} root is not live-verified")
        return errors
    if checkout.get("origin") != entry["origin"]:
        errors.append(f"{prefix} origin differs from live evidence")
    if _origin_identity(entry["origin"]) != entry["repository_identity"]:
        errors.append(f"{prefix} repository identity differs from origin")
    if not isinstance(entry["revoked"], bool):
        errors.append(f"{prefix} revoked must be boolean")
    try:
        _parse_expiry(entry.get("expires_at"))
    except TrustPolicyError as exc:
        errors.append(f"{prefix} {exc}")
    return errors


def _policy_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("version") != 1:
        errors.append("version must be 1")
    for key in ("approval_issue", "approved_by", "approved_at"):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            errors.append(f"{key} must be a non-empty string")
    if manifest.get("policy") != SAFE_POLICY:
        errors.append("policy does not match the fail-closed contract")
    materialization = manifest.get("materialization", {})
    if materialization.get("posix_mode") != "0600":
        errors.append("materialization.posix_mode must be 0600")
    if materialization.get("windows_acl") != "owner-only":
        errors.append("materialization.windows_acl must be owner-only")
    return errors


def validate_manifest(manifest: object, registry: object) -> list[str]:
    """Return owner-authorization schema and exact evidence errors."""
    required = {
        "version", "approval_issue", "approved_by", "approved_at", "policy",
        "materialization", "repositories",
    }
    errors = _required_errors(manifest, required, "manifest")
    errors.extend(validate_registry_fleet(registry))
    if errors or not isinstance(manifest, dict) or not isinstance(registry, dict):
        return errors
    errors.extend(_policy_errors(manifest))
    repositories = manifest["repositories"]
    if not isinstance(repositories, list):
        return errors + ["repositories must be a list"]
    fleet = registry["codex_fleet"]["machines"]
    for index, entry in enumerate(repositories):
        errors.extend(_entry_errors(entry, index, fleet))
    return errors


def _matching_entry(
    manifest: dict,
    machine_alias: str,
    repository_identity: str,
    origin: str,
) -> dict | None:
    for entry in manifest.get("repositories", []):
        if (
            entry.get("machine_alias") == machine_alias
            and entry.get("repository_identity") == repository_identity
            and entry.get("origin") == origin
        ):
            return entry
    return None


def _entry_decision(
    entry: dict,
    observed_root: str,
    *,
    platform: Platform,
    now: datetime,
) -> AuthorizationDecision:
    try:
        approved_root = normalize_root(entry["canonical_root"], platform=platform)
        expiry = _parse_expiry(entry.get("expires_at"))
    except (KeyError, TrustPolicyError):
        return AuthorizationDecision(False, "policy-invalid")
    if observed_root != approved_root:
        return AuthorizationDecision(False, "exact-root-mismatch", observed_root)
    if entry.get("revoked") is not False:
        return AuthorizationDecision(False, "revoked", observed_root)
    if expiry is not None and now >= expiry:
        return AuthorizationDecision(False, "expired", observed_root)
    return AuthorizationDecision(True, "authorized", observed_root)


def authorize_repository(
    manifest: dict,
    registry: dict,
    *,
    machine_alias: str,
    root: str | os.PathLike[str],
    repository_identity: str,
    origin: str,
    platform: Platform | None = None,
    now: datetime | None = None,
) -> AuthorizationDecision:
    """Authorize only an existing root matching the exact owner-approved tuple."""
    if validate_manifest(manifest, registry):
        return AuthorizationDecision(False, "policy-invalid")
    selected = _platform(platform)
    try:
        observed_root = normalize_root(root, platform=selected)
    except TrustPolicyError:
        return AuthorizationDecision(False, "root-missing")
    entry = _matching_entry(manifest, machine_alias, repository_identity, origin)
    if entry is None:
        return AuthorizationDecision(False, "exact-tuple-mismatch", observed_root)
    effective_now = now or datetime.now(timezone.utc)
    return _entry_decision(
        entry, observed_root, platform=selected, now=effective_now
    )
