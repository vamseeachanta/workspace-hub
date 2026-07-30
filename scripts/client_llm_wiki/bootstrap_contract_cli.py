"""Bounded CLI adapter for the client-wiki bootstrap contract."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Sequence

from .bootstrap_attestation import BootstrapManifestError
from .bootstrap_finalizer import (
    BootstrapFinalizerError,
    residue_json,
)


def _contract():
    from . import bootstrap_contract

    return bootstrap_contract


def _validate(args: argparse.Namespace) -> int:
    contract = _contract()
    registry = contract.load_registry(args.registry)
    for warning in registry.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    print(
        json.dumps({"kind": registry.kind.value, "version": registry.registry_version})
    )
    return 0


def _classify(args: argparse.Namespace) -> int:
    contract = _contract()
    registry = contract.load_registry(args.registry)
    entry = contract.get_entry(registry, args.short_name)
    layout = contract.derive_workspace_layout(contract._template_worktree(), entry.repo)
    contract.validate_root_disjointness(
        entry,
        [
            str(layout.template_worktree),
            str(layout.canonical_checkout),
            str(layout.target),
        ],
    )
    payload = {
        "mode": entry.mode.value,
        "repo": entry.repo,
        "short_name": entry.short_name,
        "status": entry.status,
        "target": str(layout.target),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


def _render(args: argparse.Namespace) -> int:
    _rendered, persisted = _contract().execute_render(
        Path(args.registry),
        args.short_name,
        _manifest_path=args.manifest,
    )
    payload = {
        "backing_name": persisted.backing_name,
        "manifest": str(args.manifest),
        "size": len(persisted.bytes),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def _verify(args: argparse.Namespace) -> int:
    _contract().verify_private_repo(args.repo)
    print(json.dumps({"repo": args.repo, "private": True, "archived": False}))
    return 0


def _planned(args: argparse.Namespace):
    contract = _contract()
    entry = contract.get_entry(contract.load_registry(args.registry), args.short_name)
    if entry.status != "planned":
        raise contract.BootstrapContractError("operation requires planned registry state")
    layout = contract.derive_workspace_layout(contract._template_worktree(), entry.repo)
    contract.validate_root_disjointness(
        entry, [str(layout.template_worktree), str(layout.canonical_checkout), str(layout.target)],
    )
    return contract, entry, layout


def _create(args: argparse.Namespace) -> int:
    contract, entry, _layout = _planned(args)
    contract.create_private_repo(entry.repo)
    return 0


def _clone(args: argparse.Namespace) -> int:
    contract, entry, layout = _planned(args)
    contract.clone_private_repo(entry.repo, layout.target)
    return 0


def _finalize(args: argparse.Namespace) -> int:
    result = _contract().finalize_scaffold(
        args.registry, args.short_name, args.manifest
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


def _registry(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--registry", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="client-wiki-bootstrap")
    commands = parser.add_subparsers(dest="command", required=True)
    handlers = (
        ("validate-registry", _validate),
        ("classify", _classify),
        ("render", _render),
        ("finalize-scaffold", _finalize),
        ("create-private-repo", _create),
        ("clone-private-repo", _clone),
    )
    for name, handler in handlers:
        command = commands.add_parser(name)
        _registry(command)
        if name != "validate-registry":
            command.add_argument("--short-name", required=True)
        if name in {"render", "finalize-scaffold"}:
            command.add_argument("--manifest", required=True, type=Path)
        command.set_defaults(handler=handler)
    verify = commands.add_parser("verify-private-repo")
    verify.add_argument("--repo", required=True)
    verify.set_defaults(handler=_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    contract = _contract()
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except BootstrapFinalizerError as exc:
        print(residue_json(exc), file=sys.stderr)
    except (contract.ManifestPersistenceError, BootstrapManifestError) as exc:
        backing = contract.sanitize_backing_name(
            args.manifest.name,
            getattr(exc, "backing_name", None),
        )
        payload = {
            "error": "manifest_persistence_failed",
            "residue": {"backing_name": backing, "residue_policy": "preserved"},
        }
        print(
            json.dumps(payload, sort_keys=True, separators=(",", ":")), file=sys.stderr
        )
    except (
        contract.BootstrapSchemaError,
        contract.BootstrapRenderError,
        contract.BootstrapContractError,
    ) as exc:
        residue = getattr(exc, "residue", None)
        if residue is not None:
            print(
                json.dumps(
                    {"error": "render_failed", "residue": asdict(residue)},
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
    return 1
