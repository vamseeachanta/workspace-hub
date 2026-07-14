#!/usr/bin/env python3
"""Public-safe Phase A operator interface for legal rule authority."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from rule_authority.ci_contract import validate_workflow_context
from rule_authority.codec import AuthorityFormatError, decode_document

MAX_PUBLIC_BYTES = 2 * 1024 * 1024


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="manage_rule_authority.py")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-public")
    validate.add_argument("--registry", required=True)
    validate.add_argument("--policy", required=True)
    workflow = commands.add_parser("validate-workflow-context")
    for name in ("event-name", "repository", "head-repository", "base-ref",
                 "head-sha", "tool-sha"):
        workflow.add_argument(f"--{name}", required=True)
    return parser


def _read(path: str) -> bytes:
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_PUBLIC_BYTES + 1)
    if len(raw) > MAX_PUBLIC_BYTES:
        raise ValueError("public authority too large")
    return raw


def _emit(value: dict, stream) -> None:
    stream.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def _validate_public(args: argparse.Namespace) -> int:
    registry = decode_document("registry", _read(args.registry))
    policy = decode_document("policy", _read(args.policy))
    identity = (registry["generation"], registry["authority_revision"])
    if (policy["generation"], policy["authority_revision"]) != identity:
        raise ValueError("public authority identity mismatch")
    _emit({
        "authority_revision": identity[1], "command": "validate-public",
        "generation": identity[0], "rc": 0, "verdict": "valid",
    }, sys.stdout)
    return 0


def _validate_workflow(args: argparse.Namespace) -> int:
    validate_workflow_context({
        "base_ref": args.base_ref, "event_name": args.event_name,
        "head_repository": args.head_repository, "head_sha": args.head_sha,
        "repository": args.repository, "tool_sha": args.tool_sha,
    })
    _emit({"command": "validate-workflow-context", "rc": 0, "verdict": "valid"},
          sys.stdout)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-public":
            return _validate_public(args)
        return _validate_workflow(args)
    except (AuthorityFormatError, OSError, UnicodeError, ValueError):
        _emit({"command": args.command, "message": "invalid public authority", "rc": 2},
              sys.stderr)
        return 2


if __name__ == "__main__":
    os.environ.pop("PYTHONPATH", None)
    raise SystemExit(main())
