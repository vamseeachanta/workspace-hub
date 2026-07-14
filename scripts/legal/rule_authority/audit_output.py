"""Strict value-withholding public output for authority audits."""

from __future__ import annotations

import json
import uuid


class PublicOutputError(ValueError):
    """A public result violated the closed output contract."""


def _canonical(value: dict) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ) + "\n"


def public_result(*, command: str, revision: str, generation: int,
                  objects_examined: int, coverage: str, verdict: str, rc: int) -> str:
    """Encode only the explicitly permitted public summary fields."""
    if command not in {"audit-tree", "audit-index", "audit-history"}:
        raise PublicOutputError("invalid command")
    try:
        parsed = uuid.UUID(revision)
    except (ValueError, AttributeError) as exc:
        raise PublicOutputError("invalid revision") from exc
    if str(parsed) != revision or parsed.version != 4:
        raise PublicOutputError("invalid revision")
    if type(generation) is not int or generation < 1:
        raise PublicOutputError("invalid generation")
    if type(objects_examined) is not int or objects_examined < 0:
        raise PublicOutputError("invalid object count")
    allowed = {
        (0, "clean", "complete"), (1, "blocked", "complete"),
        (2, "error", "partial"), (3, "incomplete", "partial"),
        (4, "error", "partial"),
    }
    if (rc, verdict, coverage) not in allowed:
        raise PublicOutputError("invalid result")
    return _canonical({
        "command": command, "coverage": coverage, "generation": generation,
        "objects_examined": objects_examined, "rc": rc, "revision": revision,
        "verdict": verdict,
    })


def combine_rc(*codes: int) -> int:
    """Apply the normative rc4 > rc3 > rc1 > rc0 precedence."""
    if any(code not in {0, 1, 2, 3, 4} for code in codes):
        raise PublicOutputError("invalid return code")
    return max(codes, key={0: 0, 2: 1, 1: 2, 3: 3, 4: 4}.__getitem__)


def public_failure(command: str, rc: int, _exception: BaseException) -> str:
    """Map arbitrary exceptions to fixed messages without interpolating them."""
    messages = {1: "blocked", 2: "invalid invocation", 3: "coverage incomplete", 4: "audit error"}
    if command not in {"audit-tree", "audit-index", "audit-history"} or rc not in messages:
        raise PublicOutputError("invalid failure")
    return _canonical({"command": command, "message": messages[rc], "rc": rc})
