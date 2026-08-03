"""Runtime behavior for the reusable Codex trusted-repository policy."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from inspect import signature
from pathlib import Path

import pytest
import yaml
from scripts.agents import codex_trust_policy as policy


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config/workstations/registry.yaml"
TRUST_PATH = ROOT / "config/agents/codex/trusted-repos.yaml"


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.fixture
def registry() -> dict:
    return _load_yaml(REGISTRY_PATH)


@pytest.fixture
def manifest() -> dict:
    return _load_yaml(TRUST_PATH)


def _local_policy(
    manifest: dict, registry: dict, canonical_root: Path
) -> tuple[dict, dict]:
    local_manifest = deepcopy(manifest)
    local_manifest["repositories"] = [deepcopy(manifest["repositories"][0])]
    entry = local_manifest["repositories"][0]
    entry["canonical_root"] = str(canonical_root)
    local_registry = deepcopy(registry)
    checkouts = local_registry["codex_fleet"]["machines"]["ace-linux-1"][
        "checkouts"
    ]
    workspace = next(
        item for item in checkouts if item["repository"] == "workspace-hub"
    )
    workspace["canonical_root"] = str(canonical_root)
    return local_manifest, local_registry


def _authorization_args(entry: dict, root: Path) -> dict:
    return {
        "machine_alias": entry["machine_alias"],
        "root": root,
        "repository_identity": entry["repository_identity"],
        "origin": entry["origin"],
        "platform": "posix",
        "now": datetime(2026, 8, 3, tzinfo=timezone.utc),
    }


def test_normalize_root_resolves_symlink_and_rejects_missing(tmp_path: Path) -> None:
    """Authorization must resolve the real existing checkout, not trust a string."""
    target = tmp_path / "repo"
    target.mkdir()
    link = tmp_path / "repo-link"
    link.symlink_to(target, target_is_directory=True)
    assert policy.normalize_root(link, platform="posix") == str(target.resolve())
    with pytest.raises(policy.TrustPolicyError, match="does not exist"):
        policy.normalize_root(tmp_path / "missing", platform="posix")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (r"D:/WS/Repo/../Project", r"d:\ws\project"),  # abs-path-allowed
        (r"\\?\UNC\Server\Share\Repo\..", r"\\server\share"),
    ],
)
def test_windows_root_spelling_is_drive_unc_and_case_normalized(
    raw: str, expected: str
) -> None:
    """Windows drive and UNC aliases must collapse deterministically."""
    assert policy.normalize_path_spelling(raw, platform="windows") == expected


def test_authorize_repository_uses_realpath_and_exact_tuple(
    tmp_path: Path, manifest: dict, registry: dict
) -> None:
    """A symlink may resolve to the exact root; prefix/origin drift may not."""
    target = tmp_path / "workspace-hub"
    target.mkdir()
    link = tmp_path / "workspace-link"
    link.symlink_to(target, target_is_directory=True)
    local_manifest, local_registry = _local_policy(manifest, registry, target)
    entry = local_manifest["repositories"][0]
    kwargs = _authorization_args(entry, link)
    decision = policy.authorize_repository(local_manifest, local_registry, **kwargs)
    assert decision.authorized
    assert decision.canonical_root == str(target.resolve())
    for mutation in (
        {"origin": f"{kwargs['origin']}/fork"},
        {"repository_identity": "github.com/vamseeachanta/workspace-hub-copy"},
        {"machine_alias": "unknown-host"},
    ):
        rejected = policy.authorize_repository(
            local_manifest, local_registry, **(kwargs | mutation)
        )
        assert not rejected.authorized


def test_authorize_repository_checks_filesystem_not_caller_boolean(
    tmp_path: Path, manifest: dict, registry: dict
) -> None:
    """A nonexistent approved string must fail without a root_exists shortcut."""
    missing = tmp_path / "missing"
    local_manifest, local_registry = _local_policy(manifest, registry, missing)
    entry = local_manifest["repositories"][0]
    decision = policy.authorize_repository(
        local_manifest,
        local_registry,
        **_authorization_args(entry, missing),
    )
    assert not decision.authorized
    assert decision.reason == "root-missing"
    assert "root_exists" not in signature(policy.authorize_repository).parameters


def test_production_authorization_enforces_expiry_and_revocation(
    tmp_path: Path, manifest: dict, registry: dict
) -> None:
    """The reusable consumer must deny expired and revoked entries."""
    target = tmp_path / "workspace-hub"
    target.mkdir()
    local_manifest, local_registry = _local_policy(manifest, registry, target)
    entry = local_manifest["repositories"][0]
    kwargs = _authorization_args(entry, target)
    entry["revoked"] = True
    assert policy.authorize_repository(
        local_manifest, local_registry, **kwargs
    ).reason == "revoked"
    entry["revoked"] = False
    entry["expires_at"] = "2026-08-02T00:00:00Z"
    assert policy.authorize_repository(
        local_manifest, local_registry, **kwargs
    ).reason == "expired"


def test_authorization_rejects_registry_evidence_drift(
    tmp_path: Path, manifest: dict, registry: dict
) -> None:
    """An approved tuple must still match the machine-readable live evidence."""
    target = tmp_path / "workspace-hub"
    target.mkdir()
    local_manifest, local_registry = _local_policy(manifest, registry, target)
    workspace = local_registry["codex_fleet"]["machines"]["ace-linux-1"][
        "checkouts"
    ][0]
    workspace["origin"] = "https://github.com/attacker/workspace-hub.git"
    entry = local_manifest["repositories"][0]
    decision = policy.authorize_repository(
        local_manifest,
        local_registry,
        **_authorization_args(entry, target),
    )
    assert not decision.authorized
    assert decision.reason == "policy-invalid"
