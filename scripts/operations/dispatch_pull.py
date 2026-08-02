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
#: Status for a card the run declined to reach because it hit its own ceiling.
#: Distinct from WIP_CAPPED (the ROUTER capped it) — the two need different
#: actions from an operator, and a shared "skipped" would hide which one fired.
RUN_CAPPED = "run_capped"


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
    max_cards: Optional[int] = None,
    delay_s: float = 0.0,
    sleep_fn: Optional[Callable[[float], Any]] = None,
    on_outcome: Optional[Callable[[dict], Any]] = None,
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

    Pacing (#3773 R6). ``max_cards`` bounds how many cards this run may HAND TO
    the executor, and ``delay_s`` puts a gap between those hand-offs. Both matter
    because one card is not one cheap operation: each drain writes two commits to
    `main` and pushes them, so an unbounded pass over the `dev-primary` queue was
    ~1344 cards x 2 commits, unattended, into a repo with CI and a PII gate.

      * The budget is spent on EXECUTOR CALLS, not on items seen. A card held by
        another host writes nothing to `main`, so it must not consume the ceiling
        — otherwise a busy fleet would starve this host's run of real work.
      * A card that FAILED still spent its budget: the drain had already run and
        already committed by the time it returned nonzero.
      * Cards past the ceiling are reported as ``run_capped``, never dropped. A
        queue that silently shrinks to the cap reads as a completed night.
      * The delay separates executions only; the run does not wait out a pause
        for cards it has already declined.
      * There is NO retry loop here. A card that failed stays claimable and is
        picked up by a later run, which is bounded by its own ceiling.

    ``on_outcome`` is called with each outcome dict as it is produced, so a caller
    can journal progress while the run is still in flight (a summary written only
    at the end is lost exactly when the run dies mid-way).

    Returns a per-item list of ``{"id", "status"[, "error"|"reason"]}``. No lease
    is ever released; it lapses via TTL. Pure — all effects are injected.
    """
    name_of = lease_name_fn or default_lease_name
    out: list[dict] = []
    attempted = 0

    def emit(outcome: dict) -> None:
        out.append(outcome)
        if on_outcome is not None:
            on_outcome(outcome)

    for item in items:
        if max_cards is not None and attempted >= max_cards:
            emit({"id": item["id"], "status": RUN_CAPPED,
                  "reason": f"per-run cap of {max_cards} cards reached"})
            continue
        if attempted and delay_s > 0 and sleep_fn is not None:
            sleep_fn(delay_s)
        name = name_of(item)
        tok = token_fn()
        blob = acquire(git, name, holder, ttl_s, now_fn(), tok)
        if blob is None and liveness_fn is not None:
            blob = reclaim(git, name, holder, ttl_s, now_fn(), tok, liveness_fn)
        if blob is None:
            emit({"id": item["id"], "status": "skipped_held"})
            continue
        attempted += 1
        try:
            executor(item)
        except FleetPaused as exc:
            # STOP, do not `continue`. The operator set the sentinel; every
            # remaining card would refuse identically, and recording each as a
            # failure buries the one fact that matters. Not marked done — the
            # card was never started and stays claimable.
            emit({"id": item["id"], "status": "paused", "reason": str(exc)})
            break
        except Exception as exc:  # noqa: BLE001 — record and keep going; item stays claimable
            emit({"id": item["id"], "status": "failed", "error": str(exc)})
            continue
        if verify_token(git, name, tok):
            if mark_done is not None:
                mark_done(item)
            emit({"id": item["id"], "status": "ran"})
        else:
            emit({"id": item["id"], "status": "lost_fence"})
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


# The namespace the LEASE WRITER uses, imported — never restated. Two literals
# that happen to agree are one edit away from the #3772 defect: this module used
# to sync `refs/heads/dispatch-lease/*` while `dispatch_lease` wrote
# `refs/heads/dispatch/leases/*`, so no lease ever left the host and every host
# won every claim it made. Cross-machine mutual exclusion was zero.
LEASE_REF_GLOB = _dl.REF_PREFIX + "*"


def lease_fetch_refspec() -> str:
    """Force-fetch refspec: overwrite our view with the fleet's (peers are truth)."""
    return f"+{LEASE_REF_GLOB}:{LEASE_REF_GLOB}"


def lease_push_refspec() -> str:
    """Non-forced push refspec. Each lease commit is parented on the one it
    supersedes, so a legitimate CAS fast-forwards and a stale one is rejected."""
    return LEASE_REF_GLOB


def _fetch_lease_refs(repo: Path) -> subprocess.CompletedProcess:
    """Bring remote lease refs local so CAS sees other hosts' claims (best-effort)."""
    return _git(repo, "fetch", "origin", lease_fetch_refspec())


def _push_lease_refs(repo: Path) -> subprocess.CompletedProcess:
    """Publish our lease CAS updates to origin. Best-effort, but the return code is
    handed back so the run summary can say the fleet went unsynced rather than
    leaving a silent no-op that looks exactly like a clean night."""
    return _git(repo, "push", "origin", lease_push_refspec())


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


#: drain.py's PAUSED exit (#3773 R2) — the `.claude/dispatch/PAUSE` sentinel is
#: set, so it refused to claim ANYTHING. This is not a property of the card.
FLEET_PAUSED_EXIT = 3


class FleetPaused(RuntimeError):
    """The operator paused the fleet. Stop the run; do not blame the card.

    Separated from `DrainFailed` because collapsing them makes the kill switch
    produce the loudest possible false alarm and stop nothing: every card walks
    the queue recording a failure it did not cause — ~1344 of them on
    `dev-primary`. An exit that means "the system said no" is not an exit that
    means "this unit of work broke", and only the first should end the loop.
    """

    def __init__(self, issue: str):
        super().__init__(f"{issue}: drain.py reports the fleet is paused")


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
        # Checked BEFORE the generic nonzero branch: a paused fleet is not a
        # failed card, and the order is what keeps the kill switch from being
        # reported as 1344 defects (#3773 R2).
        if done.returncode == FLEET_PAUSED_EXIT:
            raise FleetPaused(issue)
        if done.returncode != 0:
            raise DrainFailed(issue, done.returncode)
        return done.returncode

    return executor


# ── the run log ─────────────────────────────────────────────────────────────
#
# The failure this closes: a night that refused 1344 cards and a night that
# completed 1344 produced the SAME evidence — the stdout of a process nobody was
# attached to. There was no artifact to read in the morning, so "nothing broke"
# and "everything broke" were indistinguishable.
#
# It is a dated JSONL under `logs/`, which `.gitignore` excludes wholesale
# (`logs/*`, with named exceptions this path is not among). That is deliberate
# and load-bearing, not incidental: this repo is PUBLIC and gated by a PII scan.

#: Log directory, relative to the repo root. Local-only by `.gitignore`.
RUN_LOG_DIR_REL = Path("logs") / "dispatch-pull"

#: The ONLY keys copied out of an outcome into a log line.
#:
#: An allow-list, not a filter. Issue TITLES were removed from the dispatch
#: surface because they leaked client identifiers into this public repo (#3768);
#: a journal that serialised the outcome — or worse, the card — would reinstate
#: exactly that leak one layer below the fix. `owner/repo#N` is a reference, not
#: prose, and is what an operator needs to act. `reason` and `error` are this
#: module's own strings (a cap message, a drain exit code), never child output.
LOGGED_KEYS = ("status", "reason", "error")


def run_log_path(repo, *, today: Optional[str] = None) -> Path:
    """Dated log file for a run: ``<repo>/logs/dispatch-pull/YYYY-MM-DD.jsonl``."""
    from datetime import datetime, timezone
    day = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return Path(repo) / RUN_LOG_DIR_REL / f"{day}.jsonl"


class RunLog:
    """Append-only JSONL journal: one line per card, one summary line per run.

    Append, never truncate — two runs can share a night, and the second must not
    erase the first's evidence. Each line is written and flushed as it happens,
    so a run killed mid-way still leaves everything it got through.
    """

    def __init__(self, path, *, run_id: str, machine: str,
                 now_fn: Optional[Callable[[], float]] = None):
        import time as _time
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.machine = machine
        self._now = now_fn or _time.time

    def _append(self, record: dict) -> dict:
        import json
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def _stamp(self, event: str) -> dict:
        return {"event": event, "ts": self._now(), "run_id": self.run_id,
                "machine": self.machine}

    def card(self, outcome: dict, *, attempt: int = 1) -> dict:
        """One line for one card on one attempt. Built from `LOGGED_KEYS` only."""
        record = self._stamp("card")
        record["issue"] = str(outcome.get("id", ""))
        record["attempt"] = attempt
        for key in LOGGED_KEYS:
            if outcome.get(key) is not None:
                record[key] = str(outcome[key])
        return self._append(record)

    def summary(self, outcomes: Iterable[dict], **extra) -> dict:
        """The end-of-run line: how many of each cause, so the morning question
        ("did anything happen?") has an answer that outlives the terminal."""
        counts: dict[str, int] = {}
        total = 0
        for outcome in outcomes:
            counts[str(outcome.get("status"))] = counts.get(str(outcome.get("status")), 0) + 1
            total += 1
        record = self._stamp("run_summary")
        record["counts"] = counts
        record["total"] = total
        record.update({k: v for k, v in extra.items() if k not in record})
        return self._append(record)


# ── CLI ─────────────────────────────────────────────────────────────────────

#: Conservative by construction. Five cards is ten commits to `main` per run —
#: a number an operator can review in the morning. Raising it is a deliberate
#: flag on the command line, which is where that decision belongs.
DEFAULT_MAX_CARDS = 5

#: Seconds between hand-offs. Spaces the pushes so a run cannot present CI and
#: the PII gate with a burst.
DEFAULT_DELAY_S = 30.0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="lease-arbitrated pull dispatch (#3000)")
    ap.add_argument("--machine", default=None, help="registry machine id (default: this host)")
    ap.add_argument("--ttl", type=int, default=900, help="lease TTL seconds (default 900)")
    ap.add_argument("--apply", action="store_true",
                    help="run the real executor (default: dry-run, claims nothing destructive)")
    ap.add_argument("--commands", default=None,
                    help=f"per-issue command map (default: <repo>/{COMMAND_MAP_REL})")
    ap.add_argument("--repo", default=str(_REPO))
    # A ceiling, not a switch: there is no value here that means "unbounded".
    # `0` runs nothing, negatives are rejected, and the default is finite.
    ap.add_argument("--max-cards", type=_non_negative_int, default=DEFAULT_MAX_CARDS,
                    help=f"cards this run may hand to the executor "
                         f"(default {DEFAULT_MAX_CARDS}; 0 runs none)")
    ap.add_argument("--delay", type=_non_negative_float, default=DEFAULT_DELAY_S,
                    help=f"seconds between cards (default {DEFAULT_DELAY_S})")
    ap.add_argument("--log-dir", default=None,
                    help=f"run-log directory (default: <repo>/{RUN_LOG_DIR_REL})")
    return ap


def _non_negative_int(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError(
            f"{text}: the per-run cap is a ceiling; there is no unbounded value")
    return value


def _non_negative_float(text: str) -> float:
    value = float(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"{text}: delay cannot be negative")
    return value


def main(argv=None) -> int:
    import time

    args = build_parser().parse_args(argv)

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

    # Opened BEFORE anything is claimed. A journal created only once there is
    # something to write reports nothing about the runs that died before their
    # first card — which are the runs worth reading about.
    run_id = uuid.uuid4().hex[:12]
    log_path = run_log_path(repo)
    if args.log_dir:
        log_path = Path(args.log_dir) / log_path.name
    log = RunLog(log_path, run_id=run_id, machine=mid)

    fetch = _fetch_lease_refs(repo)
    items = _read_ready_cards(dispatch_file)
    runnable, deferred = partition_runnable(items, bindings)
    print(f"--- dispatch-pull {mid}: {len(items)} ready, {len(runnable)} runnable, "
          f"{len(deferred)} deferred, cap {args.max_cards}, delay {args.delay}s "
          f"[{'apply' if args.apply else 'dry-run'}] run {run_id} ---")
    for o in deferred:
        log.card(o)

    executor = make_drain_executor(repo=repo, records_dir=repo / ".claude" / "dispatch" / "records",
                                   machine=mid, bindings=bindings, apply=args.apply)
    outcomes = claim_run(
        runnable, holder=holder, git=git_lease, executor=executor,
        ttl_s=args.ttl, now_fn=time.time, token_fn=lambda: uuid.uuid4().hex,
        max_cards=args.max_cards, delay_s=args.delay, sleep_fn=time.sleep,
        on_outcome=log.card,
    )
    push = _push_lease_refs(repo)

    # Deferrals are printed with the runs, not summarised away: a card nobody has
    # bound must be as visible as one that ran, or the queue silently stalls at
    # full length while the log looks clean.
    for o in deferred + outcomes:
        print(f"  {o['status']:>12}  {o['id']}"
              + (f"  — {o['reason']}" if o.get("reason") else "")
              + (f"  — {o['error']}" if o.get("error") else ""))

    # The line that answers "what happened last night". `fetch_rc`/`push_rc` are
    # in it because a sync that failed leaves this host's leases invisible to the
    # fleet — the #3772 failure mode, reachable again transiently (offline host,
    # rejected push) and otherwise indistinguishable from a quiet night.
    summary = log.summary(deferred + outcomes, apply=bool(args.apply),
                          max_cards=args.max_cards, delay_s=args.delay,
                          ready=len(items), fetch_rc=fetch.returncode,
                          push_rc=push.returncode)
    print(f"--- summary {summary['counts']} of {summary['total']} "
          f"(fetch rc {fetch.returncode}, push rc {push.returncode}) "
          f"-> {log.path} ---")

    # Nonzero only for a drain that actually failed. `no_command` is a standing
    # configuration gap across a 1300-card backlog; alarming on it every poll
    # would train the operator to ignore the exit code that reports a real break.
    return 1 if any(o["status"] == "failed" for o in outcomes) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
