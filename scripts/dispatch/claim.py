#!/usr/bin/env python3
"""claim.py — mutual exclusion for dispatched work. workspace-hub#3740 slice 2.

`records.py` (slice 1) makes the state of a dispatched item durable. It does not
make it *exclusive*: two hosts draining the same queue can each write a perfectly
valid record and each believe they hold the item.

**Git offers no compare-and-swap across machines.** It offers a push that may be
*rejected*, which is a retry signal, not a lock. So exclusion here is not a
property of any data structure — it is an ordering, and the ordering is the whole
design:

    1. write the claim record (create-only)
    2. commit + push
    3. push REJECTED  -> another host got there first. Pull, DO NOT EXECUTE.
    4. push accepted  -> re-read the record FROM THE REMOTE, confirm it is ours
    5. only then      -> the caller may execute

Steps 3 and 4 are the load-bearing ones, and step 4 is the one that is easy to
drop. An accepted push proves *our write landed*. It does not prove *our claim
survived*: a concurrent merge can accept the push while the remote's copy of the
record names somebody else. The remote is the only authority on who holds the
item, so the remote is what we read.

## Why this fails CLOSED (unlike deckhand#580)

Anything unknown — unreadable remote, git error, a record that does not name us —
returns `ok=False` with `record=None`, and the job does not run.

That is the opposite of the notification-channel call in deckhand#580, and
deliberately so. There, a wrong DENY turned a delivery outage into a submission
outage, so ambiguity had to resolve to ALLOW. Here the payoff matrix is
inverted: there is exactly **one floating Orcina `Flex` seat fleet-wide**
(wh#3721), so a wrong ALLOW means two hosts racing one licence — both attempts
fail, and they fail confusingly, in two places, with no single log that explains
why. A wrong DENY makes one card wait for the next drain. Cheap.

`record=None` on refusal is part of that. Returning the record we *tried* to
write would invite `if result.record:` at the call site, which reads as success
and would execute.

## Injected git surface

The git operations are injected (`git=`) so the protocol can be tested without a
network or a real repo — the ordering is the thing under test, and a test that
only checked outcomes would pass an implementation that executed first and pushed
afterwards. `GitBackend` below is the real subprocess implementation used when
nothing is injected.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import records

#: Kept small on purpose. Every git call in the protocol is on the critical path
#: of a decision that must fail closed, so a hang has to become a refusal rather
#: than a stalled dispatcher holding a claim nobody can see.
GIT_TIMEOUT_SECONDS = 120


@dataclass
class ClaimResult:
    """The answer to "may I execute?" — and nothing more.

    `ok` is the only field a caller should branch on. `record` is populated
    ONLY when `ok` is True, so that a truthiness check on `record` cannot
    accidentally become a second, wrong, way of asking the same question.
    """

    ok: bool
    reason: str
    record: dict | None = None
    warnings: list[str] = field(default_factory=list)


def _refuse(reason: str, warnings: list[str] | None = None) -> ClaimResult:
    return ClaimResult(ok=False, reason=reason, record=None,
                       warnings=list(warnings or []))


# ---------------------------------------------------------------------------
# the real git surface
# ---------------------------------------------------------------------------


class GitBackend:
    """Subprocess git, used when the caller injects nothing.

    Every method answers a yes/no the protocol needs, and answers **no** when it
    cannot tell. A backend that raised on a rejected push would make step 3
    indistinguishable from step "git is broken"; a backend that returned True on
    a timeout would hand the caller a claim it never verified.
    """

    def __init__(self, repo_root: Path, *, records_dir: Path | None = None,
                 remote: str = "origin", branch: str | None = None):
        self.repo_root = Path(repo_root)
        #: Where records live, so `read_remote` can turn an issue into the path
        #: git knows it by. Defaults to the repo root itself.
        self.records_dir = Path(records_dir) if records_dir else self.repo_root
        self.remote = remote
        self._branch = branch

    # -- plumbing ---------------------------------------------------------

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=str(self.repo_root), capture_output=True,
            text=True, timeout=GIT_TIMEOUT_SECONDS, check=False,
        )

    @property
    def branch(self) -> str:
        if self._branch is None:
            done = self._run("rev-parse", "--abbrev-ref", "HEAD")
            self._branch = (done.stdout or "").strip() or "main"
        return self._branch

    # -- protocol surface -------------------------------------------------

    def commit(self, path, message: str) -> bool:
        """Commit exactly one path.

        Pathspec-scoped (`git commit -- <path>`) because dispatch hosts run
        several claims concurrently in one checkout: a bare `git commit -a`
        would sweep another lane's in-progress edits into this claim's commit.
        """
        rel = str(Path(path))
        if self._run("add", "--", rel).returncode != 0:
            return False
        done = self._run("commit", "-m", message, "--", rel)
        if done.returncode == 0:
            return True
        # Re-writing an identical record is a no-op, not a failure: there is
        # nothing to push, but nothing went wrong either.
        return "nothing to commit" in (done.stdout or "") + (done.stderr or "")

    def push(self) -> bool:
        """False means REJECTED — which the protocol reads as "someone else won".

        Deliberately does not distinguish a rejection from a network failure.
        Both mean our claim is not on the remote, and both must stop execution;
        collapsing them keeps the caller from inventing a "probably fine" branch.
        """
        return self._run("push", self.remote, f"HEAD:{self.branch}").returncode == 0

    def pull(self) -> bool:
        return self._run("pull", "--rebase", self.remote, self.branch).returncode == 0

    def read_remote(self, issue: str) -> dict | None:
        """The remote's copy of the record, or None if it cannot be read.

        None is "cannot tell", and the caller turns that into a refusal. Reading
        the working tree instead would be worthless: that file is the one we just
        wrote, so it can only ever agree with us.
        """
        self._run("fetch", self.remote, self.branch)
        path = records.record_path(self.records_dir, issue)
        try:
            rel = path.resolve().relative_to(self.repo_root.resolve())
        except ValueError:
            return None
        done = self._run("show", f"{self.remote}/{self.branch}:{rel.as_posix()}")
        if done.returncode != 0:
            return None
        try:
            return json.loads(done.stdout)
        except (ValueError, TypeError):
            return None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _same_claim(ours: dict, theirs: dict) -> bool:
    """Identity of a claim is (host, job_id) — not issue, and not state.

    The issue is the same by construction (it is how we looked the record up),
    and state moves under us legitimately. Only the pair that names *this
    attempt on this host* can distinguish our claim from a concurrent one.
    """
    return (theirs.get("host") == ours.get("host")
            and theirs.get("job_id") == ours.get("job_id"))


def _check_generation(record: dict, current_generation: str | None,
                      warnings: list[str]) -> str | None:
    """Refuse a claim written from a stale queue file. Returns a reason, or None.

    A host that is draining last week's queue is not merely late — its view of
    what is ready is wrong, and without this check it competes on equal terms
    with a current host and can win the race. Then the older queue's idea of the
    work is the one that executes.

    A record with no generation id at all is allowed but WARNED: queue files
    predating generation ids still exist, and refusing them would take the
    dispatcher down for a back-compat reason. Unverifiable is not the same as
    wrong — but it must be visible, or the gap silently becomes permanent.
    """
    if current_generation is None:
        return None
    declared = record.get("queue_generation_id")
    if declared is None:
        warnings.append(
            f"claim declares no queue_generation_id; cannot verify it against "
            f"current generation {current_generation!r}"
        )
        return None
    if declared != current_generation:
        return (f"stale queue generation {declared!r} != current "
                f"{current_generation!r}")
    return None


# ---------------------------------------------------------------------------
# the protocol
# ---------------------------------------------------------------------------


def acquire(root, record: dict, *, git=None, current_generation: str | None = None
            ) -> ClaimResult:
    """Claim an issue, or refuse. `ok is True` is the ONLY licence to execute.

    Order: validate -> generation -> write -> commit -> push -> verify remote.

    The generation check runs *before* the write so a stale host never leaves a
    record behind at all; a refused claim that still wrote a file would be
    indistinguishable, to the next reader, from a live one.

    The verify runs *after* the push and reads the remote, for the reason this
    module exists: an accepted push proves our write landed, not that our claim
    is the one that survived.
    """
    warnings: list[str] = []
    git = git or GitBackend(Path(root))

    try:
        records.validate(record)
    except Exception as exc:                       # unknown shape -> do not run
        return _refuse(f"record rejected: {exc}")

    stale = _check_generation(record, current_generation, warnings)
    if stale:
        return _refuse(stale, warnings)

    issue = record["issue"]
    try:
        path = records.write_record(root, record)
    except records.ClaimConflict as exc:
        # Someone else's live claim is already on disk locally. That is a
        # decided race, not a retryable one.
        return _refuse(f"claim conflict: {exc}", warnings)
    except Exception as exc:
        return _refuse(f"could not write claim for {issue}: {exc}", warnings)

    try:
        if not git.commit(path, f"dispatch: claim {issue}"):
            return _refuse(f"could not commit claim for {issue}", warnings)

        if not git.push():
            # THE RACE, RESOLVED AGAINST US. Pull anyway: leaving the clone
            # behind guarantees the next drain reads the same stale queue and
            # races again, so a rejection that does not resync is a loop.
            try:
                git.pull()
            except Exception as exc:
                warnings.append(f"pull after rejected push failed: {exc}")
            return _refuse(
                f"push rejected for {issue} — another host claimed it first",
                warnings,
            )

        remote = git.read_remote(issue)
    except Exception as exc:
        # Any git failure at all. We do not know who holds the claim, and
        # "do not know" resolves to "do not execute".
        return _refuse(f"git error during claim of {issue}: {exc}", warnings)

    if not isinstance(remote, dict):
        return _refuse(
            f"could not read {issue} back from the remote — cannot-verify is "
            "not verified",
            warnings,
        )

    if not _same_claim(record, remote):
        return _refuse(
            f"claim on {issue} is not ours: remote holds "
            f"{remote.get('host')}/{remote.get('job_id')}",
            warnings,
        )

    # Return the REMOTE's copy, not the one we wrote. They agree on (host,
    # job_id) — that was just checked — but the remote is what every other host
    # sees, so it is the version the caller should carry into release().
    return ClaimResult(ok=True, reason="claim confirmed on the remote",
                       record=remote, warnings=warnings)


def release(root, record: dict, *, state: str, reason: str,
            returncode: int | None = None, git=None) -> ClaimResult:
    """Record the outcome and push it. Report failure; never swallow it.

    A completion that never reaches the remote is invisible to every other host:
    the item stays `active` forever, its TTL eventually expires, and it gets
    reclaimed and re-run. That is the original defect of this epic — work that
    finished with nothing recording it — reappearing one layer up, so a failed
    push here is returned as `ok=False`, not logged and dropped.

    Unlike `acquire`, this does NOT re-read the remote to verify. Release is not
    an exclusion decision: nothing is gated on it, so there is nothing for a
    verify to protect. The push either landed or it did not, and the caller is
    told which.
    """
    git = git or GitBackend(Path(root))

    try:
        out = records.transition(record, state, reason=reason, returncode=returncode)
        path = records.write_record(root, out)
    except Exception as exc:
        return _refuse(f"could not record outcome {state!r}: {exc}")

    issue = out.get("issue")
    try:
        if not git.commit(path, f"dispatch: {state} {issue} ({reason})"):
            return _refuse(f"could not commit outcome for {issue}")
        if not git.push():
            return _refuse(
                f"outcome {state!r} for {issue} is recorded locally but the push "
                "was rejected — the remote still shows this item as held"
            )
    except Exception as exc:
        return _refuse(f"git error while releasing {issue}: {exc}")

    return ClaimResult(ok=True, reason=f"outcome {state!r} pushed", record=out)
