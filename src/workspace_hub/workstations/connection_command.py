from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workspace_hub.workstations.connection import (
    ConnectionPolicy,
    ConnectionResolverError,
    load_verified_fallback,
    resolve_connection_policy,
)
from workspace_hub.workstations.resolver import RegistryValidationError, WorkstationPathResolver


_USER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,31}$")
_REPO_ROOT = Path(__file__).resolve().parents[3]


class _SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.exit(2, "error: usage\n")


def _validated_user(value: str) -> str:
    if not _USER_RE.fullmatch(value):
        raise argparse.ArgumentTypeError("invalid_user")
    return value


def _parser(repo_root: Path) -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(prog="connect-workstation")
    parser.add_argument("machine")
    parser.add_argument("--fallback", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--user", type=_validated_user)
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=repo_root / "config" / "workstations" / "registry.yaml",
    )
    parser.add_argument("--overlay-path", type=Path)
    return parser


def _default_overlay_path() -> Path:
    configured = os.environ.get("XDG_CONFIG_HOME")
    base = Path(configured) if configured else Path.home() / ".config"
    return base / "workspace-hub" / "connection-overlay.yaml"


def build_ssh_argv(
    policy: ConnectionPolicy,
    *,
    user: str | None,
    fallback_address: str | None = None,
) -> list[str]:
    argv = ["ssh", "-o", "StrictHostKeyChecking=yes"]
    if user is not None:
        argv.extend(["-l", user])
    if fallback_address is not None:
        argv.extend(
            [
                "-o",
                f"HostName={fallback_address}",
                "-o",
                f"HostKeyAlias={policy.ssh}",
            ]
        )
    argv.append(policy.ssh)
    return argv


def _argv_shape(*, user: str | None, fallback: bool) -> list[str]:
    shape = ["ssh", "-o", "StrictHostKeyChecking=yes"]
    if user is not None:
        shape.extend(["-l", "<redacted>"])
    if fallback:
        shape.extend(
            [
                "-o",
                "HostName=<redacted>",
                "-o",
                "HostKeyAlias=<redacted>",
            ]
        )
    shape.append("<destination>")
    return shape


def _dry_run_payload(
    policy: ConnectionPolicy,
    *,
    fallback: bool,
    user: str | None,
) -> dict[str, Any]:
    return {
        "argv_shape": _argv_shape(user=user, fallback=fallback),
        "machine": policy.machine,
        "policy_sha256": policy.sha256,
        "route": "fallback" if fallback else "hostname",
        "verification": "verified" if fallback else "registry",
    }


def _emit_dry_run(policy: ConnectionPolicy, *, fallback: bool, user: str | None) -> None:
    payload = _dry_run_payload(policy, fallback=fallback, user=user)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _launch(
    argv: list[str],
    runner: Callable[..., Any],
) -> int:
    try:
        result = runner(argv, check=False, shell=False)
    except FileNotFoundError:
        return 127
    except PermissionError:
        return 126
    except KeyboardInterrupt:
        return 130
    return int(result.returncode)


def _resolve_argv(
    args: argparse.Namespace,
    *,
    now: datetime,
    repo_root: Path,
) -> tuple[ConnectionPolicy, list[str]]:
    resolver = WorkstationPathResolver.from_registry_path(args.registry_path)
    policy = resolve_connection_policy(resolver, args.machine)
    address = None
    if args.fallback:
        overlay_path = args.overlay_path or _default_overlay_path()
        verified = load_verified_fallback(
            overlay_path,
            policy,
            now=now,
            repo_root=repo_root,
        )
        address = str(verified.address)
    return policy, build_ssh_argv(policy, user=args.user, fallback_address=address)


def _emit_domain_error(error: ConnectionResolverError) -> int:
    print(f"error: {error.field_path}: {error.error_class}", file=sys.stderr)
    return error.exit_code


def _execute(
    args: argparse.Namespace,
    *,
    now: datetime,
    repo_root: Path,
    runner: Callable[..., Any],
) -> int:
    try:
        policy, argv = _resolve_argv(args, now=now, repo_root=repo_root)
    except ConnectionResolverError as error:
        return _emit_domain_error(error)
    except RegistryValidationError:
        print("error: registry_validation", file=sys.stderr)
        return 3
    except OSError:
        print("error: registry_unavailable", file=sys.stderr)
        return 3
    if args.dry_run:
        _emit_dry_run(policy, fallback=args.fallback, user=args.user)
        return 0
    return _launch(argv, runner)


def main(
    argv: Sequence[str] | None = None,
    *,
    now: datetime | None = None,
    repo_root: Path | None = None,
    runner: Callable[..., Any] = subprocess.run,
) -> int:
    root = Path(repo_root) if repo_root is not None else _REPO_ROOT
    args = _parser(root).parse_args(argv)
    current_time = now or datetime.now(timezone.utc)
    return _execute(args, now=current_time, repo_root=root, runner=runner)


__all__ = ["build_ssh_argv", "main"]
