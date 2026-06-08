#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""dispatch_lease.py — Distributed dispatch lease over a git ref (issue #2970, F3).

Goal & hard invariant
----------------------
An atomic dispatch lease so that AT MOST ONE machine runs a given task, with
safe failover. The invariant is NO double-execution, even under clock skew or
network partition. We guarantee this with two mechanisms working together:

  1. VERSIONED COMPARE-AND-SWAP (CAS) on the lease ref. Every state transition
     is a non-forced / expected-sha push. Whoever loses the CAS loses the lease;
     there is exactly one winner per transition because git refuses to advance a
     ref whose tip moved. TTL is advisory only (it gates *when* a reclaim may be
     attempted); it never by itself authorizes execution.

  2. A FENCING TOKEN. Each (re)grant of the lease carries a fresh, opaque token
     plus a monotonically increasing `generation`. A caller MUST call
     ``verify_token`` immediately before any externally-visible side effect. If
     the lease has since been reclaimed by another machine, the current blob's
     token differs and the superseded holder gets False and MUST abort. This is
     what defends against the clock-skew / partition window: a holder that
     "thinks" it still owns the lease cannot act once it has been fenced out.

Why both? CAS prevents two machines from *granting* themselves the lease
concurrently (no split-brain at hand-off). The fencing token prevents a *stale*
holder — one that paused (GC, swap, network stall) past its TTL and was validly
reclaimed — from performing a side effect when it wakes up. TTL-only schemes
fail exactly this case; that is why this module is CAS + fencing, not TTL-only.

Injection / purity
------------------
ALL git interaction and ALL nondeterminism are injected. The module never calls
``time``, ``uuid``, or git directly, so behavior is fully deterministic under
test. The caller supplies:

  * a ``git`` object (the Git interface below),
  * ``now: float`` (caller's clock reading),
  * ``new_token: str`` (caller-generated fresh fencing token),
  * for ``reclaim``, a ``liveness_fn`` that reports whether a holder is alive.

Git interface (duck-typed; caller provides an object with these methods)
-----------------------------------------------------------------------
  read_ref(name) -> (sha, blob_dict) | None
      Current tip sha and decoded JSON blob of the lease ref, or None if the
      ref does not exist.

  create_ref(name, blob_dict) -> sha | None
      Create the ref ONLY if absent (models a create-only push). Returns the new
      sha on success, or None if the ref already exists / another machine won the
      creation race. This is the creation arbiter.

  cas_update_ref(name, expected_sha, blob_dict) -> sha | None
      Advance the ref from ``expected_sha`` to a new commit carrying
      ``blob_dict`` ONLY if the ref tip is still ``expected_sha`` (models a
      non-forced / compare-and-swap push). Returns the new sha on success, or
      None if the tip has moved (CAS failed).

Lease ref naming & blob shape
-----------------------------
  ref name:  refs/heads/dispatch/leases/<name>
  blob JSON: {"holder": str, "generation": int, "token": str,
              "ttl_s": int, "renewed_at": float}
"""
from __future__ import annotations

import json
from typing import Any, Callable, Optional, Protocol, Tuple

REF_PREFIX = "refs/heads/dispatch/leases/"


def lease_ref(name: str) -> str:
    """Fully-qualified lease ref for a logical lease ``name``."""
    return REF_PREFIX + name


# --- Git interface (Protocol, for type-checkers; any duck-typed object works) ---
class Git(Protocol):
    def read_ref(self, name: str) -> Optional[Tuple[str, dict]]: ...

    def create_ref(self, name: str, blob: dict) -> Optional[str]: ...

    def cas_update_ref(
        self, name: str, expected_sha: str, blob: dict
    ) -> Optional[str]: ...


# --- Blob (de)serialization ----------------------------------------------------
# The git layer is free to store the blob however it likes; these helpers exist
# so callers/tests can round-trip the canonical JSON shape consistently. The
# acquire/renew/reclaim functions operate on plain dicts and hand them to git as
# dicts, so JSON encoding is the git layer's concern.
def encode_blob(blob: dict) -> str:
    """Canonical JSON encoding of a lease blob (sorted keys, stable)."""
    return json.dumps(blob, sort_keys=True, separators=(",", ":"))


def decode_blob(text: str) -> dict:
    """Decode a lease blob from its JSON text form."""
    return json.loads(text)


def _make_blob(
    holder: str, generation: int, token: str, ttl_s: int, renewed_at: float
) -> dict:
    return {
        "holder": holder,
        "generation": generation,
        "token": token,
        "ttl_s": ttl_s,
        "renewed_at": renewed_at,
    }


def _is_expired(blob: dict, now: float) -> bool:
    # Strictly greater-than: a lease is "fresh" while now - renewed_at <= ttl_s.
    return (now - blob["renewed_at"]) > blob["ttl_s"]


def acquire(
    git: Any,
    name: str,
    holder: str,
    ttl_s: int,
    now: float,
    new_token: str,
) -> Optional[dict]:
    """Attempt to acquire the lease ``name`` for ``holder``.

    Cases:
      * Ref absent  -> create with generation=1. Returns the lease blob on
        success, or None if the creation race was lost (another machine created
        it first).
      * Ref present, fresh (not expired), held by someone else -> None (held).
      * Ref present, held by ``holder`` -> renew (CAS the same generation with
        ``renewed_at=now``, rotating to ``new_token``). Returns the renewed blob,
        or None if the renewal CAS lost.
      * Ref present, expired, held by someone else -> None. Acquire does NOT
        steal an expired lease; that path requires ``reclaim`` (which also checks
        liveness and bumps the generation). This keeps acquire safe: it never
        grants over a possibly-still-live holder.
    """
    cur = git.read_ref(lease_ref(name))
    if cur is None:
        blob = _make_blob(holder, 1, new_token, ttl_s, now)
        sha = git.create_ref(lease_ref(name), blob)
        if sha is None:
            return None  # lost the creation race
        return blob

    _sha, blob = cur
    if blob["holder"] == holder:
        # Re-entrant: refresh our own lease (rotate token to new_token).
        return renew(git, name, holder, now, new_token=new_token)

    # Held by someone else. Acquire never reclaims (expired or not).
    return None


def renew(
    git: Any,
    name: str,
    holder: str,
    now: float,
    new_token: Optional[str] = None,
) -> Optional[dict]:
    """Renew an existing lease held by ``holder`` (same generation).

    CAS-updates the blob with ``renewed_at=now``, keeping the same generation and
    the same token unless ``new_token`` is given (then the token rotates).
    Returns the updated blob on success, or None if:
      * the ref is absent,
      * the lease is no longer held by ``holder``, or
      * the CAS failed because the ref tip moved (someone else advanced it).
    """
    cur = git.read_ref(lease_ref(name))
    if cur is None:
        return None
    sha, blob = cur
    if blob["holder"] != holder:
        return None  # we don't hold it; nothing to renew

    token = new_token if new_token is not None else blob["token"]
    updated = _make_blob(
        holder=holder,
        generation=blob["generation"],  # renew never bumps generation
        token=token,
        ttl_s=blob["ttl_s"],
        renewed_at=now,
    )
    new_sha = git.cas_update_ref(lease_ref(name), sha, updated)
    if new_sha is None:
        return None  # CAS lost: ref moved under us
    return updated


def reclaim(
    git: Any,
    name: str,
    holder: str,
    ttl_s: int,
    now: float,
    new_token: str,
    liveness_fn: Callable[[str], bool],
) -> Optional[dict]:
    """Reclaim an expired-and-dead lease for ``holder``, with a fresh fence.

    Reclaim is the ONLY safe failover path. It proceeds ONLY if BOTH:
      (a) the lease is expired:           now - renewed_at > ttl_s, AND
      (b) the current holder is dead:      liveness_fn(current_holder) is False.

    When both hold, it CAS-updates from the exact sha it just read, setting:
      generation = old_generation + 1   (monotonic fence: supersedes the old holder)
      holder     = us
      token      = new_token             (fresh fencing token)
      ttl_s      = ttl_s
      renewed_at = now

    Returns the new lease blob on success, or None if:
      * ref absent,
      * not expired (still within ttl),
      * holder still alive (liveness_fn True),
      * we already hold it (no self-reclaim; use renew), or
      * the CAS failed because another reclaimer advanced the ref first
        (this is what prevents split-brain double-grant: two reclaimers reading
        the same sha both attempt CAS, but only one matches the current tip).
    """
    cur = git.read_ref(lease_ref(name))
    if cur is None:
        return None
    sha, blob = cur

    if blob["holder"] == holder:
        # We already hold it — reclaim is not the right tool; renew instead.
        return None
    if not _is_expired(blob, now):
        return None  # still fresh: must not steal a possibly-live lease
    if liveness_fn(blob["holder"]):
        return None  # holder is alive: refuse to steal even if TTL elapsed

    new_blob = _make_blob(
        holder=holder,
        generation=blob["generation"] + 1,  # bump generation: fence the old holder
        token=new_token,
        ttl_s=ttl_s,
        renewed_at=now,
    )
    new_sha = git.cas_update_ref(lease_ref(name), sha, new_blob)
    if new_sha is None:
        return None  # another reclaimer won the CAS; we do NOT double-grant
    return new_blob


def verify_token(git: Any, name: str, token: str) -> bool:
    """Fencing check: True iff the CURRENT lease blob's token equals ``token``.

    Callers MUST invoke this immediately before any externally-visible side
    effect. A holder that has been superseded (its lease reclaimed, bumping the
    generation and rotating the token) will see the current token differ from
    its own and get False — it must then abort, guaranteeing no double-execution
    even if its local clock still believes the lease is held.

    Returns False if the ref is absent (no lease -> nothing to fence for -> no
    authority to act).
    """
    cur = git.read_ref(lease_ref(name))
    if cur is None:
        return False
    _sha, blob = cur
    return blob.get("token") == token
