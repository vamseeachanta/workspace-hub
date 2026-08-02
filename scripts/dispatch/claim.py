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
    3. push REJECTED  -> UNDO THE COMMIT, pull, diagnose, DO NOT EXECUTE.
    4. push accepted  -> re-read the record FROM THE REMOTE, confirm it is ours
    5. only then      -> the caller may execute

Steps 3 and 4 are the load-bearing ones, and step 4 is the one that is easy to
drop. An accepted push proves *our write landed*. It does not prove *our claim
survived*: a concurrent merge can accept the push while the remote's copy of the
record names somebody else. The remote is the only authority on who holds the
item, so the remote is what we read.

## Why step 3 undoes the commit (wh#3764)

A refusal is only a refusal if it leaves nothing behind. The first real drain
refused `vamseeachanta/deckhand#33` on a rejected push — and this repo's
auto-sync process, which periodically commits and pushes `main`, found the
orphaned claim commit and published it. The remote then held the issue `active`
for its full 90-minute TTL with nothing running: **exclusion without execution**,
the worst outcome this protocol can produce.

The undo is scoped hard, because dispatch lanes and auto-sync share ONE checkout
on a dispatch host:

  * the commit is identified by the RECORD it carries — `(host, job_id)` — not by
    the branch tip and not by its message, which another host writes identically;
  * the branch ref moves back by a compare-and-swap (`git update-ref <ref> <new>
    <old>`), which touches neither the index nor the working tree, so no other
    lane's staged or unstaged work is at risk. `reset --hard` would destroy it;
  * if the CAS is lost, or another commit landed on top, history is NEVER
    rewritten. The claim is removed *forward*, by a path-scoped commit.

## Why "another host claimed it first" was the wrong thing to say

That message was emitted on `deckhand#33` when no other host was involved: the
push lost a race to a sync process on the same host. It sent an operator hunting
a claimant that did not exist, and it hid the fact that nobody held the item, so
the drain could simply have tried again. A rejection is therefore diagnosed from
the remote rather than assumed (`CAUSE_HELD_ELSEWHERE` vs `CAUSE_LOST_PUSH_RACE`,
the latter `retryable=True`).

**`retryable` is not a licence.** Every rejection, whatever its cause, is still
`ok=False` with `record=None`.

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

#: How far back to look for our own claim commit when undoing it. It is
#: normally the tip; the window exists only because concurrent lanes and
#: auto-sync can commit on top between our commit and our undo.
UNDO_SEARCH_DEPTH = 20

# -- why a claim was refused. Machine-readable, because operators acted on the
#    prose and went looking for a host that did not exist (wh#3764).
CAUSE_RECORD_REJECTED = "record-rejected"
CAUSE_STALE_GENERATION = "stale-generation"
CAUSE_LOCAL_CONFLICT = "local-claim-conflict"
CAUSE_WRITE_FAILED = "write-failed"
CAUSE_COMMIT_FAILED = "commit-failed"
CAUSE_GIT_ERROR = "git-error"
CAUSE_UNVERIFIABLE = "remote-unverifiable"
CAUSE_NOT_OURS = "remote-claim-not-ours"
#: Evidence that a DIFFERENT host holds a live claim. The only cause that
#: justifies telling an operator somebody else has the item.
CAUSE_HELD_ELSEWHERE = "held-by-another-host"
#: Our push lost a race to another pusher — commonly this host's own auto-sync.
#: Nobody holds the item, so the drain may try again.
CAUSE_LOST_PUSH_RACE = "lost-push-race"

# -- what became of the claim commit after a refusal.
UNDO_DROPPED = "dropped"          # branch ref moved back; commit unreachable
UNDO_REVERTED = "reverted"        # removed forward, because history was not ours
UNDO_FAILED = "failed"            # could not be undone — a commit may remain
UNDO_UNAVAILABLE = "unavailable"  # the injected backend has no undo surface


@dataclass
class ClaimResult:
    """The answer to "may I execute?" — and nothing more.

    `ok` is the only field a caller should branch on. `record` is populated
    ONLY when `ok` is True, so that a truthiness check on `record` cannot
    accidentally become a second, wrong, way of asking the same question.

    `cause`, `retryable` and `undo` are REPORTING, not permission. `retryable`
    in particular says only that nobody is known to hold the item — a caller
    that reads it as "go ahead" has reinvented the split-brain this module
    exists to prevent.
    """

    ok: bool
    reason: str
    record: dict | None = None
    warnings: list[str] = field(default_factory=list)
    #: One of the CAUSE_* constants, or None on success.
    cause: str | None = None
    #: True only when the refusal was a lost race that named no holder.
    retryable: bool = False
    #: One of the UNDO_* constants when a claim commit had to be undone.
    undo: str | None = None


def _refuse(reason: str, warnings: list[str] | None = None, *,
            cause: str | None = None, retryable: bool = False,
            undo: str | None = None) -> ClaimResult:
    return ClaimResult(ok=False, reason=reason, record=None,
                       warnings=list(warnings or []), cause=cause,
                       retryable=retryable, undo=undo)


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

    # -- undoing a claim that was refused ---------------------------------

    def undo_commit(self, path, record) -> str:
        """Remove the claim commit for `record` so nothing can publish it.

        Returns an `UNDO_*` constant. Never raises for an ordinary git refusal —
        the caller is already refusing the claim and needs to know what state it
        is refusing *from*, not to lose that in an exception.

        Safety under concurrent writers, which is the whole difficulty:

        * **The commit is identified by its content**, not by position or
          message. Two hosts write the byte-identical subject
          `dispatch: claim owner/repo#N`, so a message match would let this host
          drop another host's claim. We match the `(host, job_id)` inside the
          committed record.
        * **A commit is only DROPPED if it is the tip and carries nothing but
          this record.** Auto-sync commits with `git add -A`, so our record can
          arrive inside a commit full of somebody else's work; dropping that
          commit would delete their work to clean up our claim.
        * **The drop is a compare-and-swap on the ref**
          (`git update-ref <ref> <parent> <commit>`), which fails rather than
          clobbers if anyone moved the branch since we looked. It rewrites no
          blobs and touches neither the index nor the working tree, so another
          lane's staged and unstaged edits survive untouched. `git reset --hard`
          would take them; `reset --mixed` would silently unstage them.
        * **Otherwise history is not rewritten at all** — the claim is removed
          going forward, by a commit scoped to the record path.
        """
        rel = self._rel(path)
        if rel is None:
            return UNDO_FAILED

        sha = self._find_claim_commit(rel, record)
        if sha is None:
            # Either it was never committed, or the commit that carries it is
            # not ours. Both resolve to "say so" — a silent success here is how
            # the orphan got published in the first place.
            return UNDO_FAILED

        if sha == self._rev_parse("HEAD") and self._touches_only(sha, rel):
            parent = self._rev_parse(f"{sha}^")
            if parent and self._cas_ref(parent, sha):
                self._restore_path(rel)
                return UNDO_DROPPED
            # CAS lost, or a root commit with no parent to fall back to. Both
            # fall through to the non-rewriting path.

        return self._remove_forward(sha, rel)

    def _cas_ref(self, new: str, expected: str) -> bool:
        """Move the current branch to `new`, but only if it is still `expected`.

        The compare-and-swap is the whole safety of the drop. Between reading
        HEAD and moving it, a concurrent lane or auto-sync can commit; without
        the expected-value argument `update-ref` would happily discard whatever
        arrived in that window. With it, the update is refused and the caller
        falls back to removing the claim forward.
        """
        return self._run("update-ref", "HEAD", new, expected).returncode == 0

    def _touches_only(self, sha: str, rel: str) -> bool:
        names = self._run("diff-tree", "--no-commit-id", "--name-only", "-r", sha)
        if names.returncode != 0:
            return False
        return [n for n in (names.stdout or "").split("\n") if n.strip()] == [rel]

    def _rel(self, path) -> str | None:
        try:
            return Path(path).resolve().relative_to(self.repo_root.resolve()).as_posix()
        except ValueError:
            return None

    def _rev_parse(self, rev: str) -> str | None:
        done = self._run("rev-parse", "--verify", "--quiet", rev)
        out = (done.stdout or "").strip()
        return out if done.returncode == 0 and out else None

    def _find_claim_commit(self, rel: str, record: dict) -> str | None:
        """The most recent commit that carries OUR version of this record."""
        listing = self._run("rev-list", f"-n{UNDO_SEARCH_DEPTH}", "HEAD", "--", rel)
        if listing.returncode != 0:
            return None
        for sha in (listing.stdout or "").split():
            blob = self._run("show", f"{sha}:{rel}")
            if blob.returncode != 0:
                continue
            try:
                got = json.loads(blob.stdout)
            except (ValueError, TypeError):
                continue
            if isinstance(got, dict) and _same_claim(record, got):
                return sha
        return None

    def _restore_path(self, rel: str) -> None:
        """Put one path back the way HEAD has it. Only that path.

        `git reset -- <path>` rewrites a single index entry and leaves the
        working tree alone; `git checkout -- <path>` then refreshes the file.
        When the path is not in HEAD at all — the ordinary case, a claim on an
        issue with no prior record — checkout has nothing to give it, so the
        file we wrote is simply removed.
        """
        self._run("reset", "-q", "--", rel)
        if self._run("checkout", "-q", "--", rel).returncode != 0:
            try:
                (self.repo_root / rel).unlink()
            except OSError:
                pass

    def _remove_forward(self, sha: str, rel: str) -> str:
        """Undo by adding a commit, never by rewriting one that is not ours.

        Restores the record to whatever the claim commit's parent had — which is
        the previous, possibly TERMINAL, record for that issue, not necessarily
        nothing. Deleting it outright would throw away a completed run's audit
        trail to clean up a refused claim.
        """
        if self._run("checkout", f"{sha}^", "--", rel).returncode != 0:
            if self._run("rm", "-q", "-f", "--ignore-unmatch", "--", rel).returncode != 0:
                return UNDO_FAILED
        done = self._run("commit", "-m", f"dispatch: undo refused claim {rel}", "--", rel)
        if done.returncode != 0 and "nothing to commit" not in (
                (done.stdout or "") + (done.stderr or "")):
            return UNDO_FAILED
        return UNDO_REVERTED

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


def _is_live(record: dict) -> bool:
    """A record only *holds* an issue while it is non-terminal.

    A `done` or `blocked` record names the host that last ran the item, not one
    that owns it now. Reading it as ownership would report an item as held by
    somebody who already walked away.
    """
    return record.get("state") not in records.TERMINAL


def _undo_claim_commit(git, path, record: dict, warnings: list[str]) -> str:
    """Take the claim commit back, and say plainly if it could not be taken.

    Runs BEFORE the resync pull: `pull --rebase` replays a commit that is still
    there, re-parenting the orphan onto the new remote tip — just as publishable
    as before, plus a conflict to resolve.

    An undo that did not happen is reported, never assumed. Absence of a signal
    read as a good signal is the failure mode this whole epic keeps meeting.
    """
    undo = getattr(git, "undo_commit", None)
    if undo is None:
        status = UNDO_UNAVAILABLE
    else:
        try:
            got = undo(path, record)
        except Exception as exc:                       # noqa: BLE001
            warnings.append(f"undoing the claim commit raised {type(exc).__name__}: {exc}")
            got = UNDO_FAILED
        status = got if isinstance(got, str) else (UNDO_DROPPED if got else UNDO_FAILED)

    if status not in (UNDO_DROPPED, UNDO_REVERTED):
        warnings.append(
            f"the claim commit for {record.get('issue')} was NOT undone "
            f"({status}) — anything that pushes this branch, including auto-sync, "
            "will publish a claim that was refused"
        )
        # The commit may survive; the record must not. Left on disk it reads as
        # live to the next drain and blocks the retry a lost race should get.
        try:
            Path(path).unlink()
        except OSError:
            pass
    return status


def _diagnose_rejection(ours: dict, remote, warnings: list[str]) -> tuple[str, bool, str]:
    """Why the push was rejected: `(cause, retryable, sentence)`.

    Only a live record naming a DIFFERENT host is evidence that somebody else
    holds the item. Anything else — no record, our own record, a finished record
    — means our push simply lost a race, most often to this host's own auto-sync
    process, and the item is still free.

    `read_remote` returns None both for "no such record" and for "could not
    read", which this cannot separate. Both are reported as a lost race: neither
    is evidence of a holder, and neither licenses execution, so the worst it can
    cost is one more refused attempt.
    """
    if isinstance(remote, dict) and _is_live(remote) and not _same_claim(ours, remote):
        held = f"{remote.get('host')}/{remote.get('job_id')}"
        return (CAUSE_HELD_ELSEWHERE, False,
                f"the remote holds a live claim by {held}")
    if remote is None:
        warnings.append("the remote holds no readable record for this issue")
        detail = "the remote holds no claim (or could not be read)"
    else:
        detail = "the remote's record is this host's own"
    return (CAUSE_LOST_PUSH_RACE, True,
            f"{detail} — the push lost a race to a concurrent pusher, "
            f"not to another host")


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

    Once the commit exists, every exit that is not a verified claim undoes it.
    The original argument covered the *file* — "a refused claim that still wrote
    a file would be indistinguishable, to the next reader, from a live one" — and
    stopped there; the commit leaked, and auto-sync published it (wh#3764). A
    refusal that leaves publishable state is not a refusal.
    """
    warnings: list[str] = []
    git = git or GitBackend(Path(root))

    try:
        records.validate(record)
    except Exception as exc:                       # unknown shape -> do not run
        return _refuse(f"record rejected: {exc}", cause=CAUSE_RECORD_REJECTED)

    stale = _check_generation(record, current_generation, warnings)
    if stale:
        return _refuse(stale, warnings, cause=CAUSE_STALE_GENERATION)

    issue = record["issue"]
    try:
        path = records.write_record(root, record)
    except records.ClaimConflict as exc:
        # Someone else's live claim is already on disk locally. That is a
        # decided race, not a retryable one.
        return _refuse(f"claim conflict: {exc}", warnings, cause=CAUSE_LOCAL_CONFLICT)
    except Exception as exc:
        return _refuse(f"could not write claim for {issue}: {exc}", warnings,
                       cause=CAUSE_WRITE_FAILED)

    try:
        committed = git.commit(path, f"dispatch: claim {issue}")
    except Exception as exc:
        return _refuse(f"git error during claim of {issue}: {exc}", warnings,
                       cause=CAUSE_GIT_ERROR)
    if not committed:
        return _refuse(f"could not commit claim for {issue}", warnings,
                       cause=CAUSE_COMMIT_FAILED)

    # From here a commit exists locally, and EVERY exit that is not a verified
    # claim has to take it back — otherwise the next process to push this
    # branch publishes a claim nobody is executing (wh#3764).
    try:
        pushed = git.push()
    except Exception as exc:
        undo = _undo_claim_commit(git, path, record, warnings)
        return _refuse(f"git error during claim of {issue}: {exc}", warnings,
                       cause=CAUSE_GIT_ERROR, undo=undo)

    if not pushed:
        # THE PUSH DID NOT LAND. Undo first — `pull --rebase` would replay the
        # claim commit and leave it just as publishable.
        undo = _undo_claim_commit(git, path, record, warnings)
        # Pull anyway: leaving the clone behind guarantees the next drain reads
        # the same stale queue and races again, so a rejection that does not
        # resync is a loop.
        try:
            git.pull()
        except Exception as exc:
            warnings.append(f"pull after rejected push failed: {exc}")
        try:
            remote = git.read_remote(issue)
        except Exception as exc:
            warnings.append(f"could not read {issue} from the remote: {exc}")
            remote = None
        cause, retryable, detail = _diagnose_rejection(record, remote, warnings)
        return _refuse(f"push rejected for {issue} — {detail}", warnings,
                       cause=cause, retryable=retryable, undo=undo)

    try:
        remote = git.read_remote(issue)
    except Exception as exc:
        # Any git failure at all. We do not know who holds the claim, and
        # "do not know" resolves to "do not execute".
        return _refuse(f"git error during claim of {issue}: {exc}", warnings,
                       cause=CAUSE_GIT_ERROR)

    if not isinstance(remote, dict):
        return _refuse(
            f"could not read {issue} back from the remote — cannot-verify is "
            "not verified",
            warnings, cause=CAUSE_UNVERIFIABLE,
        )

    if not _same_claim(record, remote):
        return _refuse(
            f"claim on {issue} is not ours: remote holds "
            f"{remote.get('host')}/{remote.get('job_id')}",
            warnings, cause=CAUSE_NOT_OURS,
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
