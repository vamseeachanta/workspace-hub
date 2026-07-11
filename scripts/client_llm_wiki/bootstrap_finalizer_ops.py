"""Named pre/post attestation seam for finalizer Git and API operations."""
from __future__ import annotations

from collections.abc import Callable
import hashlib
from typing import TypeVar
import re


T = TypeVar("T")
_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")

ATTESTED_OPERATIONS = frozenset({
    "object_format", "symbolic_head", "resolve_head", "index_list",
    "recovery_tree", "commit_read", "index_tree", "hash_object", "mktree",
    "commit_tree", "cas", "read_tree", "push", "api_query", "final_return",
})


def attested(context, operation: str, callback: Callable[[], T], attest: Callable) -> T:
    """Bracket one named injectable operation, including BaseException exits."""
    if operation not in ATTESTED_OPERATIONS:
        raise ValueError("unnamed attested operation")
    attest(context)
    try:
        return callback()
    finally:
        attest(context)


def zero_oid(oid: str) -> str:
    """Return the all-zero CAS old value matching the repository hash width."""
    if _OID.fullmatch(oid) is None:
        raise ValueError("CAS object ID is malformed")
    return "0" * len(oid)


def write_oid(context, expected: str, callback: Callable[[], bytes], attest: Callable,
              created: list[str]) -> str:
    """Record the independently known OID immediately before the write attempt."""
    attest(context)
    created.append(expected)
    raw = callback()
    attest(context)
    try:
        observed = raw.strip().decode()
    except (AttributeError, UnicodeError) as exc:
        raise ValueError("Git returned malformed object OID") from exc
    if observed != expected:
        raise ValueError("Git returned unexpected object OID")
    return expected


def expected_commit_oid(tree: str, name: str, email: str, message: bytes) -> str:
    person = f"{name} <{email}> 0 +0000"
    data = f"tree {tree}\nauthor {person}\ncommitter {person}\n\n".encode() + message
    framed = f"commit {len(data)}\0".encode() + data
    return hashlib.sha1(framed).hexdigest()
