#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""dispatch_pull.py — lease-arbitrated PULL dispatch for no-SSH hosts (issue #3000, WF3).

`workstation-dispatch.sh` (F3) reaches machines by SSH push. ace-win-1/2, macbook-portable and
gali-linux-compute-1 are `ssh: null` — they can't be pushed to. This module lets such a host CLAIM
and run work itself, using the F3 git-ref lease (`dispatch_lease.py`) as the arbiter so two hosts
polling the same source never run the same item concurrently.

Lease lifecycle reuse (IMPORTANT): the lease core has NO release/delete — `acquire → renew →
TTL-expire → reclaim`, with `verify_token` for fencing. So this module never "releases": completion
is recorded on the ITEM (`mark_done`); the lease simply lapses via TTL and a crashed holder's lease
is recovered by `reclaim`. `verify_token` is checked before `mark_done` so a holder superseded
mid-run cannot falsely complete an item.

The core (`claim_run`) is pure: git, executor, clock, token and liveness are all injected (mirrors
dispatch_lease.py). The thin agent (`main`) wires the real git adapter + the routed-card source.

On Windows/Git-Bash (no uv): `python -m pip install pyyaml` then
`python scripts/operations/dispatch_pull.py --machine ace-win-1`.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import socket
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Sibling lease cores loaded by path (scripts/ is not an importable package).
_dl = _load("dispatch_lease", _HERE / "dispatch_lease.py")
acquire = _dl.acquire
reclaim = _dl.reclaim
verify_token = _dl.verify_token
lease_ref = _dl.lease_ref


def default_lease_name(item: dict) -> str:
    """Stable lease name for a work item (sanitized for a git ref segment)."""
    raw = str(item["id"])
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")
    return f"dispatch/{slug}"


# ── pure core ────────────────────────────────────────────────────────────────
def claim_run(
    items: Iterable[dict],
    holder: str,
    git: Any,
    executor: Callable[[dict], Any],
    *,
    ttl_s: int,
    now_fn: Callable[[], float],
    token_fn: Callable[[], str],
    liveness_fn: Optional[Callable[[str], bool]] = None,
    mark_done: Optional[Callable[[dict], Any]] = None,
    lease_name_fn: Optional[Callable[[dict], str]] = None,
) -> list[dict]:
    """Claim each item under a fenced git-ref lease, run it once, record completion.

    Per item:
      * acquire the lease (or, if expired and `liveness_fn` says the holder is dead,
        `reclaim` it — acquire never steals an expired lease);
      * if it can't be obtained (held fresh by another host) -> ``skipped_held``;
      * else run ``executor(item)``; on success, fence-check with ``verify_token``:
          - still ours -> ``mark_done(item)`` (if given), status ``ran``;
          - superseded mid-run -> status ``lost_fence`` (NOT marked done);
        an executor exception -> status ``failed`` (NOT marked done -> retried later).

    Returns a per-item list of ``{"id", "status"[, "error"]}``. No lease is ever
    released; it lapses via TTL. Pure — all effects are injected.
    """
    name_of = lease_name_fn or default_lease_name
    out: list[dict] = []
    for item in items:
        name = name_of(item)
        tok = token_fn()
        blob = acquire(git, name, holder, ttl_s, now_fn(), tok)
        if blob is None and liveness_fn is not None:
            blob = reclaim(git, name, holder, ttl_s, now_fn(), tok, liveness_fn)
        if blob is None:
            out.append({"id": item["id"], "status": "skipped_held"})
            continue
        try:
            executor(item)
        except Exception as exc:  # noqa: BLE001 — record and keep going; item stays claimable
            out.append({"id": item["id"], "status": "failed", "error": str(exc)})
            continue
        if verify_token(git, name, tok):
            if mark_done is not None:
                mark_done(item)
            out.append({"id": item["id"], "status": "ran"})
        else:
            out.append({"id": item["id"], "status": "lost_fence"})
    return out


# ── thin agent (real git + routed-card source) ───────────────────────────────
def _resolve_machine(registry_path: Path, host: str) -> Optional[str]:
    """Resolve a hostname to its registry key via the WF1 alias-aware resolver."""
    hr = _load("harness_reconcile", _HERE.parent / "readiness" / "harness_reconcile.py")
    import yaml  # provided by PEP-723 / pip
    machines = (yaml.safe_load(registry_path.read_text()) or {}).get("machines", {})
    return hr.resolve_machine_id(machines, host)


def _read_ready_cards(dispatch_file: Path) -> list[dict]:
    """Read `.claude/dispatch/<machine>.yaml` → items with dispatch_status: ready.
    A missing file is not an error (no routed work yet)."""
    if not dispatch_file.exists():
        return []
    import yaml
    data = yaml.safe_load(dispatch_file.read_text()) or {}
    cards = data.get("cards", []) or []
    return [{"id": c["gh"], "card": c} for c in cards
            if c.get("gh") and c.get("dispatch_status") == "ready"]


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _fetch_lease_refs(repo: Path) -> None:
    """Bring remote lease refs local so CAS sees other hosts' claims (best-effort)."""
    _git(repo, "fetch", "origin",
         "+refs/heads/dispatch-lease/*:refs/heads/dispatch-lease/*")


def _push_lease_refs(repo: Path) -> None:
    """Publish our lease CAS updates to origin (best-effort; per-ref CAS push is the
    operator-verified live step on the no-SSH hosts)."""
    _git(repo, "push", "origin", "refs/heads/dispatch-lease/*")


def _dry_run_executor(item: dict) -> None:
    card = item.get("card", {})
    print(f"  [dry-run] would dispatch {item['id']} "
          f"(provider={card.get('provider', '?')}, repo={card.get('repo', '?')})")


def main(argv=None) -> int:
    import time

    ap = argparse.ArgumentParser(description="lease-arbitrated pull dispatch (#3000)")
    ap.add_argument("--machine", default=None, help="registry machine id (default: this host)")
    ap.add_argument("--ttl", type=int, default=900, help="lease TTL seconds (default 900)")
    ap.add_argument("--apply", action="store_true",
                    help="run the real executor (default: dry-run, claims nothing destructive)")
    ap.add_argument("--repo", default=str(_REPO))
    args = ap.parse_args(argv)

    repo = Path(args.repo)
    registry = repo / "config" / "workstations" / "registry.yaml"
    host = args.machine or socket.gethostname().split(".")[0]
    mid = _resolve_machine(registry, host)
    if mid is None:
        print(f"dispatch-pull: host '{host}' not in registry — nothing to do", file=sys.stderr)
        return 0

    dispatch_file = repo / ".claude" / "dispatch" / f"{mid}.yaml"
    git_lease = _load("git_ref_lease", _HERE / "git_ref_lease.py").GitRefLease(repo)
    holder = f"{mid}:{os.getpid()}:{uuid.uuid4().hex[:8]}"  # unique (the #2991 fix)

    _fetch_lease_refs(repo)
    items = _read_ready_cards(dispatch_file)
    print(f"--- dispatch-pull {mid}: {len(items)} ready item(s) "
          f"[{'apply' if args.apply else 'dry-run'}] ---")

    executor = _dry_run_executor  # --apply wires a real executor in the integration follow-up
    outcomes = claim_run(
        items, holder=holder, git=git_lease, executor=executor,
        ttl_s=args.ttl, now_fn=time.time, token_fn=lambda: uuid.uuid4().hex,
    )
    _push_lease_refs(repo)

    for o in outcomes:
        print(f"  {o['status']:>12}  {o['id']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
