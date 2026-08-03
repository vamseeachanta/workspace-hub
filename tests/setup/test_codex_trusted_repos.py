"""Manifest and fleet-denominator integration contract for issue #3555."""

from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from scripts.agents import codex_trust_policy as policy


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config/workstations/registry.yaml"
TRUST_PATH = ROOT / "config/agents/codex/trusted-repos.yaml"
POLICY_PATH = ROOT / "scripts/agents/codex_trust_policy.py"

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


def _fleet(registry: dict) -> dict[str, dict]:
    return registry["codex_fleet"]["machines"]


def test_fleet_denominator_enumerates_every_registry_machine(registry: dict) -> None:
    """Dropping unreachable or undeclared hosts from the rollout must fail."""
    fleet = _fleet(registry)
    assert set(fleet) == EXPECTED_MACHINES
    assert set(fleet) == {
        machine["hostname"] for machine in registry["machines"].values()
    }


def test_production_validators_accept_committed_contract(
    manifest: dict, registry: dict
) -> None:
    """The shipped helper must validate the real denominator and manifest."""
    assert policy.validate_registry_fleet(registry) == []
    assert policy.validate_manifest(manifest, registry) == []


def test_checkout_evidence_states_are_machine_readable(registry: dict) -> None:
    """Origin drift and absent approval evidence must not look merely live."""
    fleet = _fleet(registry)
    primary = {
        item["repository"]: item for item in fleet["ace-linux-1"]["checkouts"]
    }
    assert primary["assethold"]["verification"] == "DIVERGES"
    assert primary["CAD-DEVELOPMENTS"]["verification"] == "MISSING-EVIDENCE"
    for alias in ("ace-win-1", "ace-win-2", "Vamsees-MacBook-Air"):
        assert {
            item["verification"] for item in fleet[alias]["checkouts"]
        } == {"MISSING-EVIDENCE"}


def test_unreachable_hosts_are_named_not_omitted(registry: dict) -> None:
    """Transport gaps must remain explicit denominator failures."""
    assert {
        alias
        for alias, row in _fleet(registry).items()
        if row["classification"] == "UNREACHABLE"
    } == {"ace-win-1", "ace-win-2", "Vamsees-MacBook-Air", "shoerack"}


def test_manifest_has_owner_authorization_and_fail_closed_policy(
    manifest: dict,
) -> None:
    """Removing owner evidence or broadening matching must fail."""
    assert manifest["version"] == 1
    assert manifest["approval_issue"] == (
        "https://github.com/vamseeachanta/workspace-hub/issues/3555"
    )
    assert manifest["approved_by"] == "vamseeachanta"
    assert manifest["approved_at"] == "2026-08-03T04:08:58Z"
    assert manifest["policy"] == policy.SAFE_POLICY


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
    assert policy.validate_manifest(manifest, registry) == []
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
        (
            "canonical_root",
            "/mnt/local-analysis/discovered",  # abs-path-allowed
            "not live-verified",
        ),
        ("machine_alias", "unknown-host", "unknown machine_alias"),
    ],
)
def test_schema_rejects_drifted_or_unverified_trust_entries(
    manifest: dict, registry: dict, field: str, value: str, message: str
) -> None:
    """A drifted or discovery-only tuple must fail production validation."""
    candidate = deepcopy(manifest)
    candidate["repositories"][0][field] = value
    assert any(
        message in error for error in policy.validate_manifest(candidate, registry)
    )


@pytest.mark.parametrize(("field", "value"), [("expires_at", 7), ("revoked", "no")])
def test_schema_rejects_invalid_expiry_and_revocation(
    manifest: dict, registry: dict, field: str, value: object
) -> None:
    """Malformed optional expiry or revocation data must fail closed."""
    candidate = deepcopy(manifest)
    candidate["repositories"][0][field] = value
    assert policy.validate_manifest(candidate, registry)


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("installed_non_target", "INSTALLED requires CODEX-TARGET"),
        ("missing_codex_target", "NOT-INSTALLED requires NOT-CODEX-TARGET"),
        ("unreachable_installed", "UNREACHABLE requires an UNREACHABLE probe"),
        ("no_transport_reachable", "transport kind none requires UNREACHABLE"),
    ],
)
def test_registry_validator_rejects_contradictory_machine_evidence(
    registry: dict, case: str, message: str
) -> None:
    """Transport, reachability, probe, and classification must agree."""
    candidate = deepcopy(registry)
    fleet = _fleet(candidate)
    if case == "installed_non_target":
        fleet["ace-linux-1"]["classification"] = "NOT-CODEX-TARGET"
    elif case == "missing_codex_target":
        fleet["ace-linux-1"]["codex_probe"] = {
            "status": "NOT-INSTALLED",
            "version": None,
        }
    elif case == "unreachable_installed":
        fleet["ace-win-2"]["codex_probe"] = {
            "status": "INSTALLED",
            "version": "0.146.0",
        }
    else:
        fleet["ace-win-2"]["reachability"] = "REACHABLE"
    assert any(
        message in error for error in policy.validate_registry_fleet(candidate)
    )


def test_registry_validator_accepts_not_codex_target(registry: dict) -> None:
    """A reachable machine with an absent CLI must be NOT-CODEX-TARGET."""
    candidate = deepcopy(registry)
    row = _fleet(candidate)["ace-linux-1"]
    row["codex_probe"] = {"status": "NOT-INSTALLED", "version": None}
    row["classification"] = "NOT-CODEX-TARGET"
    assert policy.validate_registry_fleet(candidate) == []


@pytest.mark.parametrize(
    ("verification", "origin", "detail", "message"),
    [
        ("LIVE", None, None, "LIVE requires an origin"),
        ("ABSENT", "https://example.invalid/repo", None, "ABSENT requires null origin"),
        ("DIVERGES", None, "origin conflict", "DIVERGES requires an origin"),
        ("MISSING-EVIDENCE", None, None, "MISSING-EVIDENCE requires detail"),
    ],
)
def test_registry_validator_enforces_checkout_evidence_relationships(
    registry: dict,
    verification: str,
    origin: str | None,
    detail: str | None,
    message: str,
) -> None:
    """Checkout state must constrain its origin and explanatory evidence."""
    candidate = deepcopy(registry)
    checkout = _fleet(candidate)["ace-linux-1"]["checkouts"][0]
    checkout["verification"] = verification
    checkout["origin"] = origin
    if detail is None:
        checkout.pop("detail", None)
    else:
        checkout["detail"] = detail
    assert any(
        message in error for error in policy.validate_registry_fleet(candidate)
    )


def test_policy_functions_respect_fifty_line_limit() -> None:
    """The production helper must retain the repository function-size guardrail."""
    tree = ast.parse(POLICY_PATH.read_text(encoding="utf-8"))
    oversized = {
        node.name: node.end_lineno - node.lineno + 1
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.end_lineno is not None
        and node.end_lineno - node.lineno + 1 > 50
    }
    assert oversized == {}


@pytest.mark.parametrize(
    "candidate",
    [
        {"machines": {}, "codex_fleet": []},
        {"machines": [], "codex_fleet": {"machines": {}}},
    ],
)
def test_registry_schema_malformations_return_errors(candidate: dict) -> None:
    """Malformed container types must fail closed without raising exceptions."""
    assert policy.validate_registry_fleet(candidate)
