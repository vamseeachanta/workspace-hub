"""Owner-authorized Codex trusted-repository contract for issue #3555."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config/workstations/registry.yaml"
TRUST_PATH = ROOT / "config/agents/codex/trusted-repos.yaml"

EXPECTED_MACHINES = {
    "ace-linux-1",
    "ace-linux-2",
    "ace-win-1",
    "ace-win-2",
    "gpu-claw",
    "Vamsees-MacBook-Air",
    "shoerack",
}
EXPECTED_TRUST = {
    (
        "ace-linux-1",
        "/mnt/local-analysis/workspace-hub",  # abs-path-allowed
        "https://github.com/vamseeachanta/workspace-hub.git",
    ),
    (
        "ace-linux-2",
        "/mnt/local-analysis/workspace-hub",  # abs-path-allowed
        "https://github.com/vamseeachanta/workspace-hub",
    ),
    (
        "gpu-claw",
        "/home/undi/ws/workspace-hub",  # abs-path-allowed
        "https://github.com/vamseeachanta/workspace-hub.git",
    ),
}


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope="module")
def registry() -> dict:
    return _load_yaml(REGISTRY_PATH)


@pytest.fixture(scope="module")
def manifest() -> dict:
    return _load_yaml(TRUST_PATH)


def _machine_aliases(registry: dict) -> set[str]:
    aliases: set[str] = set()
    for machine in registry["machines"].values():
        aliases.add(machine["hostname"])
        aliases.update(machine.get("hostname_aliases", []))
    return aliases


def _fleet_rows(registry: dict) -> dict[str, dict]:
    return registry.get("codex_fleet", {}).get("machines", {})


def _checkout_by_root(row: dict, root: str) -> dict | None:
    for checkout in row.get("checkouts", []):
        if checkout.get("canonical_root") == root:
            return checkout
    return None


def _origin_identity(origin: str) -> str | None:
    parsed = urlparse(origin)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    repo_path = parsed.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    return f"{parsed.hostname.casefold()}/{repo_path}"


def _manifest_errors(manifest: dict, registry: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "version",
        "approval_issue",
        "approved_by",
        "approved_at",
        "policy",
        "materialization",
        "repositories",
    }
    errors.extend(f"missing {key}" for key in sorted(required - manifest.keys()))
    if errors:
        return errors

    aliases = _machine_aliases(registry)
    fleet = _fleet_rows(registry)
    for index, entry in enumerate(manifest["repositories"]):
        prefix = f"repositories[{index}]"
        entry_required = {
            "repository_identity",
            "origin",
            "machine_alias",
            "canonical_root",
            "revoked",
        }
        missing = entry_required - entry.keys()
        errors.extend(f"{prefix} missing {key}" for key in sorted(missing))
        if missing:
            continue
        alias = entry["machine_alias"]
        if alias not in aliases or alias not in fleet:
            errors.append(f"{prefix} unknown machine_alias")
            continue
        checkout = _checkout_by_root(fleet[alias], entry["canonical_root"])
        if not checkout or checkout.get("verification") != "LIVE":
            errors.append(f"{prefix} root is not live-verified")
            continue
        if checkout.get("origin") != entry["origin"]:
            errors.append(f"{prefix} origin differs from live evidence")
        if _origin_identity(entry["origin"]) != entry["repository_identity"]:
            errors.append(f"{prefix} repository identity differs from origin")
        if not isinstance(entry["revoked"], bool):
            errors.append(f"{prefix} revoked must be boolean")
        expires_at = entry.get("expires_at")
        if expires_at is not None:
            if not isinstance(expires_at, str):
                errors.append(f"{prefix} expires_at must be ISO-8601 or null")
                continue
            try:
                parsed_expiry = datetime.fromisoformat(
                    expires_at.replace("Z", "+00:00")
                )
                if parsed_expiry.tzinfo is None:
                    raise ValueError("expiry must include a timezone")
            except ValueError:
                errors.append(f"{prefix} expires_at must be ISO-8601 or null")
    return errors


def _is_authorized(
    manifest: dict,
    *,
    machine_alias: str,
    canonical_root: str,
    repository_identity: str,
    origin: str,
    root_exists: bool,
    now: datetime,
) -> bool:
    if not root_exists:
        return False
    for entry in manifest["repositories"]:
        exact = (
            entry["machine_alias"] == machine_alias
            and entry["canonical_root"] == canonical_root
            and entry["repository_identity"] == repository_identity
            and entry["origin"] == origin
        )
        if not exact or entry["revoked"]:
            continue
        expires_at = entry.get("expires_at")
        if expires_at is None:
            return True
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return now < expiry
    return False


def test_fleet_denominator_enumerates_every_registry_machine(registry: dict) -> None:
    """Dropping unreachable or undeclared hosts from the rollout must fail."""
    fleet = _fleet_rows(registry)
    assert set(fleet) == EXPECTED_MACHINES
    registry_hostnames = {
        machine["hostname"] for machine in registry["machines"].values()
    }
    assert set(fleet) == registry_hostnames


def test_fleet_rows_record_probe_and_checkout_evidence(registry: dict) -> None:
    """A green fleet row without transport/probe/origin evidence must fail."""
    registry_by_hostname = {
        machine["hostname"]: machine for machine in registry["machines"].values()
    }
    for alias, row in _fleet_rows(registry).items():
        assert row["transport"]["kind"] in {"local", "ssh", "none"}
        assert row["reachability"] in {"REACHABLE", "UNREACHABLE"}
        assert row["declared_agent_clis"] == registry_by_hostname[alias][
            "capabilities"
        ]["agent_clis"]
        assert row["codex_probe"]["status"] in {"INSTALLED", "NOT-INSTALLED", "UNREACHABLE"}
        assert row["classification"] in {
            "CODEX-TARGET",
            "NOT-CODEX-TARGET",
            "UNREACHABLE",
        }
        for checkout in row["checkouts"]:
            assert set(checkout) >= {
                "repository",
                "canonical_root",
                "verification",
                "origin",
            }
            if checkout["verification"] == "LIVE":
                assert checkout["origin"]
            else:
                assert checkout["origin"] is None


def test_unreachable_hosts_are_named_not_omitted(registry: dict) -> None:
    """Transport gaps must remain explicit denominator failures."""
    fleet = _fleet_rows(registry)
    assert {
        alias
        for alias, row in fleet.items()
        if row["classification"] == "UNREACHABLE"
    } == {"ace-win-1", "ace-win-2", "Vamsees-MacBook-Air", "shoerack"}


def test_manifest_has_owner_authorization_and_fail_closed_policy(
    manifest: dict,
) -> None:
    """Removing owner evidence or broadening matching must fail."""
    assert manifest["version"] == 1
    assert manifest["approval_issue"] == "https://github.com/vamseeachanta/workspace-hub/issues/3555"
    assert manifest["approved_by"] == "vamseeachanta"
    assert manifest["approved_at"] == "2026-08-03T04:08:58Z"
    assert manifest["policy"] == {
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


def test_materialization_contract_is_owner_only_and_activation_gated(
    manifest: dict,
) -> None:
    """A permissive allowlist file or launcher-before-attestation must fail."""
    materialization = manifest["materialization"]
    assert materialization["posix_mode"] == "0600"
    assert materialization["windows_acl"] == "owner-only"
    assert materialization["checks_before_use"] == [
        "expiry",
        "revocation",
        "root-exists",
        "exact-origin",
    ]
    assert materialization["activation_gate"] == {
        "issue": "https://github.com/vamseeachanta/workspace-hub/issues/3555",
        "post_machine_manifest_sha256": True,
        "launcher_must_remain_inactive_until_posted": True,
    }


def test_only_live_verified_workspace_hub_tuples_are_authorized(
    manifest: dict, registry: dict
) -> None:
    """Discovery, an org prefix, or a parent directory must not grant trust."""
    assert _manifest_errors(manifest, registry) == []
    actual = {
        (entry["machine_alias"], entry["canonical_root"], entry["origin"])
        for entry in manifest["repositories"]
    }
    assert actual == EXPECTED_TRUST
    assert {
        entry["repository_identity"] for entry in manifest["repositories"]
    } == {"github.com/vamseeachanta/workspace-hub"}


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("origin", "https://github.com/attacker/workspace-hub.git", "origin differs"),
        ("canonical_root", "/mnt/local-analysis/discovered", "not live-verified"),  # abs-path-allowed
        ("machine_alias", "unknown-host", "unknown machine_alias"),
    ],
)
def test_schema_rejects_drifted_or_unverified_trust_entries(
    manifest: dict, registry: dict, field: str, value: str, message: str
) -> None:
    """A drifted or discovery-only tuple must fail policy validation."""
    candidate = deepcopy(manifest)
    candidate["repositories"][0][field] = value
    assert any(message in error for error in _manifest_errors(candidate, registry))


def test_authorization_requires_exact_tuple_and_existing_root(manifest: dict) -> None:
    """Prefix matches and nonexistent roots must not authorize YOLO."""
    valid = manifest["repositories"][0]
    base = {
        "machine_alias": valid["machine_alias"],
        "canonical_root": valid["canonical_root"],
        "repository_identity": valid["repository_identity"],
        "origin": valid["origin"],
        "root_exists": True,
        "now": datetime(2026, 8, 3, tzinfo=timezone.utc),
    }
    assert _is_authorized(manifest, **base)
    for mutation in (
        {"canonical_root": f"{valid['canonical_root']}-copy"},
        {"canonical_root": "/mnt/local-analysis"},  # abs-path-allowed
        {"origin": f"{valid['origin']}/fork"},
        {"root_exists": False},
    ):
        assert not _is_authorized(manifest, **(base | mutation))


def test_expiry_and_revocation_fail_closed(manifest: dict) -> None:
    """Revoked and expired entries must stop authorizing immediately."""
    candidate = deepcopy(manifest)
    entry = candidate["repositories"][0]
    args = {
        "machine_alias": entry["machine_alias"],
        "canonical_root": entry["canonical_root"],
        "repository_identity": entry["repository_identity"],
        "origin": entry["origin"],
        "root_exists": True,
        "now": datetime(2026, 8, 3, tzinfo=timezone.utc),
    }
    entry["revoked"] = True
    assert not _is_authorized(candidate, **args)
    entry["revoked"] = False
    entry["expires_at"] = "2026-08-02T00:00:00Z"
    assert not _is_authorized(candidate, **args)


@pytest.mark.parametrize(("field", "value"), [("expires_at", 7), ("revoked", "no")])
def test_schema_rejects_invalid_expiry_and_revocation(
    manifest: dict, registry: dict, field: str, value: object
) -> None:
    """Malformed optional expiry or revocation data must fail closed."""
    candidate = deepcopy(manifest)
    candidate["repositories"][0][field] = value
    assert _manifest_errors(candidate, registry)
