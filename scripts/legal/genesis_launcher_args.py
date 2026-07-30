"""Strict argument parser for the owner-only genesis launcher."""

from __future__ import annotations

import re
import uuid
import posixpath


_CANONICAL_OPTIONS = (
    "tool_repo",
    "tool_sha",
    "out_parent",
    "transaction_id",
    "approval_record",
    "approval_sha256",
    "python_realpath",
    "python_sha256",
)
_OID = re.compile(r"[0-9a-f]{40}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _validate_scalar(name: str, value: str) -> None:
    if type(value) is not str or not value:
        raise ValueError(f"invalid value for option: --{name.replace('_', '-')}")
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        raise ValueError(f"invalid value for option: --{name.replace('_', '-')}")
    if name == "tool_sha" and _OID.fullmatch(value) is None:
        raise ValueError("invalid tool sha")
    if name in {"approval_sha256", "python_sha256"} and _SHA256.fullmatch(value) is None:
        raise ValueError(f"invalid {name}")
    if name == "transaction_id":
        try:
            parsed = uuid.UUID(value)
        except ValueError as exc:
            raise ValueError("invalid transaction id") from exc
        if parsed.version != 4 or str(parsed) != value:
            raise ValueError("invalid transaction id")
    if name in {"out_parent", "python_realpath"}:
        if not value.startswith("/"):
            raise ValueError(f"option must be absolute: --{name.replace('_', '-')}")
        if posixpath.normpath(value) != value or "//" in value:
            raise ValueError(f"option must be canonical: --{name.replace('_', '-')}")


def parse_launcher_args(argv: list[str]) -> dict[str, str]:
    if not argv:
        raise ValueError("missing command")

    parsed = {"command": argv[0]}
    if parsed["command"] != "genesis-current":
        raise ValueError(f"unsupported command: {parsed['command']}")

    if len(argv) != 1 + len(_CANONICAL_OPTIONS) * 2:
        raise ValueError("invalid canonical argument count")

    index = 1
    for name in _CANONICAL_OPTIONS:
        option = argv[index]
        expected = "--" + name.replace("_", "-")
        if option != expected:
            raise ValueError(f"expected option: {expected}")
        value = argv[index + 1]
        _validate_scalar(name, value)
        parsed[name] = value
        index += 2

    return parsed
