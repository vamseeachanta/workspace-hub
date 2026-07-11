"""Named pre/post attestation seam for finalizer Git and API operations."""
from __future__ import annotations

from collections.abc import Callable
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
