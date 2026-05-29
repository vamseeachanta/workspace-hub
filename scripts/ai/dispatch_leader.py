#!/usr/bin/env python3
"""Cross-machine dispatch leadership — Phase 1 (#2847).

The provider-dispatch leader (default ace-linux-1) is the only machine that may
originate leases. There is NO cross-machine coordination primitive today: the
fcntl `leader.lock`, `leases.jsonl`, and the coexistence marker all live under
`logs/` (gitignored, local disk), so they coordinate same-host processes only.
The only shared substrate across machines is git.

Phase 1 delivers the safe core:

  - A git-tracked leader-state file (`.claude/dispatch/_leader-state.yaml`) holds
    {leader, term, heartbeat_utc, heartbeat_pid}. The leader refreshes the
    heartbeat each loop; secondaries read it via `git pull`.
  - The LOAD-BEARING SELF-FENCING PRIMITIVE (`may_write_leases`): the right to
    write a lease requires a *confirmed git push* of a fresh heartbeat — not
    merely holding the local flock. A leader that is alive but cannot push
    (auth/network/hook failure) therefore self-fences, which is what actually
    prevents the alive-but-cannot-push split-brain that a token-only race cannot
    (plan-stage review BLOCKER 2).
    NOTE: this primitive is provided and unit-proven here, but is NOT yet wired
    into `provider-dispatch-loop.py:append_lease` — that integration (gating both
    lease-write call sites on `may_write_leases`) is the Phase-1b task. Until then
    the loop's lease-origination is unchanged; this module ships the gate + the
    detect/alert watcher, not the enforcement at the lease sites.
  - Detection + ALERT only (`check`). No auto-promotion in Phase 1; a stale
    leader is surfaced, never silently failed over. Inconclusive state
    (unreadable store, term regression) is UNDETERMINED and never acted on.

Phase 2 (separate, behind a flag) adds atomic git push-race promotion with
post-push confirmation and flag-only/live-`gh` redistribution.

The LeaderStateStore is an interface so unit tests inject a fake; the real
GitLeaderStateStore is git-backed.
"""
from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

# Cadence / thresholds. Coherence invariant (asserted in tests):
#   HEARTBEAT_PERIOD_S < STALE_THRESHOLD_S < LEASE_TTL_S
# STALE must exceed one heartbeat (so a single missed beat is not "dead") with
# margin for push+pull+watcher-cron latency, and stay well under the lease TTL
# so failover reasons within a single lease window.
HEARTBEAT_PERIOD_S = 10 * 60      # 10 min
STALE_THRESHOLD_S = 30 * 60       # 30 min
LEASE_TTL_S = 3 * 3600            # mirrors provider-dispatch-loop DEFAULT_LEASE_TTL_S


class ClaimResult(Enum):
    PUSHED = "pushed"            # commit landed on origin — leadership/heartbeat confirmed
    REJECTED = "rejected"       # non-fast-forward: lost a concurrent race (Phase 2)
    PUSH_FAILED = "push_failed"  # network/auth/hook failure — could not prove reachability


class Status(Enum):
    LEADER = "leader"               # this machine is the current leader
    OK = "ok"                       # a different machine leads and its heartbeat is fresh
    STALE = "stale"                 # leader heartbeat is stale — Phase 1 ALERTS (no promote)
    UNDETERMINED = "undetermined"   # cannot read / corrupt / term regressed — never act


class StoreUnavailable(RuntimeError):
    """Raised by a store when it cannot obtain fresh state (e.g. `git pull`
    failed). Treated as UNDETERMINED — never a basis for promotion."""


@dataclass(frozen=True)
class LeaderState:
    leader: str
    term: int
    heartbeat_utc: str   # ISO-8601 UTC
    heartbeat_pid: int

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "LeaderState":
        return LeaderState(
            leader=str(d["leader"]),
            term=int(d["term"]),
            heartbeat_utc=str(d["heartbeat_utc"]),
            heartbeat_pid=int(d["heartbeat_pid"]),
        )


class LeaderStateStore:
    """Interface. Real implementation is GitLeaderStateStore; tests inject a fake."""

    def read(self) -> LeaderState:
        raise NotImplementedError

    def claim(self, state: LeaderState) -> ClaimResult:
        raise NotImplementedError


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _parse(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _age_seconds(state: LeaderState, now: datetime) -> float:
    return (now - _parse(state.heartbeat_utc)).total_seconds()


def may_write_leases(
    store: LeaderStateStore,
    me: str,
    my_term: int,
    *,
    now: datetime | None = None,
    alert=None,
) -> bool:
    """Self-fence gate — call IMMEDIATELY BEFORE every lease append.

    Returns True only when, right now, this machine is the committed leader AND a
    fresh heartbeat was *confirmed pushed*. Any of {not leader, superseded by a
    higher term, push rejected, push failed} -> False (stand down / demote).
    """
    try:
        st = store.read()
    except StoreUnavailable as e:
        if alert:
            alert(f"may_write_leases: store unavailable ({e}) — refusing lease write")
        return False
    if st.leader != me or st.term > my_term:
        if alert:
            alert(f"may_write_leases: superseded (leader={st.leader}, term={st.term} > {my_term}) — demote")
        return False
    # Heartbeat keeps the COMMITTED term (st.term) — a heartbeat must never bump
    # the fencing token; only promotion (Phase 2) increments it (review #4).
    fresh = dataclasses.replace(
        st, leader=me, term=st.term, heartbeat_utc=_now(now).isoformat(), heartbeat_pid=os.getpid()
    )
    result = store.claim(fresh)
    if result is not ClaimResult.PUSHED:
        if alert:
            alert(f"may_write_leases: heartbeat push {result.value} — cannot prove reachability, standing down")
        return False
    return True


def leader_can_originate(
    store: LeaderStateStore,
    machine: str,
    *,
    now: datetime | None = None,
    alert=None,
) -> bool:
    """Phase 1b gate — may `machine` originate a lease right now?

    True iff `machine` is the committed leader AND a fresh heartbeat is confirmed
    pushed (the self-fence). Reads once to learn the committed term, then
    `may_write_leases` performs the confirmed-push CAS. A non-leader, an
    unconfirmed push, or an unreadable store all return False (stand down)."""
    try:
        st = store.read()
    except StoreUnavailable as e:
        if alert:
            alert(f"leader_can_originate: store unavailable ({e}) — refusing to originate")
        return False
    if st.leader != machine:
        if alert:
            alert(f"leader_can_originate: {machine} is not the leader ({st.leader}) — refusing")
        return False
    return may_write_leases(store, machine, st.term, now=now, alert=alert)


def check(
    store: LeaderStateStore,
    me: str,
    *,
    now: datetime | None = None,
    last_known_term: int | None = None,
    alert=None,
) -> Status:
    """Detect leader health (Phase 1: alert only, never promote).

    UNDETERMINED for any inconclusive signal (unreadable store, term regression)
    so a secondary never acts on bad data.
    """
    try:
        st = store.read()
    except StoreUnavailable as e:
        if alert:
            alert(f"leader check: store unavailable ({e}) — UNDETERMINED, no action")
        return Status.UNDETERMINED

    if last_known_term is not None and st.term < last_known_term:
        if alert:
            alert(f"leader check: term regression {st.term} < last-known {last_known_term} — corruption, UNDETERMINED")
        return Status.UNDETERMINED

    if st.leader == me:
        return Status.LEADER

    age = _age_seconds(st, _now(now))
    if age <= STALE_THRESHOLD_S:
        return Status.OK

    if alert:
        alert(
            f"DEAD LEADER? {st.leader} heartbeat age {int(age)}s > {STALE_THRESHOLD_S}s "
            f"(term {st.term}). Phase 1: alert only — manual promotion required."
        )
    return Status.STALE


# ── Git-backed store (real implementation) ──────────────────────────────────
import subprocess  # noqa: E402  (kept below the pure logic for test-import clarity)
from pathlib import Path  # noqa: E402

DEFAULT_STATE_RELPATH = ".claude/dispatch/_leader-state.yaml"

# Live leadership state lives on a DEDICATED git ref, NOT on main. Heartbeats are
# written via plumbing (commit-tree) and pushed to this ref with --force-with-lease
# (an atomic compare-and-swap), so they never touch the main working tree and a
# lost race cannot leave a divergent commit that bricks reads (#2847 review BLOCKER 1).
DEFAULT_STATE_REF = "dispatch-leader-state"
STATE_FILE_IN_REF = "_leader-state.yaml"  # the single file in the dedicated ref's tree


def _yaml_dump(state: LeaderState) -> str:
    # Minimal, dependency-free flat YAML (the file is a flat scalar map).
    return (
        f"leader: {state.leader}\n"
        f"term: {state.term}\n"
        f"heartbeat_utc: {state.heartbeat_utc}\n"
        f"heartbeat_pid: {state.heartbeat_pid}\n"
    )


def _yaml_load_flat(text: str) -> dict:
    out: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


class GitLeaderStateStore(LeaderStateStore):
    """Git-backed leadership state on a DEDICATED ref (never main).

    The dedicated ref (`dispatch-leader-state`) holds a one-file tree
    (`_leader-state.yaml`). All operations use plumbing so the main working tree
    and the checked-out branch are never touched — a lost push race therefore
    leaves NO divergent local commit (the #2847 review BLOCKER 1 failure mode is
    impossible by construction).

    read():  `git fetch` the ref, then `git show origin/<ref>:_leader-state.yaml`.
             Fetch failure / missing ref / malformed content -> StoreUnavailable
             (UNDETERMINED upstream — never a stale-leader false positive). This
             is divergence-immune: it never depends on local main being ff-able.
    claim(): build the commit via hash-object + mktree + commit-tree (no index /
             no working-tree mutation), then push to the ref with
             --force-with-lease=<ref>:<parent> — an atomic compare-and-swap.
             rc=0 -> PUSHED (our exact content is now the ref tip: a *confirmed*
             fresh heartbeat, so the BLOCKER 2 no-op-misread is impossible);
             rejected/stale-lease -> REJECTED; other -> PUSH_FAILED.
    """

    def __init__(self, repo_root: str | Path, *, ref: str = DEFAULT_STATE_REF,
                 remote: str = "origin", fetch: bool = True):
        self.repo_root = Path(repo_root)
        self.ref = ref
        self.remote = remote
        self.fetch = fetch
        self._remote_tracking = f"refs/remotes/{remote}/{ref}"
        # SHA observed by the most recent read(); claim() compare-and-swaps against
        # it so a concurrent advance between read and claim is rejected (TOCTOU-safe).
        self._last_read_sha: str | None = None

    def _git(self, *args: str, _input: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo_root), *args],
            capture_output=True, text=True, input=_input,
        )

    def _fetch_ref(self) -> str | None:
        """Fetch the dedicated ref into the remote-tracking ref. Returns the
        origin SHA (parent for the next claim) or None if the ref does not exist
        yet (bootstrap). Raises StoreUnavailable on a real network/auth failure.

        Existence is probed STRUCTURALLY with `git ls-remote --exit-code` (rc 2 =
        ref absent, rc 0 = present, other = failure) rather than scraping git's
        localized error text — so a non-C locale or a future wording change cannot
        misclassify a missing ref as a hard failure (review #2)."""
        if self.fetch:
            ls = self._git("ls-remote", "--exit-code", self.remote, self.ref)
            if ls.returncode == 2:
                return None  # bootstrap: the ref does not exist on the remote yet
            if ls.returncode != 0:
                raise StoreUnavailable(f"git ls-remote failed: {ls.stderr.strip()[:200]}")
            f = self._git("fetch", "--quiet", self.remote,
                          f"+{self.ref}:{self._remote_tracking}")
            if f.returncode != 0:
                raise StoreUnavailable(f"git fetch failed: {f.stderr.strip()[:200]}")
        rev = self._git("rev-parse", "--verify", "--quiet", self._remote_tracking)
        sha = rev.stdout.strip()
        return sha or None

    def read(self) -> LeaderState:
        parent = self._fetch_ref()
        self._last_read_sha = parent
        if parent is None:
            raise StoreUnavailable(f"leader-state ref '{self.ref}' not initialized on {self.remote}")
        show = self._git("show", f"{parent}:{STATE_FILE_IN_REF}")
        if show.returncode != 0:
            raise StoreUnavailable(f"leader-state file missing in ref '{self.ref}'")
        try:
            return LeaderState.from_dict(_yaml_load_flat(show.stdout))
        except (KeyError, ValueError) as e:
            raise StoreUnavailable(f"leader-state malformed: {e}") from e

    def claim(self, state: LeaderState, *, expected_parent: str | None = "__USE_LAST_READ__") -> ClaimResult:
        # CAS base: the SHA the caller last read() (TOCTOU-safe), else fetch the
        # current tip (bootstrap / standalone). Pass expected_parent=None to force
        # a bootstrap (create) attempt, or an explicit SHA to CAS against it.
        if expected_parent == "__USE_LAST_READ__":
            if self._last_read_sha is not None:
                parent = self._last_read_sha
            else:
                try:
                    parent = self._fetch_ref()  # standalone/bootstrap claim
                except StoreUnavailable:
                    # Honor the ClaimResult contract — a network/auth failure here
                    # is a failed claim, not an exception leaking to the caller (review #1).
                    return ClaimResult.PUSH_FAILED
        else:
            parent = expected_parent
        content = _yaml_dump(state)
        # 1) blob (write-objects only — no index, no working tree)
        h = self._git("hash-object", "-w", "--stdin", _input=content)
        if h.returncode != 0:
            return ClaimResult.PUSH_FAILED
        blob = h.stdout.strip()
        # 2) one-entry tree
        mk = self._git("mktree", _input=f"100644 blob {blob}\t{STATE_FILE_IN_REF}\n")
        if mk.returncode != 0:
            return ClaimResult.PUSH_FAILED
        tree = mk.stdout.strip()
        # 3) commit object (always a fresh commit -> no "nothing to commit" path)
        msg = f"chore(dispatch): leader heartbeat — {state.leader} term {state.term}"
        commit_args = ["commit-tree", tree, "-m", msg]
        if parent:
            commit_args += ["-p", parent]
        c = self._git(*commit_args)
        if c.returncode != 0:
            return ClaimResult.PUSH_FAILED
        commit = c.stdout.strip()
        # 4) atomic CAS push to the dedicated ref
        if parent:
            push = self._git("push", self.remote, f"{commit}:refs/heads/{self.ref}",
                             f"--force-with-lease=refs/heads/{self.ref}:{parent}")
        else:
            # bootstrap: create the ref; plain push fails if it appeared concurrently
            push = self._git("push", self.remote, f"{commit}:refs/heads/{self.ref}")
        if push.returncode == 0:
            return ClaimResult.PUSHED
        blob_out = (push.stdout + push.stderr).lower()
        if any(s in blob_out for s in ("rejected", "non-fast-forward", "stale info",
                                       "fetch first", "already exists")):
            return ClaimResult.REJECTED
        return ClaimResult.PUSH_FAILED


def _stderr_alert(msg: str) -> None:
    import sys
    print(f"[dispatch-leader] {msg}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """CLI for the watcher cron. Phase 1: --check (detect+alert) and --heartbeat
    (leader refreshes its committed heartbeat, self-fenced on push)."""
    import argparse
    import socket
    import sys

    ap = argparse.ArgumentParser(description="Dispatch leader heartbeat/health (Phase 1, #2847)")
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--machine", default=os.environ.get("DISPATCHER_MACHINE") or socket.gethostname())
    ap.add_argument("--ref", default=DEFAULT_STATE_REF, help="dedicated leadership ref")
    ap.add_argument("--no-fetch", action="store_true", help="skip git fetch (testing only)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="detect leader health; alert if stale (exit 2)")
    g.add_argument("--heartbeat", action="store_true", help="leader: refresh committed heartbeat")
    g.add_argument("--show", action="store_true", help="print current leader-state")
    args = ap.parse_args(argv)

    store = GitLeaderStateStore(args.repo_root, ref=args.ref, fetch=not args.no_fetch)

    if args.show:
        try:
            print(store.read())
            return 0
        except StoreUnavailable as e:
            print(f"unavailable: {e}", file=sys.stderr)
            return 1

    if args.heartbeat:
        # my_term = current committed term (leader keeps its own term).
        try:
            term = store.read().term
        except StoreUnavailable as e:
            _stderr_alert(f"heartbeat: {e}")
            return 1
        ok = may_write_leases(store, args.machine, term, alert=_stderr_alert)
        return 0 if ok else 1

    # --check
    status = check(store, args.machine, alert=_stderr_alert)
    print(status.value)
    return 2 if status is Status.STALE else 0


if __name__ == "__main__":
    raise SystemExit(main())
