from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from workspace_hub.workstations import connection_command


NOW = datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)


def _registry_payload() -> dict[str, object]:
    return {
        "machines": {
            "node-one": {
                "hostname": "node-one",
                "hostname_aliases": ["node-alias"],
                "os": "linux",
                "workspace_root": "/srv/workspace-hub",
                "ssh": "node-one.example",
                "connection": {
                    "schema_version": 1,
                    "preferred_route": "ssh",
                    "fallback": {
                        "kind": "tailscale_ip",
                        "reference": "node-one-tailscale",
                        "attestation_issue": 3550,
                        "max_age_seconds": 3600,
                    },
                },
            }
        }
    }


def _write_registry(tmp_path: Path, payload: object | None = None) -> Path:
    path = tmp_path / "repo" / "config" / "workstations" / "registry.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump(payload or _registry_payload(), sort_keys=False), encoding="utf-8")
    return path


def _write_overlay(tmp_path: Path, registry_path: Path) -> Path:
    resolver = connection_command.WorkstationPathResolver.from_registry_path(registry_path)
    policy = connection_command.resolve_connection_policy(resolver, "node-one")
    payload = {
        "schema_version": 1,
        "records": {
            "node-one-tailscale": {
                "machine": "node-one",
                "address": "100.64.10.20",
                "status": "verified",
                "evidence": "https://github.com/vamseeachanta/workspace-hub/issues/3550#issuecomment-123456",
                "verified_at": "2026-07-16T11:30:00Z",
                "expires_at": "2026-07-16T12:30:00Z",
                "connection_policy_sha256": policy.sha256,
            }
        },
    }
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    parent.chmod(0o700)
    path = parent / "connection-overlay.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    path.chmod(0o600)
    return path


def _args(registry: Path, *extra: str) -> list[str]:
    return ["node-one", "--registry-path", str(registry), *extra]


def test_default_and_fallback_argv_keep_canonical_destination(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)
    resolver = connection_command.WorkstationPathResolver.from_registry_path(registry)
    policy = connection_command.resolve_connection_policy(resolver, "node-one")

    assert connection_command.build_ssh_argv(policy, user=None) == [
        "ssh", "-o", "StrictHostKeyChecking=yes", "node-one.example"
    ]
    assert connection_command.build_ssh_argv(policy, user="valid-user", fallback_address="100.64.10.20") == [
        "ssh", "-o", "StrictHostKeyChecking=yes", "-l", "valid-user", "-o",
        "HostName=100.64.10.20", "-o", "HostKeyAlias=node-one.example", "node-one.example",
    ]


@pytest.mark.parametrize("fallback", [False, True])
def test_dry_run_is_exact_redacted_deterministic_json(tmp_path: Path, capsys, fallback: bool) -> None:
    registry = _write_registry(tmp_path)
    resolver = connection_command.WorkstationPathResolver.from_registry_path(registry)
    policy = connection_command.resolve_connection_policy(resolver, "node-one")
    args = _args(registry, "--dry-run", "--user", "secret-user")
    route = "hostname"
    verification = "registry"
    shape = ["ssh", "-o", "StrictHostKeyChecking=yes", "-l", "<redacted>", "<destination>"]
    if fallback:
        overlay = _write_overlay(tmp_path, registry)
        args.extend(["--fallback", "--overlay-path", str(overlay)])
        route = "fallback"
        verification = "verified"
        shape = [
            "ssh", "-o", "StrictHostKeyChecking=yes", "-l", "<redacted>", "-o",
            "HostName=<redacted>", "-o", "HostKeyAlias=<redacted>", "<destination>",
        ]

    def reject_launch(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("dry-run launched a child process")

    assert connection_command.main(
        args,
        now=NOW,
        repo_root=tmp_path / "repo",
        runner=reject_launch,
    ) == 0
    output = capsys.readouterr()
    expected = {
        "argv_shape": shape,
        "machine": "node-one",
        "policy_sha256": policy.sha256,
        "route": route,
        "verification": verification,
    }
    assert output.out == json.dumps(expected, sort_keys=True, separators=(",", ":")) + "\n"
    assert output.err == ""
    assert not any(value in output.out for value in ("node-one.example", "100.64.10.20", "secret-user"))


def test_fallback_is_explicit_only_and_launches_once_without_retry(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)
    overlay = _write_overlay(tmp_path, registry)
    calls: list[tuple[list[str], dict[str, object]]] = []

    def launch(argv: list[str], **kwargs: object):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=255)

    assert connection_command.main(_args(registry), now=NOW, repo_root=tmp_path / "repo", runner=launch) == 255
    assert len(calls) == 1
    assert not any(argument.startswith("HostName=") for argument in calls[0][0])

    calls.clear()
    args = _args(registry, "--fallback", "--overlay-path", str(overlay))
    assert connection_command.main(args, now=NOW, repo_root=tmp_path / "repo", runner=launch) == 255
    assert len(calls) == 1
    assert "HostName=100.64.10.20" in calls[0][0]


def test_launch_inherits_streams_and_sets_no_shell(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)
    observed: dict[str, object] = {}

    def launch(argv: list[str], **kwargs: object):
        observed.update(kwargs)
        return SimpleNamespace(returncode=0)

    assert connection_command.main(_args(registry), now=NOW, repo_root=tmp_path / "repo", runner=launch) == 0
    assert observed == {"check": False, "shell": False}


@pytest.mark.parametrize(
    ("error", "expected"),
    [(FileNotFoundError(), 127), (PermissionError(), 126), (KeyboardInterrupt(), 130)],
)
def test_launch_maps_runtime_failures(error: BaseException, expected: int, tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)

    def launch(argv: list[str], **kwargs: object):
        raise error

    assert connection_command.main(_args(registry), now=NOW, repo_root=tmp_path / "repo", runner=launch) == expected


@pytest.mark.parametrize(
    ("args", "expected", "error_class"),
    [
        (["secret-host"], 2, "unknown_machine"),
        (["node-one", "--registry-path", "missing.yaml"], 3, "registry_unavailable"),
    ],
)
def test_domain_exit_mapping_is_stable_and_redacted(args, expected, error_class, tmp_path: Path, capsys) -> None:
    if args == ["secret-host"]:
        registry = _write_registry(tmp_path)
        args.extend(["--registry-path", str(registry)])

    assert connection_command.main(args, now=NOW, repo_root=tmp_path / "repo") == expected
    output = capsys.readouterr()
    assert output.out == ""
    assert error_class in output.err
    assert "secret-host" not in output.err
    assert "missing.yaml" not in output.err


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda payload: payload["machines"]["node-one"]["connection"].update({"extra": "secret"}), 3),
        (lambda payload: payload["machines"]["node-one"]["connection"]["fallback"].update({"reference": "other"}), 4),
        (lambda payload: payload["machines"]["node-one"]["connection"]["fallback"].update({"max_age_seconds": 7200}), 5),
    ],
)
def test_registry_fallback_and_integrity_exits(mutation, expected: int, tmp_path: Path, capsys) -> None:
    payload = _registry_payload()
    registry = _write_registry(tmp_path, payload)
    overlay = _write_overlay(tmp_path, registry)
    mutation(payload)
    registry.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    args = _args(registry, "--fallback", "--overlay-path", str(overlay))

    assert connection_command.main(args, now=NOW, repo_root=tmp_path / "repo") == expected
    output = capsys.readouterr()
    assert "secret" not in output.err
    assert "100.64.10.20" not in output.err


def test_invalid_user_and_unknown_options_are_redacted_usage_errors(tmp_path: Path, capsys) -> None:
    registry = _write_registry(tmp_path)
    for rejected in ("bad user", "root@host", "-oProxyCommand=secret"):
        args = _args(registry, "--user", rejected) if not rejected.startswith("-o") else _args(registry, rejected)
        with pytest.raises(SystemExit) as error:
            connection_command.main(args, now=NOW, repo_root=tmp_path / "repo")
        assert error.value.code == 2
        output = capsys.readouterr()
        assert output.err == "error: usage\n"
        assert rejected not in output.err


def test_thin_executable_runs_from_non_repository_cwd(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path)
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "operations" / "connection" / "connect-workstation.py"

    result = subprocess.run(
        [sys.executable, str(script), "node-one", "--registry-path", str(registry), "--dry-run"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["machine"] == "node-one"
    assert result.stderr == ""
