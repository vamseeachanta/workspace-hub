#!/usr/bin/env python3
"""The pilot drain — one issue through claim -> execute -> release -> project.

workspace-hub#3740 slice 6.

## What these tests exist to prevent

Three failures, each of which would look like success:

1. **Executing without the claim.** `claim.acquire` returning `ok=False` and the
   payload running anyway. There is one floating solver seat fleet-wide
   (wh#3721), so two hosts running the same work is not duplicated effort — it is
   two failed licence checkouts and two confusing logs. Every refusal test here
   asserts the RUNNER WAS NOT REACHED, not merely that the result says no.
2. **Inventing a completion.** A nonzero exit, an unreadable status verb, or a
   runner that raised, recorded as `done`/`returncode 0`. `done` means ran to
   completion; `records.is_success` additionally requires `returncode == 0`, and
   nothing here may blur them.
3. **A dry run that writes.** Default-safe is only a claim until something proves
   the default path reaches no write primitive. The doubles below RAISE on every
   method, so a dry run that touched git or the runner fails loudly rather than
   being caught by a later assertion that might not exist.

Ordering is asserted, not just outcomes: `FakeGit` and `FakeRunner` share ONE
call list (the same trick `test_claim_protocol.py` uses for the protocol), so a
drain that executed first and claimed afterwards fails even though every
individual outcome would look right.

Hermetic: the git surface and the runner are injected. No network, no real `gh`,
no push, no subprocess.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/test_drain.py -q
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DRAIN_PY = REPO_ROOT / "scripts" / "dispatch" / "drain.py"


def _load():
    pkg = str(DRAIN_PY.parent)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location("dispatch_drain", DRAIN_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_drain"] = mod
    spec.loader.exec_module(mod)
    return mod


D = _load()
records = sys.modules["records"]
reconcile = sys.modules["reconcile"]

ISSUE = "vamseeachanta/digitalmodel#1885"
OURS = "host-a"
OTHER = "host-b"
NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def clock(dt=NOW):
    return lambda: dt


@pytest.fixture
def armed(monkeypatch):
    """Arm the environment gate for the tests that need the real path."""
    monkeypatch.setenv(D.APPLY_FLAG, "1")


@pytest.fixture
def disarmed(monkeypatch):
    monkeypatch.delenv(D.APPLY_FLAG, raising=False)


# --------------------------------------------------------------------------
# doubles
# --------------------------------------------------------------------------


class FakeGit:
    """Injected git surface, sharing a call list with the runner.

    Same shape as `tests/dispatch/test_claim_protocol.py:FakeGit`. `remote_holder`
    is what the remote's copy of the record NAMES — because an accepted push does
    not prove our claim survived, and the drain must inherit that check rather
    than re-deriving it.
    """

    def __init__(self, calls=None, push_ok=True, remote_holder=OURS,
                 fail_push_after=None):
        self.calls = calls if calls is not None else []
        self.push_ok = push_ok
        self.remote_holder = remote_holder
        self.fail_push_after = fail_push_after
        self.pushes = 0
        self.last_written: dict | None = None

    def commit(self, path, message):
        self.calls.append("commit")
        self.last_written = json.loads(Path(path).read_text(encoding="utf-8"))
        return True

    def push(self):
        self.calls.append("push")
        self.pushes += 1
        if self.fail_push_after is not None and self.pushes > self.fail_push_after:
            return False
        return self.push_ok

    def pull(self):
        self.calls.append("pull")
        return True

    def read_remote(self, issue):
        self.calls.append("read_remote")
        if self.last_written is None:
            return None
        remote = dict(self.last_written)
        remote["host"] = self.remote_holder
        return remote


class FakeRunner:
    """The execution surface. Records that — and when — it was asked."""

    def __init__(self, calls=None, returncode=0, raises=None, job_state="finished"):
        self.calls = calls if calls is not None else []
        self.returncode = returncode
        self.raises = raises
        self.job_state = job_state
        self.seen: list[dict] = []

    def describe(self, **kw):
        return "fake-runner"

    def execute(self, *, issue, job_id, command, work_dir=None):
        self.calls.append("execute")
        self.seen.append({"issue": issue, "job_id": job_id, "command": command,
                          "work_dir": work_dir})
        if self.raises is not None:
            raise self.raises
        return D.ExecOutcome(self.returncode, job_state=self.job_state,
                             log_ref="/state/dispatch/j1")


class Exploding:
    """Every method is a bug. Used where NOTHING may be called."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def boom(*a, **kw):
            raise AssertionError(f"a dry run reached {name}() — it must not")
        return boom


def wired(**kw):
    """A git+runner pair sharing one call list, so order is observable."""
    calls: list[str] = []
    git = FakeGit(calls=calls, **{k: v for k, v in kw.items()
                                  if k in ("push_ok", "remote_holder", "fail_push_after")})
    runner = FakeRunner(calls=calls, **{k: v for k, v in kw.items()
                                        if k in ("returncode", "raises", "job_state")})
    return calls, git, runner


def run_drain(tmp_path, calls_git_runner=None, **kw):
    calls, git, runner = calls_git_runner or wired()
    params = dict(command="echo pilot", host=OURS, job_id="j1", git=git,
                  runner=runner, apply=True, now=clock())
    params.update(kw)
    return D.drain(tmp_path, ISSUE, **params), calls, git, runner


def on_disk(tmp_path):
    return records.read_record(records.record_path(tmp_path, ISSUE))


# --------------------------------------------------------------------------
# 1. the loop actually closes
# --------------------------------------------------------------------------


def test_the_happy_path_reaches_done_with_a_record_behind_it(tmp_path, armed):
    got, _calls, _git, runner = run_drain(tmp_path)

    assert got.ok is True and got.stage == D.RELEASED
    assert got.record["state"] == "done"
    assert got.record["returncode"] == 0
    assert got.work_succeeded is True
    assert records.is_success(on_disk(tmp_path)) is True
    assert runner.seen[0]["issue"] == ISSUE, "the run must carry the issue ref"


def test_the_order_is_claim_then_execute_then_release(tmp_path, armed):
    """Outcomes alone would pass an implementation that ran first and claimed after."""
    _got, calls, _git, _runner = run_drain(tmp_path)

    assert calls.index("read_remote") < calls.index("execute"), \
        "execution must follow the REMOTE verification, not merely the push"
    # claim: commit, push, read_remote — then execute — then release: commit, push
    assert calls[:3] == ["commit", "push", "read_remote"]
    assert calls[3] == "execute"
    assert calls[4:] == ["commit", "push"]


def test_the_exit_code_and_timings_round_trip_into_the_record(tmp_path, armed):
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=0))
    rec = on_disk(tmp_path)

    assert rec["issue"] == ISSUE
    assert rec["command_ref"] == "echo pilot"
    assert rec["log_ref"] == "/state/dispatch/j1"
    assert records._parse(rec["started_at"]) is not None, \
        "started_at must be in the format records.py parses, not merely a string"
    assert records._parse(rec["finished_at"]) is not None
    assert got.record["attempts"][-1]["outcome"], "the attempt must carry its outcome"


# --------------------------------------------------------------------------
# 2. a refused claim NEVER executes
# --------------------------------------------------------------------------


def test_a_rejected_push_does_not_execute(tmp_path, armed):
    got, calls, _git, runner = run_drain(tmp_path, calls_git_runner=wired(push_ok=False))

    assert got.ok is False and got.stage == D.CLAIM_REFUSED
    assert runner.seen == [] and "execute" not in calls, \
        "another host won the race; running anyway races one licence seat"
    assert got.record is None


def test_an_accepted_push_whose_remote_names_someone_else_does_not_execute(tmp_path, armed):
    """The subtlety slice 2 exists for, inherited rather than re-derived."""
    got, calls, _git, runner = run_drain(
        tmp_path, calls_git_runner=wired(remote_holder=OTHER))

    assert got.ok is False and got.stage == D.CLAIM_REFUSED
    assert "execute" not in calls
    assert runner.seen == []


def test_an_issue_held_by_another_host_is_refused_before_any_git_call(tmp_path, armed):
    records.write_record(tmp_path, records.new_claim(
        ISSUE, machine=OTHER, host=OTHER, job_id="theirs", now=clock()))
    before = records.record_path(tmp_path, ISSUE).read_bytes()

    got, calls, _git, runner = run_drain(tmp_path)

    assert got.ok is False and got.stage == D.REFUSED
    assert OTHER in got.reason
    assert calls == [], "a decided conflict needs no push to discover"
    assert runner.seen == []
    assert records.record_path(tmp_path, ISSUE).read_bytes() == before, \
        "someone else's record must come back byte-identical"


def test_a_quarantined_issue_is_not_re_run(tmp_path, armed):
    rec = records.new_claim(ISSUE, machine=OURS, host=OURS, job_id="j0", now=clock())
    records.write_record(tmp_path, records.transition(
        rec, "blocked", reason="attempts exhausted",
        failure_category="quarantine", now=clock()))

    got, calls, _g, runner = run_drain(tmp_path)

    assert got.ok is False and got.stage == D.REFUSED
    assert "quarantin" in got.reason.lower()
    assert runner.seen == [] and calls == []


def test_an_unreadable_record_is_never_overwritten(tmp_path, armed):
    path = records.record_path(tmp_path, ISSUE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")

    got, calls, _g, runner = run_drain(tmp_path)

    assert got.ok is False and got.stage == D.REFUSED
    assert path.read_text(encoding="utf-8") == "{not json"
    assert runner.seen == [] and calls == []


def test_a_refused_claim_projects_no_label(tmp_path, armed):
    """Records -> labels. No record, no projection — not even a computed one."""
    gh_calls = []

    def gh_fn(args):
        gh_calls.append(args)
        raise AssertionError("a refused claim must not reach a label write")

    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(push_ok=False),
                                labels={"dispatch:ready"}, gh_fn=gh_fn)
    assert got.ok is False
    assert got.intended_label is None and got.label_stats is None
    assert gh_calls == []


# --------------------------------------------------------------------------
# 3. a failure is recorded as a failure
# --------------------------------------------------------------------------


def test_a_nonzero_exit_is_recorded_as_a_real_failure(tmp_path, armed):
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=3))
    rec = on_disk(tmp_path)

    assert rec["state"] == "done", "it ran to completion — that IS done"
    assert rec["returncode"] == 3
    assert rec["failure_category"] == D.PAYLOAD_ERROR
    assert records.is_success(rec) is False, "done + nonzero is NOT success"
    assert got.work_succeeded is False
    assert D.exit_code(got) == 1, "a failed payload must not exit 0"


def test_an_unknown_outcome_is_blocked_and_never_a_zero(tmp_path, armed):
    """The status verb told us nothing. Recording 0 would invent an observation."""
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=None))
    rec = on_disk(tmp_path)

    assert rec["state"] == "blocked"
    assert rec["returncode"] is None
    assert rec["failure_category"] == D.UNKNOWN_OUTCOME
    assert records.is_success(rec) is False
    assert got.work_succeeded is False


def test_a_runner_that_raises_still_leaves_a_truthful_terminal_record(tmp_path, armed):
    """Otherwise the item stays `active` until its TTL expires and gets re-run —
    the original defect one layer up: work that ended with nothing recording it."""
    got, _c, _g, _r = run_drain(
        tmp_path, calls_git_runner=wired(raises=OSError("runner host gone")))
    rec = on_disk(tmp_path)

    assert rec["state"] in records.TERMINAL
    assert rec["state"] == "blocked" and rec["returncode"] is None
    assert rec["failure_category"] == D.UNKNOWN_OUTCOME
    assert "runner host gone" in rec["reason"]
    assert got.ok is True, "the loop closed — on a failure, truthfully recorded"
    assert got.work_succeeded is False


def test_a_signal_death_and_a_dispatch_error_are_distinguishable(tmp_path, armed):
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=143))
    assert on_disk(tmp_path)["failure_category"] == D.CANCELLED

    assert D.classify(D.ExecOutcome(D.EX_NOINPUT))[2] == D.DISPATCH_ERROR
    assert D.classify(D.ExecOutcome(0)) == ("done", "ran to completion, exit 0", None)


def test_a_release_that_cannot_be_pushed_is_reported_not_swallowed(tmp_path, armed):
    """The remote still shows the item as held; saying `ok` would hide that."""
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(fail_push_after=1))

    assert got.ok is False and got.stage == D.RELEASE_FAILED
    assert "push" in got.reason.lower()
    assert got.returncode == 0, "the observed exit code is still reported"
    assert D.exit_code(got) == 2


# --------------------------------------------------------------------------
# 4. dry run by default
# --------------------------------------------------------------------------


def test_the_default_is_a_dry_run_that_reaches_no_write_primitive(tmp_path, disarmed):
    printed: list[str] = []
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock(),
                  log=printed.append)

    assert got.ok is True and got.stage == D.PLANNED and got.dry_run is True
    assert list(tmp_path.iterdir()) == [], "a dry run wrote a record"
    assert got.record is None, "a plan must not be reachable as a record"
    assert got.planned["issue"] == ISSUE
    assert "echo pilot" in "\n".join(printed) and ISSUE in "\n".join(printed)


def test_an_armed_environment_does_not_by_itself_make_a_drain_write(tmp_path, armed):
    """The env var is the second lock, not the first. Without --apply: still dry.

    This is the test that discriminates the dry-run branch itself — the gate test
    below would still pass if the branch were deleted.
    """
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock())

    assert got.stage == D.PLANNED and got.dry_run is True
    assert list(tmp_path.iterdir()) == []


def test_asking_to_apply_without_the_env_gate_is_refused(tmp_path, disarmed):
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), apply=True, now=clock())

    assert got.ok is False and got.stage == D.REFUSED
    assert D.APPLY_FLAG in got.reason
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("value", ["0", "false", "off", "", "yes please"])
def test_only_the_shared_affirmative_set_arms_writes(tmp_path, monkeypatch, value):
    """Bound to reconcile's gate, not a second opinion about what armed means."""
    monkeypatch.setenv(D.APPLY_FLAG, value)
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), apply=True, now=clock())
    assert got.ok is False
    assert list(tmp_path.iterdir()) == []


def test_the_gate_is_the_same_one_the_rest_of_dispatch_uses(tmp_path):
    assert D.APPLY_FLAG is reconcile.APPLY_FLAG


def test_the_dry_run_plan_describes_the_run_that_would_happen(tmp_path, disarmed):
    records.write_record(tmp_path, records.transition(
        records.new_claim(ISSUE, machine=OURS, host=OURS, job_id="j0", now=clock()),
        "done", reason="completed", returncode=0, now=clock()))
    printed: list[str] = []
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock(), log=printed.append)

    assert got.action == D.RECLAIM
    text = "\n".join(printed)
    assert "reclaim" in text and "attempt 2" in text
    assert D.APPLY_FLAG in text, "the plan must name what would arm it"


# --------------------------------------------------------------------------
# 5. idempotent / resumable
# --------------------------------------------------------------------------


def test_re_running_against_our_own_live_claim_re_enters_it(tmp_path, armed):
    """A dropped SSH session must not make the record say it was tried twice."""
    records.write_record(tmp_path, records.new_claim(
        ISSUE, machine=OURS, host=OURS, job_id="j1", now=clock()))

    got, _c, _g, runner = run_drain(tmp_path)

    assert got.ok is True and got.action == D.RESUME
    rec = on_disk(tmp_path)
    assert rec["attempt"] == 1, "a resume is not a second attempt"
    assert rec["job_id"] == "j1"
    assert len(rec["attempts"]) == 1
    assert runner.seen[0]["job_id"] == "j1"


def test_draining_twice_leaves_one_coherent_terminal_record(tmp_path, armed):
    first, _c, _g, _r = run_drain(tmp_path)
    second, _c2, _g2, _r2 = run_drain(tmp_path, job_id="j2")

    assert first.ok is True and second.ok is True
    rec = on_disk(tmp_path)
    assert rec["attempt"] == 2 and second.action == D.RECLAIM
    assert [a["attempt"] for a in rec["attempts"]] == [1, 2], \
        "history is appended, never overwritten — flapping must stay visible"
    assert rec["state"] == "done"


def test_attempts_are_bounded(tmp_path, armed):
    rec = records.new_claim(ISSUE, machine=OURS, host=OURS, job_id="j1",
                            max_attempts=2, now=clock())
    rec["attempt"] = 2
    records.write_record(tmp_path, records.transition(
        rec, "done", reason="completed", returncode=1, now=clock()))

    got, _c, _g, runner = run_drain(tmp_path)
    assert got.ok is False and "attempts" in got.reason
    assert runner.seen == []


# --------------------------------------------------------------------------
# 6. projection — records to labels, one direction
# --------------------------------------------------------------------------


def test_the_label_is_derived_from_the_record_by_reconcile(tmp_path, armed):
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=7))

    assert got.intended_label == "dispatch:done", \
        "the projection follows the STATE; a failed payload still reached done"
    assert got.intended_label == reconcile.intended_label(got.record)


def test_supplying_the_label_snapshot_projects_it_through_reconcile(tmp_path, armed):
    seen = []

    class Ok:
        returncode = 0

    def gh_fn(args):
        seen.append(args)
        return Ok()

    got, _c, _g, _r = run_drain(tmp_path, labels={"dispatch:ready"}, gh_fn=gh_fn)

    assert got.label_stats["labels_written"] == 1
    flat = " ".join(seen[0])
    assert "--add-label dispatch:done" in flat
    assert "--remove-label dispatch:ready" in flat
    assert "1885" in flat and "vamseeachanta/digitalmodel" in flat


def test_no_label_snapshot_means_no_label_write_at_all(tmp_path, armed):
    def gh_fn(args):
        raise AssertionError("nothing to reconcile against — must not write")

    got, _c, _g, _r = run_drain(tmp_path, gh_fn=gh_fn)
    assert got.label_stats is None and got.intended_label == "dispatch:done"


# --------------------------------------------------------------------------
# 7. argument surface and the CLI
# --------------------------------------------------------------------------


@pytest.mark.parametrize("issue", ["1885", "digitalmodel#1885", "owner/repo#abc", ""])
def test_an_unqualified_issue_is_refused(tmp_path, armed, issue):
    """A record carries owner/repo#N so a write cannot land on the wrong repo."""
    got = D.drain(tmp_path, issue, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), apply=True, now=clock())
    assert got.ok is False and got.stage == D.REFUSED


def test_a_job_id_the_runner_would_reject_is_caught_before_the_claim(tmp_path, armed):
    """Discovering it after the claim strands the item on an unrunnable job."""
    got, calls, _g, runner = run_drain(tmp_path, job_id="../../etc/passwd")
    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []
    assert D.JOB_ID_RE.match(D.new_job_id(now=clock())), \
        "the minted id must satisfy the runner's own rule"


def test_the_runner_argv_matches_the_real_run_sh_verbs(tmp_path):
    """A drain that built the wrong argv would fail only on a live host."""
    r = D.ShellRunner(script="/x/run.sh")
    argv = r.submit_argv(issue=ISSUE, job_id="j1", command="echo pilot",
                         work_dir="/w")
    assert argv[:3] == ["bash", "/x/run.sh", "submit"]
    for flag in ("--command", "--issue-ref", "--job-id", "--foreground", "--work-dir"):
        assert flag in argv
    assert r.status_argv("j1") == ["bash", "/x/run.sh", "status", "--job-id", "j1"]

    w = D.PowerShellRunner(script="C:/x/dispatch-run.ps1")
    wargv = w.submit_argv(issue=ISSUE, job_id="j1", command="echo pilot", work_dir=None)
    for flag in ("-Action", "-Command", "-IssueRef", "-JobId"):
        assert flag in wargv
    assert "-Foreground" not in wargv, \
        "the Windows runner has no foreground verb — it is a Scheduled Task"


def test_the_cli_dry_run_writes_nothing_and_exits_zero(tmp_path, disarmed, capsys):
    rc = D.main(["--issue", ISSUE, "--records", str(tmp_path), "--command", "true"])
    assert rc == 0
    assert list(tmp_path.iterdir()) == []
    assert ISSUE in capsys.readouterr().out


def test_the_cli_refuses_to_apply_without_the_env_gate(tmp_path, disarmed, capsys):
    rc = D.main(["--issue", ISSUE, "--records", str(tmp_path), "--command", "true",
                 "--apply"])
    assert rc == 2
    assert D.APPLY_FLAG in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_the_module_documents_the_licence_asymmetry(tmp_path):
    """Load-bearing documentation: delete it and the fail-closed choice looks
    like caution rather than the consequence of one floating seat."""
    text = DRAIN_PY.read_text(encoding="utf-8")
    assert "3721" in text and "fail" in text.lower()


def test_the_failure_category_vocabulary_is_pinned_to_its_literal_values():
    """These strings are a WIRE CONTRACT, so pin them literally.

    Every other assertion about a category compares against the module's own
    constant — `rec["failure_category"] == D.UNKNOWN_OUTCOME` — which moves with
    the code under test. Found by mutation: setting `UNKNOWN_OUTCOME = None`
    left all 39 tests green, because both sides of the comparison changed
    together. Setting it to "ok" would pass too.

    That matters because these values are not internal. They are written into
    durable JSON records that operators read and downstream tooling joins on;
    silently renaming one breaks every consumer while the suite stays green.

    The safety property (state `blocked`, `returncode` null) IS pinned
    elsewhere and survived that mutation correctly. This closes the diagnostics
    half: a record saying `blocked` with no reason tells an operator that
    something went wrong and nothing about what.
    """
    assert D.UNKNOWN_OUTCOME == "unknown-outcome"
    assert D.PAYLOAD_ERROR == "payload-error"
    assert D.DISPATCH_ERROR == "dispatch-error"
    assert D.CANCELLED == "cancelled"

    vocabulary = {D.UNKNOWN_OUTCOME, D.PAYLOAD_ERROR, D.DISPATCH_ERROR, D.CANCELLED}
    assert len(vocabulary) == 4, "two categories collapsed onto one string"
    assert all(v and isinstance(v, str) for v in vocabulary), (
        "a falsy category reads as 'no failure' wherever it is truth-tested")
