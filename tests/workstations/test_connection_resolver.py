from __future__ import annotations

import importlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from workspace_hub.workstations.resolver import WorkstationPathResolver


NOW = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)


def _connection() -> ModuleType:
    try:
        return importlib.import_module("workspace_hub.workstations.connection")
    except ModuleNotFoundError:
        pytest.fail("connection resolver module is missing")


def _machine(
    *,
    hostname: str = "node-one",
    aliases: list[str] | None = None,
    ssh: object = "node-one",
    connection: object | None = None,
) -> dict[str, object]:
    if connection is None:
        connection = {
            "schema_version": 1,
            "preferred_route": "ssh",
            "fallback": {
                "kind": "tailscale_ip",
                "reference": "node-one-tailscale",
                "attestation_issue": 3550,
                "max_age_seconds": 3600,
            },
        }
    return {
        "hostname": hostname,
        "hostname_aliases": aliases or [],
        "os": "linux",
        "workspace_root": "/srv/workspace-hub",
        "ssh": ssh,
        "connection": connection,
    }


def _registry_bytes(machines: dict[str, object] | None = None) -> bytes:
    payload = {"machines": machines or {"node-one": _machine()}}
    return yaml.safe_dump(payload, sort_keys=False).encode("utf-8")


def _policy(raw: bytes | None = None):
    module = _connection()
    resolver = WorkstationPathResolver.from_registry_bytes(raw or _registry_bytes())
    return module.resolve_connection_policy(resolver, "node-one")


def _overlay_payload(policy, **updates: object) -> dict[str, object]:
    record = {
        "machine": "node-one",
        "address": "100.64.10.20",
        "status": "verified",
        "evidence": (
            "https://github.com/vamseeachanta/workspace-hub/issues/3550"
            "#issuecomment-123456"
        ),
        "verified_at": "2026-07-16T11:30:00Z",
        "expires_at": "2026-07-16T12:30:00Z",
        "connection_policy_sha256": policy.sha256,
    }
    record.update(updates)
    return {"schema_version": 1, "records": {"node-one-tailscale": record}}


def _write_overlay(tmp_path: Path, payload: object) -> Path:
    parent = tmp_path / "external" / "workspace-hub"
    parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    parent.chmod(0o700)
    path = parent / "connection-overlay.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    path.chmod(0o600)
    return path


def _load_overlay(path: Path, policy, tmp_path: Path, **kwargs: object):
    return _connection().load_verified_fallback(
        path,
        policy,
        now=NOW,
        repo_root=tmp_path / "repository",
        **kwargs,
    )


def test_registry_bytes_constructor_and_path_delegate(tmp_path: Path, monkeypatch) -> None:
    raw = _registry_bytes()
    path = tmp_path / "registry.yaml"
    path.write_bytes(raw)
    calls: list[bytes] = []
    original = WorkstationPathResolver.from_registry_bytes.__func__

    def capture(cls, raw_bytes: bytes):
        calls.append(raw_bytes)
        return original(cls, raw_bytes)

    monkeypatch.setattr(WorkstationPathResolver, "from_registry_bytes", classmethod(capture))
    resolver = WorkstationPathResolver.from_registry_path(path)

    assert calls == [raw]
    assert resolver.resolve_machine("node-one").key == "node-one"


def test_registry_rejects_duplicate_yaml_keys_without_echoing_value() -> None:
    raw = b"machines:\n  node-one:\n    hostname: secret-one\n    hostname: secret-two\n"

    with pytest.raises(ValueError, match=r"registry: duplicate_key") as error:
        WorkstationPathResolver.from_registry_bytes(raw)

    assert "secret" not in str(error.value)


def test_same_machine_casefolded_identifier_repetition_is_accepted() -> None:
    resolver = WorkstationPathResolver.from_registry_bytes(
        _registry_bytes({"node-one": _machine(aliases=["NODE-ONE"], ssh="Node-One")})
    )

    assert resolver.resolve_machine("NODE-ONE").key == "node-one"


@pytest.mark.parametrize("collision", ["key", "hostname", "alias", "ssh"])
def test_cross_machine_casefolded_identifier_collision_is_rejected(collision: str) -> None:
    second_key = "node-two"
    second = _machine(hostname="node-two", ssh="ssh-two")
    if collision == "key":
        second_key = "NODE-ONE"
    elif collision == "hostname":
        second["hostname"] = "NODE-ONE"
    elif collision == "alias":
        second["hostname_aliases"] = ["NODE-ONE"]
    else:
        second["ssh"] = "NODE-ONE"

    with pytest.raises(ValueError, match=r"registry\.machines: identifier_collision"):
        WorkstationPathResolver.from_registry_bytes(
            _registry_bytes({"node-one": _machine(), second_key: second})
        )


@pytest.mark.parametrize(
    ("mutation", "error_path"),
    [
        (lambda machine: machine["connection"].update({"extra": True}), "connection"),
        (lambda machine: machine["connection"].update({"schema_version": True}), "schema_version"),
        (lambda machine: machine.update({"ssh": "bad host"}), "ssh"),
        (lambda machine: machine.update({"ssh": None}), "ssh"),
        (lambda machine: machine["connection"]["fallback"].update({"reference": "Bad_Ref"}), "reference"),
        (lambda machine: machine["connection"]["fallback"].update({"attestation_issue": 0}), "attestation_issue"),
        (lambda machine: machine["connection"]["fallback"].update({"max_age_seconds": 299}), "max_age_seconds"),
        (lambda machine: machine["connection"]["fallback"].update({"max_age_seconds": 2592001}), "max_age_seconds"),
    ],
)
def test_connection_policy_schema_is_closed_and_typed(mutation, error_path: str) -> None:
    machine = _machine()
    mutation(machine)
    resolver = WorkstationPathResolver.from_registry_bytes(_registry_bytes({"node-one": machine}))

    with pytest.raises(ValueError, match=error_path):
        _connection().resolve_connection_policy(resolver, "node-one")


def test_full_registry_is_validated_before_selected_policy() -> None:
    invalid = _machine(hostname="node-two", ssh="node-two")
    invalid["connection"]["preferred_route"] = "automatic"
    resolver = WorkstationPathResolver.from_registry_bytes(
        _registry_bytes({"node-one": _machine(), "node-two": invalid})
    )

    with pytest.raises(ValueError, match="preferred_route"):
        _connection().resolve_connection_policy(resolver, "node-one")


def test_policy_lookup_aliases_share_exact_canonical_bytes_and_digest() -> None:
    module = _connection()
    machine = _machine(hostname="node-host", aliases=["node-alias"], ssh="ssh-node")
    resolver = WorkstationPathResolver.from_registry_bytes(_registry_bytes({"node-one": machine}))
    policies = [
        module.resolve_connection_policy(resolver, identifier)
        for identifier in ("node-one", "node-host", "node-alias", "ssh-node")
    ]
    expected = (
        b'{"connection":{"fallback":{"attestation_issue":3550,"kind":"tailscale_ip",'
        b'"max_age_seconds":3600,"reference":"node-one-tailscale"},"preferred_route":'
        b'"ssh","schema_version":1},"format":"workspace-hub-connection-policy-v1",'
        b'"machine":"node-one","ssh":"ssh-node"}'
    )

    assert {policy.canonical_bytes for policy in policies} == {expected}
    assert len({policy.sha256 for policy in policies}) == 1


def test_policy_digest_ignores_unrelated_registry_edits() -> None:
    before = _policy()
    changed = _machine()
    changed["notes"] = "unrelated valid edit"

    assert _policy(_registry_bytes({"node-one": changed})).sha256 == before.sha256


@pytest.mark.parametrize(
    "mutate",
    [
        lambda machine: machine.update({"ssh": "new-node.example"}),
        lambda machine: machine["connection"]["fallback"].update({"reference": "new-ref"}),
        lambda machine: machine["connection"]["fallback"].update({"attestation_issue": 3551}),
        lambda machine: machine["connection"]["fallback"].update({"max_age_seconds": 7200}),
    ],
)
def test_every_mutable_projected_field_changes_digest(mutate) -> None:
    before = _policy()
    changed = _machine()
    mutate(changed)

    assert _policy(_registry_bytes({"node-one": changed})).sha256 != before.sha256


def test_registry_migration_removes_observed_linux_addresses() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    resolver = WorkstationPathResolver.from_registry_path(
        repo_root / "config" / "workstations" / "registry.yaml"
    )

    for identifier in ("dev-primary", "dev-secondary"):
        machine = resolver.resolve_machine(identifier)
        assert "tailscale_ip" not in machine.raw
        assert _connection().resolve_connection_policy(resolver, identifier).machine == identifier


def test_overlay_rejects_duplicate_and_legacy_digest_fields(tmp_path: Path) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy))
    path.write_text(
        "schema_version: 1\nrecords:\n  node-one-tailscale:\n"
        "    machine: node-one\n    machine: other\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate_key"):
        _load_overlay(path, policy, tmp_path)

    payload = _overlay_payload(policy, registry_sha256="0" * 64)
    path = _write_overlay(tmp_path, payload)
    with pytest.raises(ValueError, match="overlay.records.*unknown_field"):
        _load_overlay(path, policy, tmp_path)


@pytest.mark.parametrize("mode", [0o644, 0o700])
def test_overlay_rejects_file_mode_broader_than_0600(tmp_path: Path, mode: int) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy))
    path.chmod(mode)

    with pytest.raises(ValueError, match="overlay.file: unsafe_mode"):
        _load_overlay(path, policy, tmp_path)


def test_overlay_rejects_symlink_unsafe_parent_and_repo_internal_path(tmp_path: Path) -> None:
    policy = _policy()
    real = _write_overlay(tmp_path, _overlay_payload(policy))
    link = real.with_name("link.yaml")
    link.symlink_to(real)
    with pytest.raises(ValueError, match="overlay.file: invalid_type"):
        _load_overlay(link, policy, tmp_path)

    real.parent.chmod(0o777)
    with pytest.raises(ValueError, match="overlay.parent: unsafe_mode"):
        _load_overlay(real, policy, tmp_path)
    real.parent.chmod(0o700)

    repo_root = tmp_path / "repository"
    repo_root.mkdir()
    repo_root.chmod(0o700)
    internal = repo_root / "overlay.yaml"
    internal.write_text(yaml.safe_dump(_overlay_payload(policy)), encoding="utf-8")
    internal.chmod(0o600)
    with pytest.raises(ValueError, match="overlay.file: repository_internal"):
        _connection().load_verified_fallback(internal, policy, now=NOW, repo_root=repo_root)


def test_overlay_rejects_non_owner(tmp_path: Path, monkeypatch) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy))
    monkeypatch.setattr(os, "getuid", lambda: path.stat().st_uid + 1)

    with pytest.raises(ValueError, match="overlay.parent: wrong_owner"):
        _load_overlay(path, policy, tmp_path)


@pytest.mark.parametrize(
    ("updates", "error_path"),
    [
        ({"address": "192.0.2.10"}, "address"),
        ({"address": "not-an-address"}, "address"),
        ({"status": "pending"}, "status"),
        ({"machine": "node-two"}, "machine"),
        ({"evidence": "https://example.invalid/comment"}, "evidence"),
        ({"verified_at": "2026-07-16T12:00:01Z"}, "verified_at"),
        ({"expires_at": "2026-07-16T11:30:00Z"}, "expires_at"),
        ({"expires_at": "2026-07-16T11:29:59Z"}, "expires_at"),
        ({"expires_at": "2026-07-16T13:00:01Z"}, "expires_at"),
        ({"expires_at": "2026-07-16T12:00:00Z"}, "expires_at"),
        ({"verified_at": "2026-07-16T11:30:00+00:00"}, "verified_at"),
        ({"connection_policy_sha256": "A" * 64}, "connection_policy_sha256"),
        ({"connection_policy_sha256": "0" * 64}, "connection_policy_sha256"),
    ],
)
def test_overlay_rejects_invalid_or_mismatched_attestation(
    tmp_path: Path, updates: dict[str, object], error_path: str
) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy, **updates))

    with pytest.raises(ValueError, match=error_path):
        _load_overlay(path, policy, tmp_path)


def test_overlay_accepts_synthetic_verified_tailscale_fallback(tmp_path: Path) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy))

    fallback = _load_overlay(path, policy, tmp_path)

    assert str(fallback.address) == "100.64.10.20"
    assert fallback.machine == "node-one"
    assert fallback.reference == "node-one-tailscale"


def test_windows_fallback_is_explicitly_unsupported(tmp_path: Path) -> None:
    policy = _policy()
    path = _write_overlay(tmp_path, _overlay_payload(policy))

    with pytest.raises(ValueError, match="overlay: unsupported_platform") as error:
        _load_overlay(path, policy, tmp_path, platform_name="nt")

    assert error.value.exit_code == 4
