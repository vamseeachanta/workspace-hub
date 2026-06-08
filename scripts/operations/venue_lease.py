#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""venue_lease.py — single-active-venue lease (issue #2971, F4).

Goal
----
Exactly ONE host runs a Telegram venue's WRITE functions (client-visible side
effects), while READ-only functions are NEVER gated — so a lease problem can
never silently stop the safe, multi-host-friendly reads. This is the
Codex-reviewed design: gating is PER-CAPABILITY, not one blanket gate.

Layering
--------
This module is a thin policy layer on top of the F3 dispatch lease
(`dispatch_lease.py`, the versioned-CAS + fencing-token primitive) and its
real-git adapter (`git_ref_lease.py`). It owns:

  * the venue's capability → criticality map (which functions are WRITE vs READ),
  * the venue lease name,
  * the gating decision (`is_gated`),
  * the host-ownership decision for a capability (`holds_venue`), and
  * the fencing wrapper a write function must call immediately before its side
    effect (`fence`).

All git interaction and nondeterminism stay injected exactly as in F3: the
caller passes a `git` object, `now`, and `new_token`; `holds_venue` optionally
accepts a `liveness_fn` to enable safe reclaim of an expired+dead holder.

The dependency modules live in `scripts/operations/` and are NOT importable as a
package, so they are loaded by FILE PATH via importlib (same pattern the F3
real-git tests use).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable, Optional

# --- importlib-by-path load of the F3 dependencies (same dir, not a package) ---
_OPS_DIR = Path(__file__).resolve().parent


def _load(mod_name: str, file_name: str):
    path = _OPS_DIR / file_name
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {mod_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dispatch_lease = _load("dispatch_lease", "dispatch_lease.py")
git_ref_lease = _load("git_ref_lease", "git_ref_lease.py")

# --- Venue policy -------------------------------------------------------------
# write = client-visible side effect → MUST be single-host (gated by the lease).
# read  = safe to run on every host → NEVER gated (so lease trouble can't stop it).
VENUE_CAPABILITIES: dict[str, str] = {
    "escalation-sweep": "write",
    "bot-send": "write",
    "member-audit": "read",
    "parity": "read",
}

VENUE_LEASE_NAME = "venue-telegram"


def is_gated(capability: str) -> bool:
    """True iff ``capability`` is a WRITE capability (and therefore lease-gated).

    Fails CLOSED on an unknown capability: a function we don't recognize might
    have a client-visible side effect, so we refuse to make a gating decision
    rather than silently treating it as a safe read.
    """
    try:
        criticality = VENUE_CAPABILITIES[capability]
    except KeyError:
        raise ValueError(f"unknown venue capability: {capability!r}")
    return criticality == "write"


def holds_venue(
    git: Any,
    capability: str,
    holder: str,
    ttl_s: int,
    now: float,
    new_token: str,
    *,
    liveness_fn: Optional[Callable[[str], bool]] = None,
) -> dict:
    """Decide whether ``holder`` may run ``capability`` for the venue right now.

    Returns ``{"allowed": bool, "reason": str, "lease": dict | None}``.

    READ capability
        Never gated → ``allowed=True``, ``lease=None``, reason ``"read-not-gated"``.
        No lease is touched, so reads run on every host regardless of lease state.

    WRITE capability
        Attempt to acquire/renew the venue lease for ``holder``:
          * Lease free (absent)             → acquire (generation 1) → allowed.
          * Lease already held by ``holder`` → renew (re-entrant)    → allowed.
          * Lease held by another FRESH host → allowed=False, reason "held by <h>".
          * Lease held by an EXPIRED host    → if ``liveness_fn`` is given AND the
            holder is dead, reclaim (fences the old holder, generation+1) → allowed;
            otherwise allowed=False (we never steal a possibly-live lease).

    The returned ``lease`` blob carries the fencing ``token`` the caller must
    later pass to :func:`fence` immediately before the side effect.
    """
    if not is_gated(capability):  # READ (or raises ValueError on unknown)
        return {"allowed": True, "reason": "read-not-gated", "lease": None}

    name = VENUE_LEASE_NAME

    # acquire handles both the free-create case and the re-entrant renew case.
    lease = dispatch_lease.acquire(git, name, holder, ttl_s, now, new_token)
    if lease is not None:
        return {"allowed": True, "reason": "acquired", "lease": lease}

    # We did not get it via acquire. Inspect why.
    cur = git.read_ref(dispatch_lease.lease_ref(name))
    if cur is None:
        # Lost a creation race (someone created it between our read and create).
        return {"allowed": False, "reason": "lost creation race", "lease": None}

    _sha, blob = cur
    other = blob["holder"]

    # If the current holder is expired and we were handed a liveness probe, try a
    # safe reclaim (only succeeds if the holder is also dead; bumps generation).
    if liveness_fn is not None:
        reclaimed = dispatch_lease.reclaim(
            git, name, holder, ttl_s, now, new_token, liveness_fn
        )
        if reclaimed is not None:
            return {"allowed": True, "reason": "reclaimed", "lease": reclaimed}

    return {"allowed": False, "reason": f"held by {other}", "lease": None}


def fence(git: Any, token: str) -> bool:
    """Fencing check for the venue lease — call IMMEDIATELY before a side effect.

    Thin wrapper over :func:`dispatch_lease.verify_token` bound to the venue
    lease. Returns True iff the venue lease's CURRENT token still equals
    ``token``. A write function MUST call this just before its client-visible
    action; on False (the lease was reclaimed by another host and the token
    rotated) the function MUST abort — guaranteeing no double-execution even if
    this host still locally believes it holds the lease.
    """
    return dispatch_lease.verify_token(git, VENUE_LEASE_NAME, token)
