#!/usr/bin/env python3
"""The heartbeat that lets a payload outlive its TTL. workspace-hub#3773, R4 lift.

`records.heartbeat()` shipped documented as "beaten OUT-OF-BAND while the child
process runs" and **nothing beat it**. It was called in exactly one place — the
RESUME branch of `drain.prepare` — so `heartbeat_at` froze at claim time. Any
payload outliving `ttl_minutes` had an expired record while it was still
running, `reconcile.settle` returned it to `ready`, and the next `prepare`
RECLAIMed it: two payloads, one issue, one floating solver seat (wh#3721).

R4 closed that by REFUSING the configuration — `max(timeout, runner.timeout) >=
ttl_minutes * 60`. Correct, and a hard ceiling: no payload could run longer than
90 minutes. This file proves the beater that lifts it.

The whole design is bounded by ONE asymmetry, which every test here exists to
hold:

    a beat that is missed costs one TTL of delay.
    a beat that makes a DEAD HOLDER LOOK ALIVE strands the issue forever.

So a beat is never a write we are entitled to make — it is a write we must
re-earn from the record store on every single tick: the record must still be
there, still name this host and job, and still be `active`. Anything else stops
the beater. That is why `claim.beat` re-reads from disk rather than beating the
copy it was handed, and why the beater is joined BEFORE the outcome is written.

Cost is the other constraint. `claim.py` commits AND pushes every record write,
so a naive 30-second beat is ~480 pushes to `main` for one 4-hour card. The beat
interval is therefore a FRACTION OF THE TTL, not a constant: cost is
`run_length / (ttl / BEATS_PER_TTL)`, and raising the TTL lowers it.

Hermetic: git, the runner, the clock and the routing rules are injected. No
network, no `gh`, no push, no real subprocess.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/test_heartbeat.py -q
"""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
from datetime import datetime, timedelta, timezone
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
claim = sys.modules["claim"]

ISSUE = "vamseeachanta/digitalmodel#1885"
OURS = "host-a"
OTHER = "host-b"
NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def clock(dt=NOW):
    return lambda: dt


@pytest.fixture
def armed(monkeypatch):
    monkeypatch.setenv(D.APPLY_FLAG, "1")


@pytest.fixture
def disarmed(monkeypatch):
    monkeypatch.delenv(D.APPLY_FLAG, raising=False)


def caps(**per_machine):
    per_machine.setdefault("default", 1)
    return lambda: {"wip_caps": {"per_machine": dict(per_machine)}}


def held_claim(root, *, issue=ISSUE, host=OURS, job_id="j1", now=clock()):
    """A live claim on disk, exactly as `claim.acquire` would have left it."""
    rec = records.new_claim(issue, machine=host, host=host, job_id=job_id, now=now)
    records.write_record(root, rec)
    return rec


def on_disk(root, issue=ISSUE):
    return records.read_record(records.record_path(root, issue))


def land_record(root, record):
    """Put a record on disk the way a `git pull` does — past the create-only guard.

    `records.write_record` refuses to overwrite ANOTHER host's live claim, which
    is the point of that guard. But the case a beat has to survive is precisely
    the one it cannot produce locally: somebody else's claim arriving in the
    checkout from the remote.
    """
    records.record_path(root, record["issue"]).write_text(
        json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return record


def beat_of(record):
    return records._parse(record.get("heartbeat_at"))


# ==========================================================================
# doubles
# ==========================================================================


class RecordingGit:
    """Records WHAT each commit carried, so a beat can be told from a release.

    `FakeGit` in the sibling files records only that a commit happened. The
    question this file has to answer — "did an `active` record get written AFTER
    a terminal one?" — is invisible at that resolution.
    """

    def __init__(self, calls=None, push_ok=True, remote_holder=OURS):
        self.calls = calls if calls is not None else []
        self.commits: list[dict] = []
        self.push_ok = push_ok
        self.remote_holder = remote_holder
        self.last_written: dict | None = None
        #: Set once a commit that is NOT the claim carries an `active` record —
        #: i.e. the beater has beaten. Lets a payload double block on a real beat
        #: instead of on a sleep.
        self.beaten = threading.Event()

    def commit(self, path, message):
        self.calls.append("commit")
        rec = json.loads(Path(path).read_text(encoding="utf-8"))
        self.last_written = rec
        self.commits.append({"message": message, "state": rec.get("state"),
                             "heartbeat_at": rec.get("heartbeat_at"),
                             "job_id": rec.get("job_id"), "host": rec.get("host")})
        return True

    def push(self):
        self.calls.append("push")
        if len(self.commits) > 1 and self.commits[-1]["state"] == "active":
            self.beaten.set()
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

    # -- derived views the assertions read ------------------------------

    def active_commits(self):
        return [c for c in self.commits if c["state"] == "active"]

    def first_terminal_index(self):
        for i, c in enumerate(self.commits):
            if c["state"] in records.TERMINAL:
                return i
        return None


class ExplodingGit:
    def commit(self, path, message):
        raise RuntimeError("git is on fire")

    def push(self):
        raise RuntimeError("git is on fire")


class BeatingRunner:
    """A payload that does not return until the beater has actually beaten.

    Blocking on a real beat rather than on a sleep is what keeps this hermetic:
    there is no interval to tune and no wall-clock race to lose on a loaded box.
    """

    def __init__(self, git, calls=None, returncode=0, raises=False):
        self.git = git
        self.calls = calls if calls is not None else []
        self.returncode = returncode
        self.raises = raises
        self.beat_seen = False
        self.seen: list[dict] = []

    def describe(self, **kw):
        return "beating-runner"

    def execute(self, *, issue, job_id, command, work_dir=None):
        self.calls.append("execute")
        self.seen.append({"issue": issue, "job_id": job_id, "command": command})
        self.beat_seen = self.git.beaten.wait(timeout=30)
        if self.raises:
            raise RuntimeError("the payload blew up")
        return D.ExecOutcome(self.returncode, job_state="finished")


class ThreadWatchRunner:
    """Looks for a beater thread WHILE the payload runs.

    Counting beats cannot answer "was a beater started?": a payload that returns
    immediately lets `stop()` win the race before the first interval elapses, so
    zero beats is what a correctly-suppressed beater AND a wrongly-started one
    both look like. A mutation pass caught exactly that — `if heartbeat:` changed
    to `if True:` left the suite green. The thread is the property; the beats are
    a side effect of one.
    """

    def __init__(self, calls=None, returncode=0):
        self.calls = calls if calls is not None else []
        self.returncode = returncode
        self.seen: list[dict] = []
        self.beaters_during_run: list[str] = []

    def describe(self, **kw):
        return "thread-watch-runner"

    def execute(self, *, issue, job_id, command, work_dir=None):
        self.calls.append("execute")
        self.seen.append({"issue": issue, "job_id": job_id, "command": command})
        self.beaters_during_run = [
            t.name for t in threading.enumerate()
            if t.name.startswith("dispatch-heartbeat-")]
        return D.ExecOutcome(self.returncode, job_state="finished")


class JoinWatchGit(RecordingGit):
    """Looks for a live beater AT THE MOMENT the outcome is committed.

    Asserting "no `active` record followed the terminal one" catches the failure
    only when the race is lost, which is most of the time and not all of it. This
    asks the question directly and deterministically: was the beater still
    running when `claim.release` wrote?
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.beaters_at_outcome: list[str] | None = None

    def commit(self, path, message):
        rec = json.loads(Path(path).read_text(encoding="utf-8"))
        if rec.get("state") in records.TERMINAL and self.beaters_at_outcome is None:
            self.beaters_at_outcome = [
                t.name for t in threading.enumerate()
                if t.name.startswith("dispatch-heartbeat-")]
        return super().commit(path, message)


class FakeTime:
    """A clock that only moves when the beater waits on it.

    `max_waits` exists so a beater that never terminates FAILS rather than
    hanging. Found by mutation: deleting the deadline check made the loop
    unbounded, and the suite's answer was a CI timeout — a red that names no
    property and blocks the run for its whole limit.
    """

    def __init__(self, stop_after=None, max_waits=10_000):
        self.t = 0.0
        self.waits = 0
        self.stop_after = stop_after
        self.max_waits = max_waits

    def clock(self):
        return self.t

    def wait(self, seconds):
        self.waits += 1
        if self.waits > self.max_waits:
            raise AssertionError(
                f"the beater was still going after {self.waits} intervals "
                f"({self.t:.0f}s of its own clock) — nothing bounded it")
        self.t += float(seconds)
        return self.stop_after is not None and self.waits > self.stop_after


def beats(*results):
    """A `beat_fn` double returning a scripted sequence, then its last value."""
    seen: list[dict] = []
    seq = list(results)

    def fn(root, record, *, git=None):
        seen.append(dict(record))
        return seq[len(seen) - 1] if len(seen) <= len(seq) else seq[-1]

    fn.seen = seen
    return fn


def run_drain(tmp_path, git=None, runner=None, **kw):
    calls: list[str] = []
    git = git if git is not None else RecordingGit(calls=calls)
    runner = runner if runner is not None else BeatingRunner(git, calls=calls)
    params = dict(command="echo pilot", host=OURS, job_id="j1", git=git,
                  runner=runner, apply=True, now=clock(),
                  rules_loader=caps(**{OURS: 1}), beat_interval=0.001)
    params.update(kw)
    return D.drain(tmp_path, ISSUE, **params), calls, git, runner


# ==========================================================================
# A — the beat interval is derived from the TTL, because the cost is pushes
# ==========================================================================


def test_the_beat_interval_is_a_fraction_of_the_ttl_not_a_constant():
    """A constant interval makes the push bill grow with run length and gives an
    operator no dial. Deriving it from the TTL means raising the TTL — the very
    thing a long payload needs — LOWERS the number of pushes per run."""
    assert records.beat_interval_seconds(90) * records.BEATS_PER_TTL == 90 * 60
    assert records.beat_interval_seconds(240) == 2 * records.beat_interval_seconds(120)


def test_the_interval_leaves_room_for_consecutive_missed_beats():
    """A beat is a push, and a push loses races. If the interval were the TTL,
    one lost race would expire a live claim; the margin is what makes a missed
    beat cost nothing at all."""
    for ttl in (5, 90, 240, 1440):
        interval = records.beat_interval_seconds(ttl)
        assert interval * 2 < ttl * 60, (
            f"ttl {ttl}m leaves no slack: one missed beat would expire the record")
        # N-1 consecutive failures still leave an attempt inside the window.
        assert interval * (records.BEATS_PER_TTL - 1) < ttl * 60


def test_a_tiny_ttl_is_floored_rather_than_becoming_a_push_storm():
    """`ttl/BEATS_PER_TTL` on a 20-second TTL is a push every 5 seconds, on a
    branch several lanes and auto-sync already contend for."""
    assert records.beat_interval_seconds(1) >= records.MIN_BEAT_SECONDS
    assert records.MIN_BEAT_SECONDS > 0


def test_the_number_of_pushes_a_long_run_costs_stays_bounded():
    """The reason a naive beater was not shipped: 30s beats over 4 hours is ~480
    commits pushed to `main` for ONE card. Pin the economics, not the constant."""
    four_hours = 4 * 60 * 60
    pushes = four_hours / records.beat_interval_seconds(90)
    assert pushes < 20, f"a 4h run under a 90m ttl costs {pushes} pushes"


# ==========================================================================
# B — a beat is a write that must be RE-EARNED from the record store
# ==========================================================================


def test_a_beat_refreshes_the_heartbeat_on_disk_and_pushes_it(tmp_path):
    """`reconcile` may run on a host that never saw our local file. A beat that
    only touched the working tree would be invisible exactly where the reclaim
    decision is made."""
    rec = held_claim(tmp_path)
    git = RecordingGit()

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is False and got.written is True and got.pushed is True
    assert got.landed is True
    assert beat_of(on_disk(tmp_path)) > beat_of(rec), "the heartbeat did not advance"
    assert git.commits and git.commits[-1]["state"] == "active"


def test_a_beat_carries_the_on_disk_record_forward_not_our_stale_copy(tmp_path):
    """The beater holds a copy from claim time. Beating THAT would silently
    revert anything written since — the log ref, the attempt list, the started
    stamp — turning a liveness signal into a data-loss mechanism."""
    rec = held_claim(tmp_path)
    moved = dict(on_disk(tmp_path))
    moved["log_ref"] = "/jobs/j1"
    moved["started_at"] = "2026-08-01T12:00:30Z"
    records.write_record(tmp_path, moved)

    claim.beat(tmp_path, rec, git=RecordingGit())

    after = on_disk(tmp_path)
    assert after["log_ref"] == "/jobs/j1" and after["started_at"] == "2026-08-01T12:00:30Z"
    assert beat_of(after) > beat_of(rec)


def test_a_beat_on_a_record_that_is_no_longer_ours_stops_and_writes_nothing(tmp_path):
    """If another host's claim is on disk, a beat would refresh THEIR record —
    the drain docstring's forbidden second opinion about someone else's
    liveness, in the one place it could actually strand an issue."""
    rec = held_claim(tmp_path)
    theirs = dict(on_disk(tmp_path))
    theirs["host"] = OTHER
    theirs["job_id"] = "their-job"
    land_record(tmp_path, theirs)
    git = RecordingGit()

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is True and got.written is False and got.pushed is False
    after = on_disk(tmp_path)
    assert after["host"] == OTHER and after["job_id"] == "their-job"
    assert after["heartbeat_at"] == theirs["heartbeat_at"], "their heartbeat moved"
    assert git.commits == []


def test_a_beat_on_a_terminal_record_stops_and_does_not_resurrect_it(tmp_path):
    """THE failure this whole design is bounded by. A beat that landed after the
    outcome would write an `active` record over a `done` one: the issue would
    read as held, by a host that finished, forever — a permanent strand instead
    of a 90-minute one."""
    rec = held_claim(tmp_path)
    records.write_record(tmp_path, records.transition(
        on_disk(tmp_path), "done", reason="ran to completion, exit 0", returncode=0))
    ended = on_disk(tmp_path)
    git = RecordingGit()

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is True and got.written is False
    after = on_disk(tmp_path)
    assert after["state"] == "done" and after["state"] in records.TERMINAL
    assert after["returncode"] == 0
    assert after["heartbeat_at"] == ended["heartbeat_at"]
    assert git.commits == []


def test_a_beat_on_a_record_settled_back_to_ready_stops(tmp_path):
    """`reconcile.settle` returning us to `ready` means our claim was judged
    dead and the issue is free. Beating it back to fresh would let this host
    keep an issue it no longer holds, while another host runs it."""
    rec = held_claim(tmp_path)
    records.write_record(tmp_path, records.transition(
        on_disk(tmp_path), "ready", reason="heartbeat expired"))
    git = RecordingGit()

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is True and got.written is False
    assert on_disk(tmp_path)["state"] == "ready"
    assert git.commits == []


def test_a_beat_on_a_vanished_record_stops_and_does_not_recreate_it(tmp_path):
    """A record that is gone is not one we can prove we hold. Writing it back
    would mint a claim out of a liveness signal."""
    rec = held_claim(tmp_path)
    records.record_path(tmp_path, ISSUE).unlink()
    git = RecordingGit()

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is True and got.written is False
    assert not records.record_path(tmp_path, ISSUE).exists()
    assert git.commits == []


def test_a_rejected_push_is_reported_and_does_not_stop_the_beat(tmp_path):
    """A beat commit is our own live claim, not a refused one: it is legitimately
    publishable and the next push carries it. Stopping on one lost race would
    turn a transient into an expiry of a job that is running perfectly."""
    rec = held_claim(tmp_path)
    git = RecordingGit(push_ok=False)

    got = claim.beat(tmp_path, rec, git=git)

    assert got.stop is False
    assert got.written is True and got.pushed is False and got.landed is False


def test_a_beat_never_undoes_its_own_commit_and_never_pulls(tmp_path):
    """`acquire` undoes a commit because a REFUSED claim must leave nothing
    publishable, and pulls to resync a host that lost a race. A beat is neither:
    undoing it would delete the liveness we just recorded, and `pull --rebase`
    from a background thread moves the branch under every other lane in the
    checkout."""
    rec = held_claim(tmp_path)
    calls: list[str] = []
    git = RecordingGit(calls=calls, push_ok=False)
    git.undo_commit = lambda path, record: (_ for _ in ()).throw(
        AssertionError("a beat undid its own commit"))

    claim.beat(tmp_path, rec, git=git)

    assert "pull" not in calls


def test_a_git_error_during_a_beat_is_contained(tmp_path):
    """A beater thread that raises kills the beat for the rest of the run and,
    worse, does it silently. The payload must not care that git hiccuped."""
    rec = held_claim(tmp_path)

    got = claim.beat(tmp_path, rec, git=ExplodingGit())

    assert got.stop is False and got.pushed is False and got.landed is False


def test_a_beat_result_cannot_be_mistaken_for_a_claim(tmp_path):
    """`ClaimResult` answers "may I execute?" — and `record` is None on refusal
    precisely so a truthiness check cannot become a second way to ask. A beat
    must not be able to answer that question at all."""
    rec = held_claim(tmp_path)
    got = claim.beat(tmp_path, rec, git=RecordingGit())

    assert not isinstance(got, claim.ClaimResult)
    assert not hasattr(got, "record")
    assert not hasattr(got, "ok")


# ==========================================================================
# C — the beater's lifetime is bounded three ways, not one
# ==========================================================================


def test_a_job_shorter_than_one_interval_costs_no_beats_at_all(tmp_path):
    """The beat is due when the record is at risk, not when the job starts. Most
    cards finish well inside one interval and must cost zero pushes."""
    fake = FakeTime()
    fn = beats(claim.BeatResult(written=True, pushed=True))
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=1350, deadline=600, beat_fn=fn,
                     clock=fake.clock, wait=fake.wait)

    hb.run()

    assert fn.seen == [], "a beat fired before the first interval elapsed"


def test_the_beater_stops_at_its_own_deadline_even_if_nobody_stops_it(tmp_path):
    """The fail-safe. If the drain wedges — in a git call, in a runner that never
    returns — an unbounded beater keeps a dead holder looking alive forever. Two
    independent stop conditions, so losing the signal one does not lose both."""
    fake = FakeTime()
    fn = beats(claim.BeatResult(written=True, pushed=True))
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=100, deadline=450, beat_fn=fn,
                     clock=fake.clock, wait=fake.wait)

    hb.run()

    assert len(fn.seen) == 4, "the beater ran past its deadline"
    assert fake.t < 600
    assert any("deadline" in w for w in hb.warnings)


def test_the_beater_stops_the_moment_the_claim_stops_being_ours(tmp_path):
    """Delegated to `claim.beat`, which re-earns the write every tick. The
    beater must ACT on that answer, and say so — a claim taken from under a
    running payload is the loudest thing this loop can learn."""
    fake = FakeTime()
    fn = beats(claim.BeatResult(written=True, pushed=True),
               claim.BeatResult(stop=True, reason="the record is held by host-b/their-job"))
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=100, deadline=100000, beat_fn=fn,
                     clock=fake.clock, wait=fake.wait)

    hb.run()

    assert len(fn.seen) == 2, "the beater kept beating a claim that is not ours"
    assert any("host-b/their-job" in w for w in hb.warnings)


def test_persistently_missed_beats_are_reported_once_the_record_must_be_stale(tmp_path):
    """A beater that cannot land is indistinguishable, from outside, from a dead
    host — which is CORRECT, and it is also the moment another host may start a
    second payload on the one solver seat. It is not actionable from here, so it
    is reported, exactly as an unconfirmed cancel is."""
    fake = FakeTime()
    fn = beats(claim.BeatResult(written=True, pushed=False))
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=400,
                     interval=100, deadline=900, beat_fn=fn,
                     clock=fake.clock, wait=fake.wait)

    hb.run()

    stale = [w for w in hb.warnings if "expired" in w or "stale" in w]
    assert stale, f"no warning that the record must now be expired: {hb.warnings}"
    assert len(stale) == 1, "the warning repeated once per tick"


def test_a_landed_beat_clears_the_staleness_it_was_measuring(tmp_path):
    """Discriminator: a warning that fires whatever happens is not a signal. One
    lost push inside the margin must produce nothing at all."""
    fake = FakeTime()
    fn = beats(claim.BeatResult(written=True, pushed=False),
               claim.BeatResult(written=True, pushed=True),
               claim.BeatResult(written=True, pushed=True))
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=400,
                     interval=100, deadline=350, beat_fn=fn,
                     clock=fake.clock, wait=fake.wait)

    hb.run()

    assert [w for w in hb.warnings if "expired" in w or "stale" in w] == []


def test_a_beater_that_will_not_stop_is_reported_never_assumed_stopped(tmp_path):
    """`stop()` must JOIN, not merely signal: the outcome write happens next, and
    a beat still in flight would land on top of it. If the join is lost, the one
    thing that must not happen is silence."""
    entered = threading.Event()
    release = threading.Event()

    def wedged(root, record, *, git=None):
        entered.set()
        release.wait(timeout=30)
        return claim.BeatResult(written=True, pushed=True)

    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=0.0, deadline=600, beat_fn=wedged)
    hb.start()
    try:
        assert entered.wait(timeout=30)
        assert hb.stop(timeout=0.2) is False
        assert any("did not stop" in w for w in hb.warnings)
    finally:
        release.set()
        hb.stop(timeout=30)


def test_stop_joins_a_healthy_beater_and_reports_nothing(tmp_path):
    """Discriminator for the test above."""
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=0.001, deadline=600,
                     beat_fn=beats(claim.BeatResult(written=True, pushed=True)))
    hb.start()
    assert hb.stop(timeout=30) is True
    assert [w for w in hb.warnings if "did not stop" in w] == []


def test_the_beater_thread_cannot_outlive_its_process(tmp_path):
    """A beater in a detached PROCESS would survive the drain that owns it and
    beat a claim whose payload died — the worst state in this design. A daemon
    thread dies with the interpreter, so the process is the hard bound."""
    hb = D.Heartbeat(tmp_path, held_claim(tmp_path), git=None, ttl_seconds=5400,
                     interval=0.001, deadline=600,
                     beat_fn=beats(claim.BeatResult(written=True, pushed=True)))
    hb.start()
    try:
        assert hb._thread.daemon is True
    finally:
        hb.stop(timeout=30)


# ==========================================================================
# D — the drain beats only a claim it holds, and stops before it releases
# ==========================================================================


def test_the_payload_is_beaten_while_it_runs(tmp_path, armed):
    """The defect: `heartbeat_at` froze at claim time and nothing moved it."""
    got, _calls, git, runner = run_drain(tmp_path)

    assert got.ok is True and got.stage == D.RELEASED
    assert runner.beat_seen is True
    active = git.active_commits()
    assert len(active) >= 2, "only the claim commit carried a heartbeat"
    assert records._parse(active[-1]["heartbeat_at"]) > \
        records._parse(active[0]["heartbeat_at"])


def test_no_beat_lands_after_the_outcome_is_recorded(tmp_path, armed):
    """The load-bearing ordering. `stop()` joins BEFORE `claim.release` writes,
    and `claim.beat` re-checks the on-disk state, so there are two independent
    reasons an `active` record can never follow a terminal one."""
    got, _calls, git, _runner = run_drain(tmp_path)

    end = git.first_terminal_index()
    assert end is not None, "no terminal record was ever committed"
    after = [c for c in git.commits[end + 1:] if c["state"] == "active"]
    assert after == [], f"a beat landed after the outcome: {after}"
    assert on_disk(tmp_path)["state"] in records.TERMINAL
    assert got.record["returncode"] == 0


def test_the_beater_is_stopped_even_when_the_runner_raises(tmp_path, armed):
    """A `finally`, not a happy-path call. The exception path is exactly where a
    forgotten stop leaves a beater running against a payload that is gone."""
    calls: list[str] = []
    git = RecordingGit(calls=calls)
    runner = BeatingRunner(git, calls=calls, raises=True)

    got, _calls, git, runner = run_drain(tmp_path, git=git, runner=runner)

    assert runner.beat_seen is True
    assert got.record["state"] == "blocked"
    assert got.record["returncode"] is None, "an unobserved outcome became a code"
    end = git.first_terminal_index()
    assert [c for c in git.commits[end + 1:] if c["state"] == "active"] == []


def test_the_beater_is_joined_before_the_outcome_is_written(tmp_path, armed):
    """`stop()` SIGNALS and JOINS, and the join is what orders the two writes.

    Signalling alone leaves a beat in flight that can land on top of the terminal
    record. `claim.beat` would refuse it on its own state check, so this is the
    second of two independent guards — and it is the one that makes the ordering
    a fact rather than a race won."""
    calls: list[str] = []
    git = JoinWatchGit(calls=calls)
    runner = BeatingRunner(git, calls=calls)

    got, _calls, git, runner = run_drain(tmp_path, git=git, runner=runner)

    assert got.ok is True and runner.beat_seen is True
    assert git.beaters_at_outcome == [], (
        f"the outcome was written with a beater still running: "
        f"{git.beaters_at_outcome}")


def test_the_beater_is_joined_before_the_outcome_of_a_runner_that_raised(
        tmp_path, armed):
    """The exception path, deterministically. This is where a stop that is not in
    a `finally` leaves a beater refreshing a claim whose payload is gone."""
    calls: list[str] = []
    git = JoinWatchGit(calls=calls)
    runner = BeatingRunner(git, calls=calls, raises=True)

    got, _calls, git, runner = run_drain(tmp_path, git=git, runner=runner)

    assert got.record["state"] == "blocked"
    assert git.beaters_at_outcome == []


def test_no_heartbeat_starts_no_beater_at_all(tmp_path, armed):
    """The switch must reach the BEATER, not only the rail. A flag that changed
    what is refused but not what runs would let an operator who turned beating
    off still get beats — and, read the other way, would leave a lifted ceiling
    resting on a beater that was never started.

    Asserted on the THREAD rather than on the beats: a payload that returns
    inside one interval produces zero beats whether or not a beater exists, so
    counting commits here answers a different question than the one asked."""
    calls: list[str] = []
    git = RecordingGit(calls=calls)

    got, _calls, git, runner = run_drain(tmp_path, git=git,
                                         runner=ThreadWatchRunner(calls=calls),
                                         heartbeat=False)

    assert got.ok is True and len(runner.seen) == 1
    assert runner.beaters_during_run == [], \
        f"--no-heartbeat started {runner.beaters_during_run}"
    assert len(git.active_commits()) == 1


def test_beating_is_on_by_default(tmp_path, armed):
    """Discriminator for the test above, and the shipped choice: a heartbeat that
    must be opted into is one that is off on the host where the four-hour run
    happens."""
    calls: list[str] = []
    git = RecordingGit(calls=calls)

    got, _calls, git, runner = run_drain(tmp_path, git=git,
                                         runner=ThreadWatchRunner(calls=calls))

    assert got.ok is True
    assert len(runner.beaters_during_run) == 1, \
        "no beater was running while the payload ran"


def test_the_default_beater_actually_beats(tmp_path, armed):
    """A thread that exists and never writes is the original defect with a
    thread in front of it."""
    got, _calls, git, runner = run_drain(tmp_path)

    assert got.ok is True and runner.beat_seen is True
    assert len(git.active_commits()) >= 2


def test_a_refused_claim_beats_nothing(tmp_path, armed):
    """`ok is True` is the only licence to execute, and it is the only licence to
    beat. A beater started before the claim verified would refresh a record the
    remote says belongs to somebody else."""
    got, _calls, git, runner = run_drain(tmp_path, git=RecordingGit(push_ok=False))

    assert got.ok is False and got.stage == D.CLAIM_REFUSED
    assert runner.seen == [], "the runner was reached without a verified claim"
    assert len(git.active_commits()) == 1, "something beat a claim that was refused"


def test_a_claim_verified_to_another_host_beats_nothing(tmp_path, armed):
    """The push landed but the remote names someone else — `CAUSE_NOT_OURS`."""
    git = RecordingGit(remote_holder=OTHER)
    got, _calls, git, runner = run_drain(tmp_path, git=git)

    assert got.ok is False and got.stage == D.CLAIM_REFUSED
    assert runner.seen == []
    assert len(git.active_commits()) == 1


def test_a_dry_run_beats_nothing(tmp_path, disarmed):
    """A dry run reaches no write primitive at all — the beater is one."""
    got, calls, git, _runner = run_drain(tmp_path, apply=False)

    assert got.dry_run is True
    assert calls == [] and git.commits == []
    assert list(tmp_path.iterdir()) == []


# ==========================================================================
# E — R4: the ceiling is lifted BY the mechanism, not instead of it
# ==========================================================================


def test_without_a_beater_a_timeout_beyond_the_ttl_is_still_refused(tmp_path, armed):
    """R4, preserved verbatim in its own terms. With `--no-heartbeat` nothing
    refreshes `heartbeat_at`, so the original coupling is exactly as fatal as it
    was and is refused before anything is claimed or run."""
    got, calls, _git, runner = run_drain(tmp_path, timeout=90 * 60, ttl_minutes=90,
                                         heartbeat=False)

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []
    assert not records.record_path(tmp_path, ISSUE).exists()


def test_with_a_beater_a_payload_may_outlive_its_ttl(tmp_path, armed):
    """The lift. A four-hour solver run under a 90-minute TTL is the binding
    case, and it is now safe because the record is refreshed while it runs."""
    got, _calls, git, runner = run_drain(tmp_path, timeout=4 * 60 * 60,
                                         ttl_minutes=90)

    assert got.ok is True and got.stage == D.RELEASED
    assert len(runner.seen) == 1
    assert len(git.active_commits()) >= 2, "the ceiling was lifted without a beater"


def test_a_runner_whose_own_timeout_outlives_the_ttl_is_allowed_when_beating(
        tmp_path, armed):
    """The runner is what actually waits. R4 caught it because nothing beat;
    with a beater it is the same safe case as our own timeout."""
    git = RecordingGit()
    runner = BeatingRunner(git)
    runner.timeout = 99 * 60

    got, _calls, git, runner = run_drain(tmp_path, git=git, runner=runner,
                                         ttl_minutes=90)

    assert got.ok is True and len(runner.seen) == 1


def test_a_runner_whose_own_timeout_outlives_the_ttl_is_still_refused_unbeaten(
        tmp_path, armed):
    """Discriminator: the relaxation is conditional on the mechanism, not on the
    field it is checking."""
    git = RecordingGit()
    runner = BeatingRunner(git)
    runner.timeout = 99 * 60

    got, calls, _g, _r = run_drain(tmp_path, git=git, runner=runner,
                                   ttl_minutes=90, heartbeat=False)

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == []


def test_a_ttl_too_short_for_its_own_beat_interval_is_refused(tmp_path, armed):
    """The rail that replaces R4 when beating is on. A TTL the beater cannot keep
    ahead of is the SAME defect wearing the fix's clothes — the record expires
    under a live job — and it must be refused, not beaten at."""
    got, calls, _git, runner = run_drain(tmp_path, ttl_minutes=1, timeout=30,
                                         beat_interval=None)

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []
    assert not records.record_path(tmp_path, ISSUE).exists()


def test_an_operator_supplied_interval_is_railed_by_the_same_rule(tmp_path, armed):
    """`--beat-interval` is a dial, not a bypass. An interval longer than the TTL
    it is protecting refuses whatever the derived default would have been."""
    got, calls, _git, runner = run_drain(tmp_path, ttl_minutes=90,
                                         beat_interval=90 * 60)

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []


def test_the_refusal_still_does_not_need_the_write_gate_to_fire(tmp_path, disarmed):
    """An operator learns about the misconfiguration from the PLAN, not from the
    first unattended double-execution."""
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=ExplodingGit(), runner=None, now=clock(),
                  ttl_minutes=1, timeout=30, rules_loader=caps(**{OURS: 1}))

    assert got.ok is False and got.stage == D.REFUSED


def test_the_beaters_deadline_outlives_the_longest_permitted_wait():
    """A beater that stopped first would expire the record under a payload the
    drain is still legitimately waiting for — R4's own defect, reintroduced by
    the fix. Bounded, though: the grace is finite, so a wedged drain still
    releases the issue."""
    assert D.beat_deadline_seconds(4 * 60 * 60) > 4 * 60 * 60
    assert D.beat_deadline_seconds(0) > 0
    assert D.beat_deadline_seconds(100) - 100 == D.beat_deadline_seconds(200) - 200


def test_the_shipped_defaults_still_satisfy_the_unbeaten_rule():
    """`--no-heartbeat` must remain a usable configuration, not a trap."""
    assert D.DEFAULT_TIMEOUT_SECONDS < records.DEFAULT_TTL_MINUTES * 60


def test_the_cli_exposes_both_the_switch_and_the_dial(tmp_path, armed, capsys):
    """A rail reachable only from Python is not reachable by the operator who
    runs the fleet."""
    rc = D.main(["--issue", ISSUE, "--records", str(tmp_path), "--command", "true",
                 "--timeout", "5400", "--ttl-minutes", "90", "--no-heartbeat"])
    capsys.readouterr()
    assert rc != 0
    assert list(tmp_path.iterdir()) == []

    rc = D.main(["--issue", ISSUE, "--records", str(tmp_path), "--command", "true",
                 "--ttl-minutes", "1", "--timeout", "30"])
    capsys.readouterr()
    assert rc != 0
    assert list(tmp_path.iterdir()) == []


# ==========================================================================
# F — the beat against a REAL repository
#
# Every test above drives a git double, which proves the protocol and proves
# nothing about the commit. That gap matters more for a beat than for anything
# else in this module: the beater fires repeatedly, on a thread, in a checkout
# several dispatch lanes and an auto-sync process are all writing to.
# ==========================================================================


def _git(repo, *args):
    import subprocess
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


class NoPushBackend(claim.GitBackend):
    """The real commit path; the push stubbed, because there is no remote."""

    def push(self):
        return True


def test_a_real_beat_commits_only_the_record_and_sweeps_no_other_lane(tmp_path):
    """`git commit -a` every interval, for hours, across every concurrent lane,
    would publish other people's half-finished work on a schedule. The claim
    commit is pathspec-scoped for this reason and the beat — which fires far more
    often — must be too."""
    repo = _init(tmp_path)
    records_dir = repo / "records"
    rec = held_claim(records_dir)

    other_lane = repo / "seed.txt"
    other_lane.write_text("another lane is mid-edit\n", encoding="utf-8")
    staged = repo / "staged.txt"
    staged.write_text("staged by another lane\n", encoding="utf-8")
    _git(repo, "add", "staged.txt")
    untracked = repo / "scratch.txt"
    untracked.write_text("untracked work in progress\n", encoding="utf-8")

    got = claim.beat(records_dir, rec,
                     git=NoPushBackend(repo, records_dir=records_dir, branch="main"))

    assert got.landed is True
    touched = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r",
                   "HEAD").stdout.split()
    assert touched == ["records/vamseeachanta-digitalmodel#1885.json"], \
        f"the beat commit swept {touched}"

    # And the other lane's three kinds of work are exactly as they were.
    assert other_lane.read_text(encoding="utf-8") == "another lane is mid-edit\n"
    assert untracked.read_text(encoding="utf-8") == "untracked work in progress\n"
    assert "staged.txt" in _git(repo, "diff", "--cached", "--name-only").stdout


def test_a_real_beat_commits_the_advanced_heartbeat(tmp_path):
    """Discriminator: a commit that touches the right path and carries the OLD
    bytes is the defect this fixes, committed."""
    repo = _init(tmp_path)
    records_dir = repo / "records"
    rec = held_claim(records_dir)
    rel = "records/vamseeachanta-digitalmodel#1885.json"

    claim.beat(records_dir, rec,
               git=NoPushBackend(repo, records_dir=records_dir, branch="main"))

    committed = json.loads(_git(repo, "show", f"HEAD:{rel}").stdout)
    assert beat_of(committed) > beat_of(rec)
    assert committed["state"] == "active"
    assert committed["host"] == rec["host"] and committed["job_id"] == rec["job_id"]


# ==========================================================================
# G — the interaction with liveness that the beat exists to serve
# ==========================================================================


def test_a_beaten_record_is_not_expired_by_the_rule_that_reclaims_it(tmp_path):
    """The end-to-end property, stated in the vocabulary that actually decides:
    `records.is_expired` is what `reconcile.settle` consults, so a beat is only
    worth anything if it moves THAT answer."""
    rec = held_claim(tmp_path)
    later = NOW + timedelta(minutes=100)

    assert records.is_expired(on_disk(tmp_path), now=clock(later)) is True

    claim.beat(tmp_path, rec, git=RecordingGit())

    assert records.is_expired(on_disk(tmp_path), now=clock(later)) is False
