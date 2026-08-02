#!/usr/bin/env python3
"""The five rails that let `drain.py` run UNATTENDED. workspace-hub#3773.

`test_drain.py` proves the loop closes for one card driven by a human. This
file proves the loop can be left alone over 1344 of them. Each rail closes a
defect that an adversarial audit found would corrupt the record or lose control
of the box, and each is asserted as a PROPERTY of the outcome — a state on disk,
a runner that was or was not reached, an argv that was or was not issued — never
as the wording of a message. A test that greps for a sentence pins the sentence.

R1  WIP cap        a direct drain ignored `wip_caps` entirely, so N sessions on
                   one machine could all claim at once. `dispatch.py` says "WIP
                   is enforced at claim time by the consuming session"; nothing
                   enforced it.
R2  kill switch    there was no way to stop the loop short of `kill`, and
                   `run.sh` detaches payloads so they outlive the session.
R3  timeout kills  `subprocess.run(timeout=)` kills the CHILD. `run.sh` and the
                   payload are grandchildren: they kept running, orphaned, while
                   the record said the outcome was unknown.
R4  ttl coupling   nothing refreshes `heartbeat_at` while a job runs, so a job
                   outliving `ttl_minutes` gets settled back to `ready` and
                   RECLAIMed — two payloads, one issue. Until an out-of-band
                   beater exists the coupling must be refused, not left to the
                   coincidence that 3600s < 90min.
R5  quarantine     a thrice-failed card kept its `done`/`returncode 3` record,
                   projected `dispatch:done`, and was counted as executed. The
                   refusal wrote NOTHING, so nothing downstream could see it.

Hermetic: git, the runner and the routing rules are injected. No network, no
`gh`, no push, no real subprocess.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/test_drain_unattended.py -q
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DRAIN_PY = REPO_ROOT / "scripts" / "dispatch" / "drain.py"
RUN_SH = REPO_ROOT / "scripts" / "dispatch" / "run.sh"


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
    monkeypatch.setenv(D.APPLY_FLAG, "1")


@pytest.fixture
def disarmed(monkeypatch):
    monkeypatch.delenv(D.APPLY_FLAG, raising=False)


# --------------------------------------------------------------------------
# doubles — same shape as test_drain.py's, sharing one call list so ORDER is
# observable and "it refused" can be told from "it refused after executing".
# --------------------------------------------------------------------------


class FakeGit:
    def __init__(self, calls=None, push_ok=True, remote_holder=OURS):
        self.calls = calls if calls is not None else []
        self.push_ok = push_ok
        self.remote_holder = remote_holder
        self.last_written: dict | None = None

    def commit(self, path, message):
        self.calls.append("commit")
        self.last_written = json.loads(Path(path).read_text(encoding="utf-8"))
        return True

    def push(self):
        self.calls.append("push")
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
    def __init__(self, calls=None, returncode=0, cancelled=None):
        self.calls = calls if calls is not None else []
        self.returncode = returncode
        self.cancelled = cancelled
        self.seen: list[dict] = []

    def describe(self, **kw):
        return "fake-runner"

    def execute(self, *, issue, job_id, command, work_dir=None):
        self.calls.append("execute")
        self.seen.append({"issue": issue, "job_id": job_id, "command": command})
        return D.ExecOutcome(self.returncode, job_state="finished",
                             detail="", cancelled=self.cancelled)


class Exploding:
    def __getattr__(self, name):
        def boom(*a, **kw):
            raise AssertionError(f"this path reached {name}() — it must not")
        return boom


def wired(**kw):
    calls: list[str] = []
    git = FakeGit(calls=calls, **{k: v for k, v in kw.items()
                                  if k in ("push_ok", "remote_holder")})
    runner = FakeRunner(calls=calls, **{k: v for k, v in kw.items()
                                        if k in ("returncode", "cancelled")})
    return calls, git, runner


def caps(**per_machine):
    """A routing-rules loader carrying just the WIP caps, for hermeticity."""
    per_machine.setdefault("default", 1)
    return lambda: {"wip_caps": {"per_machine": dict(per_machine)}}


def run_drain(tmp_path, calls_git_runner=None, **kw):
    calls, git, runner = calls_git_runner or wired()
    params = dict(command="echo pilot", host=OURS, job_id="j1", git=git,
                  runner=runner, apply=True, now=clock(),
                  rules_loader=caps(**{OURS: 1}))
    params.update(kw)
    return D.drain(tmp_path, ISSUE, **params), calls, git, runner


def on_disk(tmp_path, issue=ISSUE):
    return records.read_record(records.record_path(tmp_path, issue))


def active_claim(tmp_path, issue, *, machine=OURS, host=OURS):
    records.write_record(tmp_path, records.new_claim(
        issue, machine=machine, host=host, job_id=f"job-{issue[-3:]}", now=clock()))


def finished(tmp_path, *, issue=ISSUE, attempt=1, max_attempts=3, returncode=3):
    rec = records.new_claim(issue, machine=OURS, host=OURS, job_id="j0",
                            max_attempts=max_attempts, now=clock())
    rec["attempt"] = attempt
    records.write_record(tmp_path, records.transition(
        rec, "done", reason="completed", returncode=returncode, now=clock()))


# ==========================================================================
# R1 — the WIP cap is enforced where the claim is decided
# ==========================================================================


def test_a_machine_already_at_its_wip_cap_claims_nothing_more(tmp_path, armed):
    """The 260-worker scar: `route.py` only ANNOTATES a proposal with a slot.
    A drain invoked directly never saw it, so the cap bounded nothing."""
    active_claim(tmp_path, "vamseeachanta/digitalmodel#101")
    active_claim(tmp_path, "vamseeachanta/digitalmodel#102")

    got, calls, _git, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 2}))

    assert got.ok is False and got.stage == D.REFUSED
    assert runner.seen == [] and calls == [], "over the cap, nothing may be claimed"
    assert not records.record_path(tmp_path, ISSUE).exists(), \
        "a refused claim must leave no record behind"


def test_below_the_cap_the_claim_still_proceeds(tmp_path, armed):
    """Discriminator: a cap that refuses everything would pass the test above."""
    active_claim(tmp_path, "vamseeachanta/digitalmodel#101")

    got, _calls, _git, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 2}))

    assert got.ok is True and got.stage == D.RELEASED
    assert len(runner.seen) == 1


def test_another_machines_claims_do_not_consume_our_cap(tmp_path, armed):
    """The cap is per-machine. Counting the fleet would idle every host."""
    active_claim(tmp_path, "vamseeachanta/digitalmodel#101", machine=OTHER, host=OTHER)
    active_claim(tmp_path, "vamseeachanta/digitalmodel#102", machine=OTHER, host=OTHER)

    got, _c, _g, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 1}))

    assert got.ok is True and len(runner.seen) == 1


def test_terminal_records_do_not_consume_the_cap(tmp_path, armed):
    """WIP is work IN PROGRESS. Counting finished cards would wedge the machine
    permanently after `cap` successful drains."""
    finished(tmp_path, issue="vamseeachanta/digitalmodel#101", returncode=0)
    finished(tmp_path, issue="vamseeachanta/digitalmodel#102", returncode=0)

    got, _c, _g, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 1}))

    assert got.ok is True and len(runner.seen) == 1


def test_a_reclaim_is_capped_too_not_only_a_first_claim(tmp_path, armed):
    """RECLAIM starts a payload exactly as CLAIM does; exempting it would leave
    the cap enforced on the path that happens least."""
    finished(tmp_path)                                     # our target: reclaimable
    active_claim(tmp_path, "vamseeachanta/digitalmodel#101")

    got, calls, _g, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 1}))

    assert got.ok is False and got.stage == D.REFUSED
    assert runner.seen == [] and calls == []
    assert on_disk(tmp_path)["state"] == "done", "the refused record is untouched"


def test_re_entering_our_own_claim_is_not_a_new_slot(tmp_path, armed):
    """A RESUME occupies the slot it already holds. Counting it against the cap
    would make an operator's re-run after a dropped SSH session impossible."""
    active_claim(tmp_path, ISSUE)

    got, _c, _g, runner = run_drain(tmp_path, job_id="job-885",
                                    rules_loader=caps(**{OURS: 1}))

    assert got.ok is True and got.action == D.RESUME
    assert len(runner.seen) == 1


def test_unreadable_routing_rules_fail_closed(tmp_path, armed):
    """No cap read is not "no cap"."""
    def broken():
        raise OSError("routing-rules.yaml is gone")

    got, calls, _g, runner = run_drain(tmp_path, rules_loader=broken)

    assert got.ok is False and got.stage == D.REFUSED
    assert runner.seen == [] and calls == []
    assert not records.record_path(tmp_path, ISSUE).exists()


@pytest.mark.parametrize("cfg", [
    {},                                             # no wip_caps at all
    {"wip_caps": {}},                               # no per_machine
    {"wip_caps": {"per_machine": {}}},              # empty mapping
    {"wip_caps": {"per_machine": {"other": 4}}},    # no entry AND no default
    {"wip_caps": {"per_machine": {"default": "lots"}}},   # unparseable
    {"wip_caps": {"per_machine": {"default": -1}}},       # nonsense
])
def test_a_config_that_names_no_usable_cap_fails_closed(tmp_path, armed, cfg):
    got, calls, _g, runner = run_drain(tmp_path, rules_loader=lambda: cfg)

    assert got.ok is False and got.stage == D.REFUSED
    assert runner.seen == [] and calls == []


def test_an_unreadable_record_counts_against_the_cap(tmp_path, armed):
    """It may be a live claim of ours. Skipping what we cannot read would make
    corruption look like idle capacity."""
    junk = tmp_path / "junk.json"
    junk.write_text("{not json", encoding="utf-8")

    got, _c, _g, runner = run_drain(tmp_path, rules_loader=caps(**{OURS: 1}))

    assert got.ok is False and runner.seen == []


def test_the_cap_is_read_from_the_routing_rules_not_from_this_module(tmp_path):
    """The value lives in `.claude/memory/kanban/routing-rules.yaml`, the same
    file `route.apply_wip` and `dispatch.py --capacity` read. A second copy in
    drain.py would drift, and both would look correct in isolation."""
    rules = D.load_routing_rules()
    per_machine = (rules.get("wip_caps") or {}).get("per_machine") or {}

    assert per_machine, "wip_caps.per_machine is where the cap lives"
    assert isinstance(per_machine.get("default"), int), \
        "an unlisted machine must still resolve to a number, or every host fails closed"
    for machine, cap in per_machine.items():
        assert D.machine_wip_cap(machine) == int(cap)
    assert D.machine_wip_cap("a-machine-that-is-not-in-the-roster") == \
        int(per_machine["default"])


# ==========================================================================
# R2 — the kill switch
# ==========================================================================


def pause(root) -> Path:
    path = D.pause_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("stop\n", encoding="utf-8")
    return path


def test_a_pause_sentinel_stops_the_drain_before_it_claims(tmp_path, armed):
    pause(tmp_path)

    got, calls, _g, runner = run_drain(tmp_path)

    assert got.stage == D.PAUSED
    assert calls == [], "the sentinel must gate the CLAIM, not just the payload"
    assert runner.seen == []
    assert not records.record_path(tmp_path, ISSUE).exists()


def test_without_the_sentinel_the_same_drain_runs(tmp_path, armed):
    """Discriminator: an unconditional refusal would pass the test above."""
    got, _c, _g, runner = run_drain(tmp_path)
    assert got.ok is True and len(runner.seen) == 1


def test_the_sentinel_is_consulted_on_every_drain_not_at_loop_start(tmp_path, armed):
    """`run.sh` uses `setsid nohup`, so a wrapper loop already running is exactly
    the case the switch exists for: work NOT YET CLAIMED must stop."""
    first, _c, _g, runner1 = run_drain(tmp_path)
    assert first.ok is True

    pause(tmp_path)
    second, calls2, _g2, runner2 = run_drain(tmp_path, job_id="j2")

    assert second.stage == D.PAUSED
    assert runner2.seen == [] and calls2 == []


def test_a_pause_is_reported_distinctly_from_a_failure(tmp_path, armed):
    """An operator's stop must not read as a broken card in the exit code — a
    wrapper loop that cannot tell them apart either spins or gives up wrongly."""
    roots = {}
    for name in ("paused", "refused", "failed"):
        roots[name] = tmp_path / name
        roots[name].mkdir()
    pause(roots["paused"])

    paused, _c, _g, _r = run_drain(roots["paused"])
    refused, _c2, _g2, _r2 = run_drain(roots["refused"],
                                       calls_git_runner=wired(push_ok=False))
    failed, _c3, _g3, _r3 = run_drain(roots["failed"],
                                      calls_git_runner=wired(returncode=3))

    assert paused.stage not in (D.REFUSED, D.CLAIM_REFUSED, D.RELEASE_FAILED,
                                D.RELEASED, D.PLANNED)
    codes = {D.exit_code(paused), D.exit_code(refused), D.exit_code(failed)}
    assert len(codes) == 3, "paused, refused and failed must be distinguishable"
    assert D.exit_code(paused) != 0, "a paused drain did no work"


def test_the_sentinel_lives_where_the_operator_can_reach_it(tmp_path):
    """A path only this module knows is not a kill switch."""
    assert D.pause_path(tmp_path) == tmp_path / ".claude" / "dispatch" / "PAUSE"
    assert D.pause_path(tmp_path).parent == D.pause_path(tmp_path).parent


def test_a_dry_run_is_not_stopped_by_the_sentinel(tmp_path, disarmed):
    """A plan writes nothing and runs nothing; refusing it would make the switch
    look broken to the operator checking what would happen."""
    pause(tmp_path)
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock(),
                  rules_loader=caps(**{OURS: 1}))
    assert got.stage == D.PLANNED


# ==========================================================================
# R3 — a timeout that actually kills
# ==========================================================================


def fake_subprocess(script):
    """A `subprocess` shim for drain's namespace. `script` is a list of stdout
    strings or exceptions, consumed in call order; argv is recorded."""
    seen: list[list[str]] = []

    def run(argv, **kw):
        seen.append(list(argv))
        item = script.pop(0) if script else "{}"
        if isinstance(item, BaseException):
            raise item
        return types.SimpleNamespace(stdout=item, stderr="", returncode=0)

    shim = types.SimpleNamespace(run=run,
                                 TimeoutExpired=subprocess.TimeoutExpired,
                                 SubprocessError=subprocess.SubprocessError)
    return seen, shim


def shell_runner(**kw):
    kw.setdefault("timeout", 10)
    kw.setdefault("sleep", lambda _s: None)
    return D.ShellRunner(script="/x/run.sh", **kw)


def ticking(values):
    it = iter(values)
    last = [values[-1]]

    def tick():
        try:
            last[0] = next(it)
        except StopIteration:
            pass
        return last[0]
    return tick


def test_a_submit_that_never_returns_cancels_the_job(tmp_path, monkeypatch):
    """`--foreground` means the submit call IS the payload. Killing our child
    leaves `run.sh` and the payload — its grandchildren — running."""
    timeout = subprocess.TimeoutExpired(cmd=["bash"], timeout=10)
    seen, shim = fake_subprocess([timeout, '{"ok":true,"action":"cancel"}'])
    monkeypatch.setattr(D, "subprocess", shim)

    outcome = shell_runner().execute(issue=ISSUE, job_id="j1", command="sleep 1d")

    assert outcome.returncode is None, "a timeout is not an exit code"
    assert outcome.cancelled is True
    assert seen[-1] == ["bash", "/x/run.sh", "cancel", "--job-id", "j1"]


def test_a_poll_that_runs_past_the_deadline_cancels_the_job(tmp_path, monkeypatch):
    seen, shim = fake_subprocess(['{"ok":true}', '{"state":"running"}',
                                  '{"ok":true,"action":"cancel"}'])
    monkeypatch.setattr(D, "subprocess", shim)

    outcome = shell_runner(clock=ticking([0, 999])).execute(
        issue=ISSUE, job_id="j1", command="sleep 1d")

    assert outcome.returncode is None and outcome.job_state == "running"
    assert outcome.cancelled is True
    assert ["bash", "/x/run.sh", "cancel", "--job-id", "j1"] in seen


def test_a_job_that_finished_is_never_cancelled(tmp_path, monkeypatch):
    """Discriminator: cancelling unconditionally would pass the two above and
    would SIGTERM every completed payload's successor."""
    seen, shim = fake_subprocess(['{"ok":true}', '{"state":"finished","exit_code":0}'])
    monkeypatch.setattr(D, "subprocess", shim)

    outcome = shell_runner(clock=ticking([0, 1])).execute(
        issue=ISSUE, job_id="j1", command="true")

    assert outcome.returncode == 0 and outcome.cancelled is None
    assert not any("cancel" in argv for argv in seen)


def test_a_cancel_that_did_not_work_is_visible_not_swallowed(tmp_path, monkeypatch):
    """A payload we could neither observe nor stop is the worst state this loop
    can reach: it holds the one solver seat and nothing knows."""
    timeout = subprocess.TimeoutExpired(cmd=["bash"], timeout=10)
    seen, shim = fake_subprocess([timeout, '{"ok":false,"error":"no such job"}'])
    monkeypatch.setattr(D, "subprocess", shim)

    outcome = shell_runner().execute(issue=ISSUE, job_id="j1", command="sleep 1d")

    assert outcome.cancelled is False, "attempted-and-failed is not the same as never-tried"
    assert outcome.returncode is None


def test_a_cancel_that_itself_hangs_is_reported_as_failed(tmp_path, monkeypatch):
    timeouts = [subprocess.TimeoutExpired(cmd=["bash"], timeout=10),
                subprocess.TimeoutExpired(cmd=["bash"], timeout=60)]
    seen, shim = fake_subprocess(timeouts)
    monkeypatch.setattr(D, "subprocess", shim)

    outcome = shell_runner().execute(issue=ISSUE, job_id="j1", command="sleep 1d")

    assert outcome.cancelled is False


def test_an_uncancelled_job_reaches_the_drains_warnings(tmp_path, armed):
    """The record says `blocked`/`unknown-outcome` either way. Whether a payload
    is STILL RUNNING is a different fact and the operator needs it."""
    got, _c, _g, _r = run_drain(
        tmp_path, calls_git_runner=wired(returncode=None, cancelled=False))

    assert got.record["state"] == "blocked"
    assert got.warnings, "a payload that could not be stopped must be surfaced"

    clean, _c2, _g2, _r2 = run_drain(
        tmp_path, job_id="j2",
        calls_git_runner=wired(returncode=None, cancelled=True))
    assert clean.warnings == [], "a confirmed cancel is not a warning"


def test_the_cancel_verb_exists_in_the_real_runner(tmp_path):
    """The argv above is worthless if `run.sh` does not answer to it — the exact
    class of defect that shipped a Windows runner path pointing at nothing."""
    text = RUN_SH.read_text(encoding="utf-8")
    assert "cmd_cancel" in text and "cancel)" in text
    assert D.ShellRunner(script="/x/run.sh").cancel_argv("j1") == \
        ["bash", "/x/run.sh", "cancel", "--job-id", "j1"]
    wargv = D.PowerShellRunner(script="C:/x/dispatch-run.ps1").cancel_argv("j1")
    assert "-Action" in wargv and "cancel" in wargv and "j1" in wargv


# ==========================================================================
# R4 — a timeout that outlives the TTL double-executes
# ==========================================================================


def test_a_timeout_at_or_beyond_the_ttl_is_refused_before_anything_runs(
        tmp_path, armed):
    """Nothing beats `heartbeat_at` while the child runs, so a job that outlives
    its TTL is settled back to `ready` and RECLAIMed WHILE IT IS STILL RUNNING."""
    got, calls, _g, runner = run_drain(tmp_path, timeout=90 * 60, ttl_minutes=90)

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []
    assert not records.record_path(tmp_path, ISSUE).exists()


def test_a_timeout_inside_the_ttl_is_allowed(tmp_path, armed):
    """Discriminator."""
    got, _c, _g, runner = run_drain(tmp_path, timeout=90 * 60 - 1, ttl_minutes=90)
    assert got.ok is True and len(runner.seen) == 1


def test_the_refusal_does_not_need_the_write_gate_to_fire(tmp_path, disarmed):
    """An operator learns about the misconfiguration from the PLAN, not from the
    first unattended double-execution."""
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock(),
                  timeout=5400, ttl_minutes=90, rules_loader=caps(**{OURS: 1}))
    assert got.ok is False and got.stage == D.REFUSED


def test_a_runner_carrying_its_own_oversized_timeout_is_caught(tmp_path, armed):
    """The runner is what actually waits. A drain told a safe number while its
    runner holds an unsafe one is the coupling wearing a disguise."""
    runner = D.ShellRunner(script="/x/run.sh", timeout=99 * 60)
    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=runner, apply=True, now=clock(),
                  ttl_minutes=90, rules_loader=caps(**{OURS: 1}))

    assert got.ok is False and got.stage == D.REFUSED
    assert not records.record_path(tmp_path, ISSUE).exists()


def test_the_shipped_defaults_satisfy_their_own_rule(tmp_path):
    """Today's 3600s vs 90min is a coincidence that MASKS the defect. Pin it so
    raising either default without the other fails here, not in production."""
    assert D.DEFAULT_TIMEOUT_SECONDS < records.DEFAULT_TTL_MINUTES * 60


def test_the_cli_refuses_the_same_coupling(tmp_path, armed, capsys):
    rc = D.main(["--issue", ISSUE, "--records", str(tmp_path), "--command", "true",
                 "--timeout", "5400", "--ttl-minutes", "90"])
    capsys.readouterr()
    assert rc != 0
    assert list(tmp_path.iterdir()) == []


# ==========================================================================
# R5 — a thrice-failed card must not look like a successful one
# ==========================================================================


def exhausted(tmp_path):
    """A card that has used every attempt and ended `done` with a nonzero code."""
    finished(tmp_path, attempt=3, max_attempts=3, returncode=3)


def test_attempt_exhaustion_writes_a_terminal_blocked_record(tmp_path, armed):
    """`should_quarantine` tripped and the drain wrote NOTHING, so the record
    stayed `done`/`returncode 3` — indistinguishable from a card that worked."""
    exhausted(tmp_path)

    got, calls, _g, runner = run_drain(tmp_path)

    rec = on_disk(tmp_path)
    assert rec["state"] == "blocked" and rec["state"] in records.TERMINAL
    assert rec["returncode"] == 3, "the observed exit code is not erased"
    assert records.is_success(rec) is False
    assert runner.seen == [], "quarantine records the card, it does not run it"
    assert "push" in calls, "a record nobody else can see is not a quarantine"


def test_the_quarantined_card_stops_projecting_dispatch_done(tmp_path, armed):
    """`chain.py` counts `dispatch:done` as executed. This is the whole defect."""
    exhausted(tmp_path)
    before = reconcile.intended_label(on_disk(tmp_path))

    got, _c, _g, _r = run_drain(tmp_path)

    assert before == "dispatch:done"
    assert got.intended_label == reconcile.intended_label(on_disk(tmp_path))
    assert got.intended_label != "dispatch:done"


def test_a_quarantined_card_is_distinguishable_from_a_successful_one(tmp_path, armed):
    """The property, stated directly: same drain, two cards, two states."""
    good = tmp_path / "good"
    bad = tmp_path / "bad"
    good.mkdir()
    bad.mkdir()
    exhausted(bad)

    ok_result, _c, _g, _r = run_drain(good)
    bad_result, _c2, _g2, _r2 = run_drain(bad)

    assert on_disk(good)["state"] != on_disk(bad)["state"]
    assert ok_result.work_succeeded is True and bad_result.work_succeeded is False
    assert reconcile.intended_label(on_disk(good)) != \
        reconcile.intended_label(on_disk(bad))


def test_the_quarantine_carries_why_it_stopped(tmp_path, armed):
    exhausted(tmp_path)
    got, _c, _g, _r = run_drain(tmp_path)

    rec = on_disk(tmp_path)
    assert rec["failure_category"] == D.ATTEMPTS_EXHAUSTED
    assert rec["attempt"] >= rec["max_attempts"]
    assert rec["attempts"][-1]["outcome"], "the attempt log records its own end"


def test_an_already_quarantined_card_is_not_re_written(tmp_path, armed):
    """Idempotence. Re-pushing a blocked record on every pass of an unattended
    loop is 1344 commits a day saying nothing new."""
    exhausted(tmp_path)
    run_drain(tmp_path)
    before = records.record_path(tmp_path, ISSUE).read_bytes()

    got, calls, _g, runner = run_drain(tmp_path, job_id="j2")

    assert got.ok is False and got.stage == D.REFUSED
    assert calls == [] and runner.seen == []
    assert records.record_path(tmp_path, ISSUE).read_bytes() == before


def test_a_dry_run_quarantines_nothing(tmp_path, disarmed):
    exhausted(tmp_path)
    before = records.record_path(tmp_path, ISSUE).read_bytes()

    got = D.drain(tmp_path, ISSUE, command="echo pilot", host=OURS, job_id="j1",
                  git=Exploding(), runner=Exploding(), now=clock(),
                  rules_loader=caps(**{OURS: 1}))

    assert got.ok is False
    assert records.record_path(tmp_path, ISSUE).read_bytes() == before


def test_a_quarantine_that_cannot_be_pushed_is_reported(tmp_path, armed):
    """Same contract as a release: locally-recorded is not recorded."""
    exhausted(tmp_path)

    got, _c, _g, runner = run_drain(tmp_path, calls_git_runner=wired(push_ok=False))

    assert got.ok is False and got.stage == D.RELEASE_FAILED
    assert runner.seen == []


def test_a_paused_loop_does_not_quarantine_either(tmp_path, armed):
    """The switch stops WRITES to the shared record store, not only payloads."""
    exhausted(tmp_path)
    pause(tmp_path)
    before = records.record_path(tmp_path, ISSUE).read_bytes()

    got, calls, _g, _r = run_drain(tmp_path)

    assert got.stage == D.PAUSED
    assert calls == []
    assert records.record_path(tmp_path, ISSUE).read_bytes() == before


def test_the_quarantine_category_is_pinned_to_its_literal_value():
    """A wire contract: operators read it and tooling joins on it. Comparing it
    only against the module's own constant would move with a rename."""
    assert D.ATTEMPTS_EXHAUSTED == "attempts-exhausted"
    vocabulary = {D.UNKNOWN_OUTCOME, D.PAYLOAD_ERROR, D.DISPATCH_ERROR,
                  D.CANCELLED, D.ATTEMPTS_EXHAUSTED}
    assert len(vocabulary) == 5, "two categories collapsed onto one string"


# ==========================================================================
# the guarantees these fixes must not have traded away
# ==========================================================================


def test_there_is_still_exactly_one_branch_that_may_execute(tmp_path, armed):
    """Every refusal added here must reach the runner zero times."""
    scenarios = {
        "over-cap": lambda p: active_claim(p, "vamseeachanta/digitalmodel#101"),
        "paused": pause,
        "quarantined": exhausted,
        "held-elsewhere": lambda p: active_claim(p, ISSUE, machine=OTHER, host=OTHER),
    }
    for name, setup in scenarios.items():
        root = tmp_path / name
        root.mkdir()
        setup(root)
        got, _c, _g, runner = run_drain(root, rules_loader=caps(**{OURS: 1}))
        assert runner.seen == [], f"{name} reached the runner"
        assert got.ok is False, f"{name} reported ok"


def test_an_unverified_claim_still_licenses_nothing(tmp_path, armed):
    got, calls, _g, runner = run_drain(
        tmp_path, calls_git_runner=wired(remote_holder=OTHER))
    assert got.stage == D.CLAIM_REFUSED and runner.seen == [] and "execute" not in calls


def test_an_unknown_returncode_is_still_never_coerced_to_success(tmp_path, armed):
    got, _c, _g, _r = run_drain(tmp_path, calls_git_runner=wired(returncode=None))
    rec = on_disk(tmp_path)
    assert rec["returncode"] is None and rec["state"] == "blocked"
    assert records.is_success(rec) is False and got.work_succeeded is False
