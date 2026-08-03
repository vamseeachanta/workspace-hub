#!/usr/bin/env python3
"""A refused claim must leave nothing behind, and must say what actually happened.

workspace-hub#3764. Reproduced live on the first real drain against
`vamseeachanta/deckhand#33`:

    claim-refused: push rejected ... — another host claimed it first

...and then, checking by content rather than by exit code, the claim commit that
refusal was supposed to abandon was on `origin/main`, published by this repo's
auto-sync process, holding the issue `active` for a 90-minute TTL with nothing
running. **Exclusion without execution.**

Two defects, tested separately here because they fail independently:

**D1 — the refusal left publishable state.** `acquire` writes the record, commits
it, pushes, and on a rejected push refuses. The *file* argument in its docstring
("a refused claim that still wrote a file would be indistinguishable, to the next
reader, from a live one") is right and stops one leak; the commit is the other,
and nothing undid it. Any process that pushes this branch — an auto-sync timer, a
parallel dispatch lane, a human `git push` — publishes the refused claim.

**D2 — the diagnosis named a culprit that did not exist.** No other host was
involved: the push lost a race to a sync process on the *same* host. "Another
host claimed it first" sends an operator hunting a claimant who is not there, and
it hides the fact that this rejection is *retryable* — nobody holds the item.

The undo is the dangerous half. This repo runs concurrent dispatch lanes and an
auto-sync process in ONE shared checkout, so an undo that reaches beyond the
claim commit destroys somebody else's work. The `GitBackend` tests below run
against a real temporary repository precisely because that is a property of the
git mechanics, not of the protocol, and a fake cannot falsify it.

Hermetic: the protocol tests inject git; the backend tests use a local
`git init` with no remote. No network either way.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/ -q
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAIM_PY = REPO_ROOT / "scripts" / "dispatch" / "claim.py"


def _load():
    pkg = str(CLAIM_PY.parent)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location("dispatch_claim_undo", CLAIM_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_claim_undo"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()

ISSUE = "vamseeachanta/deckhand#33"
OURS = "ace-linux-1"
OTHER = "ace-win-1"


def _ours(**kw):
    base = {"schema": 1, "issue": ISSUE, "state": "active",
            "host": OURS, "job_id": "j1", "attempt": 1}
    base.update(kw)
    return base


# --------------------------------------------------------------------------
# doubles
# --------------------------------------------------------------------------


class FakeGit:
    """Injected git surface whose push is rejected, as in the live incident.

    `undo` is what the backend reports back about the undo it was asked to do.
    A backend that says it dropped the commit is also expected to have taken the
    working-tree file with it — that is what the real one does, and a double that
    lies about it would let a leak through the protocol tests.
    """

    def __init__(self, *, push_ok=False, remote_record=None, undo=None):
        self.push_ok = push_ok
        self.remote_record = remote_record
        self.undo_result = C.UNDO_DROPPED if undo is None else undo
        self.calls: list[str] = []
        self.undone: list[tuple[Path, dict]] = []

    def commit(self, path, message):
        self.calls.append("commit")
        return True

    def push(self):
        self.calls.append("push")
        return self.push_ok

    def pull(self):
        self.calls.append("pull")
        return True

    def read_remote(self, issue):
        self.calls.append("read_remote")
        return self.remote_record

    def undo_commit(self, path, record):
        self.calls.append("undo_commit")
        self.undone.append((Path(path), dict(record)))
        if self.undo_result in (C.UNDO_DROPPED, C.UNDO_REVERTED):
            Path(path).unlink(missing_ok=True)
        return self.undo_result


class OldGit:
    """A backend from before this fix: no undo surface at all.

    Kept because `drain.py`'s test doubles are exactly this shape. A missing
    capability must be REPORTED, never quietly treated as "nothing to undo".
    """

    def __init__(self, *, remote_record=None):
        self.remote_record = remote_record
        self.calls: list[str] = []

    def commit(self, path, message):
        self.calls.append("commit")
        return True

    def push(self):
        self.calls.append("push")
        return False

    def pull(self):
        self.calls.append("pull")
        return True

    def read_remote(self, issue):
        self.calls.append("read_remote")
        return self.remote_record


# --------------------------------------------------------------------------
# D1 — a rejected push leaves nothing publishable
# --------------------------------------------------------------------------


def test_a_rejected_push_undoes_the_claim_commit(tmp_path):
    """The defect, stated positively: the commit must not survive the refusal."""
    git = FakeGit()
    got = C.acquire(tmp_path, _ours(), git=git)

    assert got.ok is False
    assert git.undone, "a rejected push must ask the git surface to undo the claim commit"
    assert got.undo == C.UNDO_DROPPED


def test_the_undo_names_the_claim_we_wrote(tmp_path):
    """It must undo OUR commit, identified by the record, not "the last commit".

    Concurrent lanes commit into the same checkout; "the tip" and "our claim" are
    not the same object, and only the record can tell them apart.
    """
    rec = _ours()
    git = FakeGit()
    C.acquire(tmp_path, rec, git=git)

    path, handed = git.undone[0]
    assert path.name.endswith(".json")
    assert (handed["host"], handed["job_id"]) == (rec["host"], rec["job_id"])


def test_the_undo_happens_before_the_pull(tmp_path):
    """Order matters: `pull --rebase` replays a commit that is still there.

    Pulling first re-parents the orphaned claim onto the new remote tip, leaving
    it just as publishable as before and adding a conflict to resolve.
    """
    git = FakeGit()
    C.acquire(tmp_path, _ours(), git=git)

    assert git.calls.index("undo_commit") < git.calls.index("pull")


def test_no_rejection_path_leaves_a_local_claim_record(tmp_path):
    """Whatever the remote says, the refused claim must not remain on disk.

    A record left behind reads as live to the next drain, and blocks the retry
    that a lost push race is supposed to get.
    """
    for remote in (None, _ours(), _ours(host=OTHER, job_id="theirs")):
        git = FakeGit(remote_record=remote)
        C.acquire(tmp_path, _ours(), git=git)
        assert not any(tmp_path.glob("*.json")), \
            f"a refused claim left a record behind (remote={remote})"

    # ...and especially when the commit could NOT be taken back: a record left
    # next to a surviving commit is the stranded claim, twice over.
    for git in (FakeGit(undo=C.UNDO_FAILED), OldGit()):
        C.acquire(tmp_path, _ours(), git=git)
        assert not any(tmp_path.glob("*.json")), \
            f"an un-undone claim left a record behind ({type(git).__name__})"


@pytest.mark.parametrize("make_git, expected", [
    (lambda: OldGit(remote_record=_ours()), C.UNDO_UNAVAILABLE),
    (lambda: FakeGit(undo=C.UNDO_FAILED, remote_record=_ours()), C.UNDO_FAILED),
])
def test_a_claim_commit_that_survived_is_reported_not_assumed_gone(tmp_path, make_git,
                                                                   expected):
    """Absence of an undo must not read as a successful one.

    This is the failure mode the whole epic keeps meeting — no signal taken for
    a good signal — so a commit that outlived its refusal has to surface.

    The control run is the point of the test. Asserting only "there is a
    warning" passes on ANY warning from anywhere in the refusal path, which is a
    test of the weather; pinning the same scenario with a working undo to zero
    warnings makes the surviving commit the only thing that can produce one.
    """
    control = C.acquire(tmp_path, _ours(), git=FakeGit(remote_record=_ours()))
    assert control.undo == C.UNDO_DROPPED
    assert control.warnings == [], "control: an undone claim warns about nothing"

    got = C.acquire(tmp_path, _ours(), git=make_git())

    assert got.ok is False
    assert got.undo == expected
    assert got.warnings, "a claim commit that survived its refusal must be visible"


# --------------------------------------------------------------------------
# D2 — the rejection is diagnosed, not guessed
# --------------------------------------------------------------------------


def test_a_remote_held_by_another_host_is_a_genuine_refusal(tmp_path):
    """The only case that justifies "someone else has it": evidence they do."""
    git = FakeGit(remote_record=_ours(host=OTHER, job_id="theirs"))
    got = C.acquire(tmp_path, _ours(), git=git)

    assert got.ok is False
    assert got.cause == C.CAUSE_HELD_ELSEWHERE
    assert got.retryable is False, "another host holds it; retrying just races again"


def test_an_absent_remote_record_is_a_lost_push_race(tmp_path):
    """Nobody holds the item. The push simply lost to a concurrent pusher."""
    git = FakeGit(remote_record=None)
    got = C.acquire(tmp_path, _ours(), git=git)

    assert got.cause == C.CAUSE_LOST_PUSH_RACE
    assert got.retryable is True


def test_a_remote_record_that_is_OURS_is_a_lost_push_race(tmp_path):
    """The live incident, exactly.

    `deckhand#33` was rejected with "another host claimed it first" while no
    other host existed. Our own host's record on the remote is evidence of a
    lost push race, never of a rival claimant.
    """
    git = FakeGit(remote_record=_ours())
    got = C.acquire(tmp_path, _ours(), git=git)

    assert got.cause == C.CAUSE_LOST_PUSH_RACE
    assert got.retryable is True


def test_a_finished_record_from_another_host_is_not_a_held_claim(tmp_path):
    """`held` means live. A terminal record is history, not an owner.

    Reading a `done` record as a live claim would make the item look owned by a
    host that walked away from it.
    """
    git = FakeGit(remote_record=_ours(host=OTHER, job_id="theirs", state="done"))
    got = C.acquire(tmp_path, _ours(), git=git)

    assert got.cause == C.CAUSE_LOST_PUSH_RACE
    assert got.retryable is True


# --------------------------------------------------------------------------
# fail closed — the guarantee neither fix may weaken
# --------------------------------------------------------------------------


def test_retryable_is_never_a_licence_to_execute(tmp_path):
    """`ok` remains the only licence. A retryable refusal is still a refusal.

    Getting this wrong permissively is far worse than a spurious refusal: two
    hosts against one floating licence seat (wh#3721).
    """
    for remote in (None, _ours(), _ours(host=OTHER, job_id="theirs"),
                   _ours(host=OTHER, job_id="theirs", state="done")):
        got = C.acquire(tmp_path, _ours(), git=FakeGit(remote_record=remote))
        assert got.ok is False
        assert got.record is None


def test_an_undo_failure_never_turns_a_refusal_into_a_pass(tmp_path):
    for status in (C.UNDO_FAILED, C.UNDO_UNAVAILABLE, C.UNDO_DROPPED, C.UNDO_REVERTED):
        git = FakeGit(undo=status, remote_record=_ours())
        got = C.acquire(tmp_path, _ours(), git=git)
        assert got.ok is False and got.record is None


def test_a_successful_claim_is_not_undone_and_is_not_retryable(tmp_path):
    rec = _ours()
    git = FakeGit(push_ok=True, remote_record=rec)
    got = C.acquire(tmp_path, rec, git=git)

    assert got.ok is True
    assert git.undone == [], "an accepted push must not undo anything"
    assert got.retryable is False
    assert got.undo is None


# --------------------------------------------------------------------------
# GitBackend — the undo mechanics, against a real repository
# --------------------------------------------------------------------------


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, check=False)


def _init(tmp_path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "dispatch@test.invalid")
    _git(repo, "config", "user.name", "dispatch test")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-m", "seed")
    return repo


def _subjects(repo) -> list[str]:
    return _git(repo, "log", "--format=%s", "--all").stdout.split("\n")


def _backend(repo, records_dir):
    return C.GitBackend(repo, records_dir=records_dir, branch="main")


def _commit_a_claim(repo, records_dir, record):
    """Write + commit a claim exactly the way `acquire` does."""
    path = C.records.write_record(records_dir, record)
    backend = _backend(repo, records_dir)
    assert backend.commit(path, f"dispatch: claim {record['issue']}") is True
    return backend, path


def test_backend_undo_leaves_no_claim_commit_reachable(tmp_path):
    """Unreachable is the requirement — a reachable commit is a publishable one."""
    repo = _init(tmp_path)
    records_dir = repo / "records"
    before = _git(repo, "rev-parse", "HEAD").stdout.strip()

    backend, path = _commit_a_claim(repo, records_dir, _ours())
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() != before

    assert backend.undo_commit(path, _ours()) == C.UNDO_DROPPED

    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == before
    assert not any(s.startswith("dispatch: claim") for s in _subjects(repo))
    assert not path.exists(), "the record must go with the commit"


def test_backend_undo_does_not_destroy_a_concurrent_lane_s_work(tmp_path):
    """The reason this is not `git reset --hard`.

    Other dispatch lanes and an auto-sync process share this checkout. An undo
    that reaches past its own commit is a data-loss bug that would present as
    "my edits vanished", with nothing pointing back here.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"

    tracked = repo / "seed.txt"
    tracked.write_text("another lane was editing this\n", encoding="utf-8")
    untracked = repo / "scratch.txt"
    untracked.write_text("untracked work in progress\n", encoding="utf-8")
    staged = repo / "staged.txt"
    staged.write_text("staged by another lane\n", encoding="utf-8")
    _git(repo, "add", "staged.txt")

    backend, path = _commit_a_claim(repo, records_dir, _ours())
    assert backend.undo_commit(path, _ours()) == C.UNDO_DROPPED

    assert tracked.read_text(encoding="utf-8") == "another lane was editing this\n"
    assert untracked.read_text(encoding="utf-8") == "untracked work in progress\n"
    assert staged.read_text(encoding="utf-8") == "staged by another lane\n"
    assert "staged.txt" in _git(repo, "diff", "--cached", "--name-only").stdout, \
        "another lane's staged work must still be staged"


def test_backend_undo_never_drops_a_commit_that_landed_on_top(tmp_path):
    """History that is not ours is never rewritten — not even to fix our mess.

    When another lane commits between our commit and our undo, moving the branch
    ref back would silently delete their commit. The claim still has to go, so it
    goes forward instead: a commit that removes it.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"

    backend, path = _commit_a_claim(repo, records_dir, _ours())
    (repo / "other-lane.txt").write_text("landed after our claim\n", encoding="utf-8")
    _git(repo, "add", "other-lane.txt")
    _git(repo, "commit", "-m", "another lane: unrelated work")
    theirs = _git(repo, "rev-parse", "HEAD").stdout.strip()

    assert backend.undo_commit(path, _ours()) == C.UNDO_REVERTED

    assert _git(repo, "merge-base", "--is-ancestor", theirs, "HEAD").returncode == 0, \
        "the other lane's commit must still be reachable"
    rel = path.relative_to(repo).as_posix()
    assert _git(repo, "cat-file", "-e", f"HEAD:{rel}").returncode != 0, \
        "the refused claim must not be in the published tree"
    assert not path.exists()


def test_backend_undo_never_drops_a_commit_carrying_other_work(tmp_path):
    """Auto-sync commits with `git add -A`, so our record arrives with company.

    Dropping such a commit to clean up a refused claim would delete whatever
    else it swept in. The claim still has to go, so it goes forward.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"
    backend = _backend(repo, records_dir)

    path = C.records.write_record(records_dir, _ours())
    hitchhiker = repo / "swept-in.txt"
    hitchhiker.write_text("somebody else's work\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "auto-sync: publish")

    assert backend.undo_commit(path, _ours()) == C.UNDO_REVERTED

    assert _git(repo, "cat-file", "-e", "HEAD:swept-in.txt").returncode == 0, \
        "work swept into the same commit must survive the undo"
    rel = path.relative_to(repo).as_posix()
    assert _git(repo, "cat-file", "-e", f"HEAD:{rel}").returncode != 0


def test_backend_ref_move_is_a_compare_and_swap(tmp_path):
    """The guard against the window between reading HEAD and moving it.

    A concurrent lane can commit in that window. Tested directly because the
    window cannot be driven deterministically through `undo_commit`, and an
    unconditional ref move would pass every other test in this file while
    silently discarding whatever landed in it.
    """
    repo = _init(tmp_path)
    backend = _backend(repo, repo / "records")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    stale = "0" * 40

    assert backend._cas_ref(f"{head}", stale) is False
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == head


def test_backend_undo_refuses_a_commit_that_is_not_ours(tmp_path):
    """Identity is (host, job_id) from the record, not the commit message.

    Two hosts write the same commit subject for the same issue. Undoing on the
    message alone would let this host drop another host's claim.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"
    backend, path = _commit_a_claim(repo, records_dir, _ours(host=OTHER, job_id="theirs"))
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()

    assert backend.undo_commit(path, _ours()) == C.UNDO_FAILED
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == head, \
        "somebody else's claim commit must survive untouched"


def _seed_a_finished_record(repo, records_dir):
    """A completed run's record, committed, as a prior claim would leave it."""
    path = C.records.write_record(records_dir, _ours(state="done", job_id="j0",
                                                     returncode=0))
    _git(repo, "add", "--", path.relative_to(repo).as_posix())
    _git(repo, "commit", "-m", "dispatch: done")
    return path, path.read_bytes()


@pytest.mark.parametrize("crowd_the_tip, expected", [
    (False, C.UNDO_DROPPED),
    (True, C.UNDO_REVERTED),
])
def test_backend_undo_restores_a_record_the_claim_overwrote(tmp_path, crowd_the_tip,
                                                            expected):
    """A claim may legitimately overwrite a TERMINAL record. Undo puts it back.

    Deleting it instead would destroy the completed run's audit trail — the
    exact thing the records epic exists to stop losing. Both undo routes owe the
    same answer: dropping the commit and removing it forward differ in how they
    reach the prior state, not in what that state is.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"
    path, finished = _seed_a_finished_record(repo, records_dir)

    backend, path = _commit_a_claim(repo, records_dir, _ours(job_id="j1"))
    if crowd_the_tip:
        (repo / "other-lane.txt").write_text("x\n", encoding="utf-8")
        _git(repo, "add", "other-lane.txt")
        _git(repo, "commit", "-m", "another lane")

    assert backend.undo_commit(path, _ours(job_id="j1")) == expected
    assert path.read_bytes() == finished, "the completed run's record must come back"
    assert json.loads(path.read_text(encoding="utf-8"))["job_id"] == "j0"


def test_acquire_end_to_end_against_a_real_repo_publishes_nothing(tmp_path):
    """The live incident, end to end, with the real git surface.

    `push` is rejected; afterwards the branch must look exactly as it did before
    the drain, and nothing may be left for auto-sync to publish.
    """
    repo = _init(tmp_path)
    records_dir = repo / "records"
    before = _git(repo, "rev-parse", "HEAD").stdout.strip()

    class RejectedPush(C.GitBackend):
        def push(self):
            return False

        def pull(self):
            return True

        def read_remote(self, issue):
            return None

    got = C.acquire(records_dir, _ours(),
                    git=RejectedPush(repo, records_dir=records_dir, branch="main"))

    assert got.ok is False and got.record is None
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == before
    assert not any(s.startswith("dispatch: claim") for s in _subjects(repo))
    assert _git(repo, "status", "--porcelain").stdout.strip() == "", \
        "a refused claim must leave the working tree as it found it"
    assert got.retryable is True
