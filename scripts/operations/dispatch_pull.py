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


# ── card -> command binding ──────────────────────────────────────────────────
#
# A card is an ISSUE, and an issue's work is generally not a shell one-liner.
# The card carries `gh`, `repo`, `url`, `domain`, `provider`, `dispatch_status`,
# `wip_eligible`, `routed_by` — and, deliberately, no title (#3768). There is no
# field on it a payload could be read from.
#
# Three ways to supply one were available; this module takes the third.
#
#   1. A `command:` field ON the card. Rejected: `dispatch.py --write` rebuilds
#      `.claude/dispatch/<machine>.yaml` wholesale from `route.py` proposals, so
#      a hand-added field is destroyed by the next routing run. A binding that
#      evaporates on a schedule is worse than none.
#   2. A per-domain / per-provider default template. Rejected: `domain` is a
#      routing axis, not a statement about what the work IS. `dev-primary` alone
#      holds 1344 cards; one template per domain would fire the same command at
#      hundreds of unrelated issues, and every one of them would produce a
#      record. That is the false-completion failure this stack exists to close,
#      automated.
#   3. An explicit per-issue map, kept OUTSIDE the generated queue. Chosen. It
#      survives regeneration, it is reviewable in a diff, and — the part that
#      matters — writing an entry is a deliberate human act, which is where the
#      plan-approval gate already lives. An issue nobody has bound is an issue
#      nobody has authorised to run unattended.
#
# An unbound card is REFUSED and reported as `no_command`. It is never executed,
# never marked done, and never silently absent from the report.

#: Default location of the map, relative to the repo root. Not under
#: `.claude/dispatch/<machine>.yaml`'s naming, so `dispatch.py`'s glob and the
#: staleness sweep both leave it alone.
COMMAND_MAP_REL = Path(".claude") / "dispatch" / "commands.yaml"

#: Same shape drain.py validates (`ISSUE_RE`). Checked at LOAD time: a key that
#: cannot match any card would otherwise be an entry that binds nothing, forever,
#: with no signal — a typo indistinguishable from a deliberate omission.
_BINDING_KEY_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+#[0-9]+$")

#: The environment gate drain.py and reconcile.py already share. Declared here by
#: NAME only: this module never sets it. `--apply` is the first gate, this is the
#: second, and one flag must not be able to satisfy both.
APPLY_FLAG = "DISPATCH_APPLY_ENABLED"

#: Deferral statuses. Distinct values, not a shared "skipped": an operator
#: reading a nightly log has to be able to tell "the router capped this" from
#: "nobody has said what this card runs", because the two need different actions.
NO_COMMAND = "no_command"
WIP_CAPPED = "wip_capped"


class UndefinedPayload(RuntimeError):
    """No command is bound to this card. Raised instead of running anything."""


class DrainFailed(RuntimeError):
    """drain.py exited nonzero. Carries the child's code so it is not lost."""

    def __init__(self, issue: str, returncode: int):
        self.returncode = returncode
        super().__init__(f"{issue}: drain.py exited {returncode}")


def item_key(item: dict) -> str:
    """The issue ref a card binds under — `owner/repo#N`."""
    card = item.get("card") or {}
    return str(card.get("gh") or item.get("id") or "")


def load_command_bindings(path) -> dict[str, str]:
    """Read the per-issue command map. Absent file -> no bindings (not an error).

    A missing map means the fleet runs nothing, loudly — the correct posture for
    a loop that would otherwise have to guess. What is NOT tolerated is a map
    that looks like it binds something and does not: a malformed key or a
    non-string command raises rather than being skipped, because both would read
    as "configured" in review and behave as "unbound" at runtime.
    """
    path = Path(path)
    if not path.exists():
        return {}
    import yaml
    data = yaml.safe_load(path.read_text()) or {}
    raw = data.get("commands") or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: 'commands' must be a mapping of issue -> command")
    out: dict[str, str] = {}
    for key, value in raw.items():
        key = str(key)
        if not _BINDING_KEY_RE.match(key):
            raise ValueError(
                f"{path}: binding key {key!r} is not owner/repo#N — it can never "
                f"match a card, so it would bind nothing without saying so")
        if not isinstance(value, str):
            raise ValueError(
                f"{path}: command for {key} must be a string, got "
                f"{type(value).__name__}")
        out[key] = value
    return out


def resolve_command(item: dict, bindings: dict) -> Optional[str]:
    """The command bound to this card, or None. Blank is None.

    An empty command is not an empty payload: `run.sh` would execute nothing and
    exit 0, and the drain would record a clean completion for work that never
    happened. Whitespace-only is the same defect with a space in it.
    """
    value = bindings.get(item_key(item))
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def partition_runnable(items: Iterable[dict], bindings: dict) -> tuple[list[dict], list[dict]]:
    """Split cards into (runnable, deferred-with-a-reason) BEFORE any claim.

    Deferring here rather than inside the executor keeps unrunnable cards from
    touching the lease refs at all — a card that cannot run should not create,
    renew, or contend for a lease that another host then has to wait out.

    `wip_eligible` is checked first: the router's cap is about whether this card
    may run NOW, which is decided regardless of what it would run. A MISSING flag
    is treated as capped — an absent field is not permission (the same fail-closed
    reading `dispatch.py` gives an absent `generated_at`).
    """
    runnable: list[dict] = []
    deferred: list[dict] = []
    for item in items:
        card = item.get("card") or {}
        if card.get("wip_eligible") is not True:
            deferred.append({"id": item["id"], "status": WIP_CAPPED,
                             "reason": "not wip_eligible — the router capped it"})
            continue
        if resolve_command(item, bindings) is None:
            deferred.append({"id": item["id"], "status": NO_COMMAND,
                             "reason": f"no command bound in {COMMAND_MAP_REL}"})
            continue
        runnable.append(item)
    return runnable, deferred


def make_drain_executor(*, repo, records_dir, machine: str, bindings: dict,
                        apply: bool = False, run=None, drain_py=None,
                        python: str | None = None) -> Callable[[dict], int]:
    """Build the executor `claim_run` runs: one card -> one `drain.py` process.

    Injected, not hardcoded — `claim_run` stays pure and this stays testable
    without a subprocess. `run` defaults to `subprocess.run`.

    drain.py is invoked rather than imported so its exit code is the interface:
    0 only for a dry run or work that genuinely succeeded, 1 when the loop closed
    but the work did not (`blocked` lands here, carrying `unknown-outcome`), 2
    when the loop did not close. Anything nonzero raises, so `claim_run` records
    `failed` and never calls `mark_done`.

    The child's environment is INHERITED, never augmented: `--apply` is this
    module's gate, `DISPATCH_APPLY_ENABLED` is drain's, and an executor that set
    the second one would collapse two gates into one flag.
    """
    run = run or subprocess.run
    repo = Path(repo)
    records_dir = Path(records_dir)
    drain_py = Path(drain_py) if drain_py else repo / "scripts" / "dispatch" / "drain.py"
    python = python or sys.executable

    def executor(item: dict) -> int:
        issue = item_key(item)
        command = resolve_command(item, bindings)
        if command is None:
            # Reached only when a caller wires this straight into `claim_run`
            # without `partition_runnable`. It must still refuse: the guard that
            # exists in one place is the guard that gets bypassed.
            raise UndefinedPayload(
                f"{issue}: no command bound in {COMMAND_MAP_REL} — refusing to "
                f"invent a payload")
        argv = [python, str(drain_py),
                "--issue", issue,
                "--records", str(records_dir),
                "--repo-root", str(repo),
                "--machine", machine,
                "--command", command]
        if apply:
            argv.append("--apply")
        done = run(argv, cwd=str(repo), check=False)
        if done.returncode != 0:
            raise DrainFailed(issue, done.returncode)
        return done.returncode

    return executor


def main(argv=None) -> int:
    import time

    ap = argparse.ArgumentParser(description="lease-arbitrated pull dispatch (#3000)")
    ap.add_argument("--machine", default=None, help="registry machine id (default: this host)")
    ap.add_argument("--ttl", type=int, default=900, help="lease TTL seconds (default 900)")
    ap.add_argument("--apply", action="store_true",
                    help="run the real executor (default: dry-run, claims nothing destructive)")
    ap.add_argument("--commands", default=None,
                    help=f"per-issue command map (default: <repo>/{COMMAND_MAP_REL})")
    ap.add_argument("--repo", default=str(_REPO))
    args = ap.parse_args(argv)

    # Two gates, checked before anything is fetched, read or claimed. Asking for
    # writes is not being permitted them, and a refusal that happens after the
    # lease refs move has already had an effect.
    if args.apply and os.environ.get(APPLY_FLAG) != "1":
        print(f"dispatch-pull: REFUSED — --apply needs {APPLY_FLAG}=1 as well. "
              f"Nothing claimed.", file=sys.stderr)
        return 2

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

    bindings = load_command_bindings(Path(args.commands) if args.commands
                                     else repo / COMMAND_MAP_REL)

    _fetch_lease_refs(repo)
    items = _read_ready_cards(dispatch_file)
    runnable, deferred = partition_runnable(items, bindings)
    print(f"--- dispatch-pull {mid}: {len(items)} ready, {len(runnable)} runnable, "
          f"{len(deferred)} deferred [{'apply' if args.apply else 'dry-run'}] ---")

    executor = make_drain_executor(repo=repo, records_dir=repo / ".claude" / "dispatch" / "records",
                                   machine=mid, bindings=bindings, apply=args.apply)
    outcomes = claim_run(
        runnable, holder=holder, git=git_lease, executor=executor,
        ttl_s=args.ttl, now_fn=time.time, token_fn=lambda: uuid.uuid4().hex,
    )
    _push_lease_refs(repo)

    # Deferrals are printed with the runs, not summarised away: a card nobody has
    # bound must be as visible as one that ran, or the queue silently stalls at
    # full length while the log looks clean.
    for o in deferred + outcomes:
        print(f"  {o['status']:>12}  {o['id']}"
              + (f"  — {o['reason']}" if o.get("reason") else "")
              + (f"  — {o['error']}" if o.get("error") else ""))
    # Nonzero only for a drain that actually failed. `no_command` is a standing
    # configuration gap across a 1300-card backlog; alarming on it every poll
    # would train the operator to ignore the exit code that reports a real break.
    return 1 if any(o["status"] == "failed" for o in outcomes) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
