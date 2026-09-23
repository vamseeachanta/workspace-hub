#!/usr/bin/env python3
"""Label reconciliation — one direction, dry by default. workspace-hub#3740 slice 3.

867 issues sit at `dispatch:ready` because nothing ever wrote a later state.
Slice 1 made the record authoritative, slice 2 made claiming it safe; this slice
recomputes each `dispatch:` label FROM the record and writes only the difference.

## The four properties these tests defend

1. **One direction.** Records project onto labels. A label never becomes a
   record. Adopting the 867 existing `dispatch:ready` labels as claims would look
   like instant progress and would invent 867 runs that never happened, so the
   tests assert not just "no state was inferred" but that the records directory
   is byte-for-byte untouched by a label-only input.

2. **Drift is a finding.** The GitHub UI is what humans read and believe. A label
   saying `ready` over a record saying `done` has already told someone something
   false. Correcting it silently repairs the data and destroys the evidence that
   the projection failed — so drift is reported first, and reported **even when
   writes are disabled**. A dry run that hides drift reads as confirmation, which
   is this epic's recurring failure: absence of signal mistaken for success.

3. **Bounded retries.** An expired heartbeat returns to `ready` — unless attempts
   are exhausted, in which case it stops at `blocked` carrying its history. An
   unbounded retry loop looks like resilience and hides a job that can never
   succeed.

4. **A future heartbeat is skew, never expiry.** Hosts do not share a clock.
   Treating a fast clock as expiry requeues live work, and the symptom presents
   as random job loss — the hardest kind of bug to attribute.

Hermetic: injected clock, tmp_path records, no gh, no git, no network. Every
write primitive is booby-trapped in the dry-run tests, so reaching one fails
loudly rather than silently succeeding against a real repo.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/test_reconcile.py -q
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RECONCILE_PY = REPO_ROOT / "scripts" / "dispatch" / "reconcile.py"


def _load():
    pkg = str(RECONCILE_PY.parent)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location("dispatch_reconcile", RECONCILE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dispatch_reconcile"] = mod
    spec.loader.exec_module(mod)
    return mod


RC = _load()
# Reach records/route THROUGH reconcile. Loading them separately would create a
# second module instance whose RecordSchemaError is a different class, and the
# resulting `pytest.raises` mismatch would be blamed on the code under test.
R = RC.records
ROUTE = RC.route

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
ISSUE = "vamseeachanta/digitalmodel#1885"
OTHER = "vamseeachanta/workspace-hub#3740"
FLAG = RC.APPLY_FLAG


def _clock(dt=NOW):
    return lambda: dt


@pytest.fixture(autouse=True)
def _no_flag(monkeypatch):
    """Default state for every test: writes are UNARMED.

    The gate must fail closed, so the unset case is the one that has to hold in
    every test, not only in the tests that are about the gate.
    """
    monkeypatch.delenv(FLAG, raising=False)


def _boom(*a, **k):
    raise AssertionError("a write primitive was reached through a closed gate")


@pytest.fixture
def trapped(monkeypatch):
    """Booby-trap everything that can mutate a live issue or a record."""
    monkeypatch.setattr(ROUTE, "gh", _boom, raising=False)
    monkeypatch.setattr(ROUTE, "ensure_labels", _boom, raising=False)
    monkeypatch.setattr(ROUTE, "fetch_open_issues", _boom, raising=False)
    monkeypatch.setattr(R, "write_record", _boom, raising=False)


class FakeGh:
    """Records every `gh` invocation so the ARGUMENTS and ORDER can be asserted."""

    def __init__(self, returncode=0, stderr=""):
        self.returncode = returncode
        self.stderr = stderr
        self.calls: list[list[str]] = []

    def __call__(self, args, **kw):
        self.calls.append(list(args))
        return subprocess.CompletedProcess(args=args, returncode=self.returncode,
                                           stdout="", stderr=self.stderr)


def _claim(issue=ISSUE, **kw):
    kw.setdefault("machine", "dev-primary")
    kw.setdefault("host", "ace-linux-1")
    kw.setdefault("job_id", "j1")
    kw.setdefault("now", _clock())
    return R.new_claim(issue, **kw)


def _write(root, record):
    path = R.record_path(root, record["issue"])
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# one direction: records -> labels, never the reverse
# --------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["ready", "active", "done", "blocked"])
def test_the_label_is_computed_from_the_record_state(state):
    rec = dict(_claim(), state=state)
    assert RC.intended_label(rec) == f"dispatch:{state}"


def test_every_lifecycle_state_has_a_label_to_project_into():
    """A state with no label is a card that silently vanishes from every board."""
    assert set(RC.LABEL_FOR_STATE) == set(R.STATES)


def test_a_label_with_no_record_is_reported_never_adopted(tmp_path, trapped):
    """The 867-issue temptation.

    Adopting existing `dispatch:ready` labels as claims would look like instant
    progress. It would also fabricate 867 runs that never happened, and §4 would
    then join completion evidence onto nothing.
    """
    report = RC.reconcile(tmp_path, {OTHER: {"dispatch:ready", "machine:m"}},
                          now=_clock())
    assert report.outcomes == [], "a label must not produce a reconcilable item"
    orphans = report.of_kind(RC.ORPHAN_LABEL)
    assert [f.issue for f in orphans] == [OTHER]


def test_reconciling_label_only_input_leaves_the_records_directory_untouched(tmp_path):
    """Stronger than 'no state was inferred': nothing was written at all."""
    before = sorted(p.name for p in tmp_path.iterdir())
    RC.reconcile(tmp_path, {OTHER: {"dispatch:active"}}, now=_clock())
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_a_non_dispatch_label_on_an_unknown_issue_is_not_a_finding(tmp_path):
    """Only the `dispatch:` axis is this module's business.

    Reporting every unmanaged issue would bury the orphan signal under noise
    from every issue in the repo.
    """
    report = RC.reconcile(tmp_path, {OTHER: {"machine:m", "domain:x"}}, now=_clock())
    assert report.of_kind(RC.ORPHAN_LABEL) == []


# --------------------------------------------------------------------------
# drift is a finding, not a silent fix
# --------------------------------------------------------------------------


def _done(root, issue=ISSUE):
    rec = R.transition(_claim(issue), "done", reason="completed", returncode=0,
                       now=_clock())
    _write(root, rec)
    return rec


def test_drift_is_reported_with_BOTH_sides_named(tmp_path, trapped):
    """"Drift detected" is useless; the reader needs to know which side is wrong."""
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    drift = report.of_kind(RC.DRIFT)
    assert len(drift) == 1
    assert "ready" in drift[0].detail and "done" in drift[0].detail


def test_drift_is_reported_even_when_writes_are_disabled(tmp_path, trapped, capsys):
    """The property that makes the dry run worth running.

    A reconciler that only surfaces drift once someone has armed writes surfaces
    it at the exact moment it is being erased.
    """
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    print(RC.format_report(report, armed=False))
    out = capsys.readouterr().out
    assert RC.DRIFT.upper() in out
    assert ISSUE in out


def test_drift_is_corrected_toward_the_record_not_away_from_it(tmp_path):
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    outcome = report.outcomes[0]
    assert outcome.add == ("dispatch:done",)
    assert outcome.remove == ("dispatch:ready",)


def test_an_issue_with_no_dispatch_label_is_its_own_class(tmp_path):
    """Missing is not drift: nobody was told anything false, they were told nothing.

    Different remedy, different urgency — collapsing them would hide the case
    where the UI actively misled someone.
    """
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"machine:m"}}, now=_clock())
    assert report.counts()[RC.LABEL_MISSING] == 1
    assert report.counts()[RC.DRIFT] == 0
    assert report.outcomes[0].add == ("dispatch:done",)


def test_an_agreeing_label_produces_no_write(tmp_path):
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:done"}}, now=_clock())
    assert report.outcomes[0].writes_labels is False
    assert report.counts()[RC.IN_SYNC] == 1


# --------------------------------------------------------------------------
# stale-active: revert once, then stop
# --------------------------------------------------------------------------


def _stale(root, ttl=30, attempt=1, max_attempts=3, issue=ISSUE):
    rec = _claim(issue, ttl_minutes=ttl, max_attempts=max_attempts)
    rec["attempt"] = attempt
    _write(root, rec)
    return rec


def test_an_expired_heartbeat_returns_to_ready(tmp_path):
    _stale(tmp_path, ttl=30)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(minutes=45)))
    outcome = report.outcomes[0]
    assert outcome.record["state"] == "ready"
    assert outcome.record["reason"] == "heartbeat expired"
    assert outcome.intended == "dispatch:ready"


def test_a_live_heartbeat_is_left_alone(tmp_path):
    _stale(tmp_path, ttl=90)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(minutes=30)))
    assert report.outcomes[0].record_changed is False
    assert report.counts()[RC.STALE_ACTIVE] == 0


def test_the_ttl_is_the_records_own_not_a_global_one(tmp_path):
    """A ~57-sim OrcaFlex batch is not a 20-second smoke test.

    One global TTL requeues legitimate long runs, which is worse than never
    expiring: it interrupts work that was fine.
    """
    _stale(tmp_path, ttl=600)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(hours=5)))
    assert report.outcomes[0].record["state"] == "active"


def test_an_exhausted_record_is_quarantined_rather_than_requeued(tmp_path):
    """The stop that makes the retry safe.

    Reverting forever is a loop nobody watches; it consumes a licence seat and
    reports as activity.
    """
    _stale(tmp_path, ttl=30, attempt=3, max_attempts=3)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(minutes=45)))
    outcome = report.outcomes[0]
    assert outcome.record["state"] == "blocked"
    assert outcome.intended == "dispatch:blocked"
    assert report.counts()[RC.QUARANTINED] == 1
    assert report.counts()[RC.STALE_ACTIVE] == 0


def test_quarantine_carries_the_attempt_history(tmp_path):
    """`blocked` with no history is a dead end nobody can debug.

    The next question is always "same failure on one host, or three different
    ones?" and only the attempt list answers it.
    """
    rec = _claim(ttl_minutes=30, max_attempts=2)
    rec = R.transition(rec, "ready", reason="heartbeat expired", now=_clock())
    rec = R.reclaim(rec, host="ace-linux-2", job_id="j2", now=_clock())
    _write(tmp_path, rec)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(minutes=45)))
    detail = report.of_kind(RC.QUARANTINED)[0].detail
    assert "ace-linux-1" in detail and "ace-linux-2" in detail
    assert len(report.outcomes[0].record["attempts"]) == 2


def test_a_terminal_record_is_never_re_settled(tmp_path):
    """Only a live claim can go stale.

    A `done` record older than any TTL must not be dragged back to ready — that
    would resurrect finished work every time the reconciler ran.
    """
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:done"}},
                          now=_clock(NOW + timedelta(days=30)))
    assert report.outcomes[0].record["state"] == "done"
    assert report.outcomes[0].record_changed is False


# --------------------------------------------------------------------------
# clock skew is reported, never acted on
# --------------------------------------------------------------------------


def _skewed(root, ahead=timedelta(hours=3)):
    rec = R.heartbeat(_claim(ttl_minutes=30), now=_clock(NOW + ahead))
    _write(root, rec)
    return rec


def test_a_future_heartbeat_is_skew_not_expiry(tmp_path):
    _skewed(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}}, now=_clock())
    assert report.counts()[RC.CLOCK_SKEW] == 1
    assert report.counts()[RC.STALE_ACTIVE] == 0
    assert report.outcomes[0].record["state"] == "active"


def test_skew_consumes_no_attempt_and_changes_no_record(tmp_path):
    """Acting on a fast clock is how live work disappears without a trace."""
    _skewed(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}}, now=_clock())
    outcome = report.outcomes[0]
    assert outcome.record_changed is False
    assert outcome.record["attempt"] == 1


def test_skew_still_projects_the_state_the_record_holds(tmp_path):
    """Held is not ignored — the label must still say what the record says."""
    _skewed(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    assert report.outcomes[0].add == ("dispatch:active",)


def test_a_heartbeat_barely_ahead_is_ordinary_drift_not_a_finding(tmp_path):
    """Hosts are never perfectly synchronised; flagging 20s would flag everything."""
    _skewed(tmp_path, ahead=timedelta(seconds=20))
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}}, now=_clock())
    assert report.counts()[RC.CLOCK_SKEW] == 0


# --------------------------------------------------------------------------
# the dispatch: axis stays single-valued
# --------------------------------------------------------------------------


def test_the_cardinality_guard_is_route_s_own_not_a_second_copy():
    """Two copies of the rule drift, and then disagree about what a legal write is."""
    assert RC.assert_write_preserves_cardinality is ROUTE.assert_write_preserves_cardinality


def test_two_dispatch_labels_collapse_to_exactly_one(tmp_path):
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready", "dispatch:active"}},
                          now=_clock())
    outcome = report.outcomes[0]
    merged = (set(outcome.current) - set(outcome.remove)) | set(outcome.add)
    assert merged == {"dispatch:done"}
    assert report.counts()[RC.LABEL_AMBIGUOUS] == 1


def test_a_write_leaving_two_values_is_refused_at_the_boundary(monkeypatch, tmp_path):
    """The guard must be WIRED, not merely defined.

    A hand-built outcome that would add a second `dispatch:` value has to raise
    BEFORE `gh` is called — a check that runs in a report afterwards is a report,
    not a control.
    """
    monkeypatch.setenv(FLAG, "1")
    gh = FakeGh()
    bad = RC.Outcome(issue=ISSUE, current=("dispatch:ready",),
                     intended="dispatch:done", add=("dispatch:done",), remove=())
    report = RC.Report(outcomes=[bad], findings=[], records_root=tmp_path)
    with pytest.raises(ROUTE.AmbiguousAxis):
        RC.apply(report, tmp_path, gh_fn=gh)
    assert gh.calls == [], "the guard ran after the write"


# --------------------------------------------------------------------------
# dry run by default
# --------------------------------------------------------------------------


def test_reconcile_reaches_no_write_primitive(tmp_path, trapped):
    """The read path must be provably read-only, not merely intended to be."""
    _done(tmp_path)
    _stale(tmp_path, issue=OTHER, ttl=30)
    RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}},
                 now=_clock(NOW + timedelta(hours=2)))


def test_apply_is_refused_when_the_flag_is_unset(tmp_path, trapped):
    with pytest.raises(SystemExit) as exc:
        RC.apply(RC.Report(outcomes=[], findings=[]), tmp_path, gh_fn=_boom)
    assert FLAG in str(exc.value), "the error must name the flag, or nobody can fix it"


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "maybe", "true-ish", " ", ""])
def test_any_non_affirmative_value_fails_closed(monkeypatch, value):
    """A naive `if os.environ.get(FLAG)` treats "0" and "false" as permission.

    That is worse than no gate, because it reads as protected.
    """
    monkeypatch.setenv(FLAG, value)
    with pytest.raises(SystemExit):
        RC.assert_write_allowed()


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_an_explicit_affirmative_opens_the_gate(monkeypatch, value):
    monkeypatch.setenv(FLAG, value)
    RC.assert_write_allowed()


def test_both_gates_agree_on_what_counts_as_armed():
    """One flag, one meaning.

    If reconcile accepted a value route rejected (or the reverse), each gate
    would look correct in isolation while the pair let a write through.
    """
    assert RC.APPLY_FLAG == ROUTE.APPLY_FLAG
    assert set(RC.AFFIRMATIVE) == set(ROUTE._AFFIRMATIVE)


# --------------------------------------------------------------------------
# the write path itself
# --------------------------------------------------------------------------


def test_apply_edits_the_repo_the_record_names(monkeypatch, tmp_path):
    """The record is fully qualified so a write needs no ambient repo.

    Run from the wrong checkout, an ambient-repo reconciler would edit another
    repository's issue of the same number.
    """
    monkeypatch.setenv(FLAG, "1")
    _done(tmp_path)
    gh = FakeGh()
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    RC.apply(report, tmp_path, gh_fn=gh)
    args = gh.calls[0]
    assert args[:2] == ["issue", "edit"]
    assert "1885" in args and "vamseeachanta/digitalmodel" in args
    assert "--add-label" in args and "--remove-label" in args


def test_a_malformed_issue_key_refuses_rather_than_guessing_a_repo():
    with pytest.raises(ValueError):
        RC.split_issue("1885")


def test_apply_writes_the_record_before_the_label(monkeypatch, tmp_path):
    """Order is the whole safety argument.

    Label-then-record leaves, on failure, a label advertising a state no record
    supports — manufacturing exactly the drift this module exists to remove.
    Record-then-label leaves the state correct and the next pass re-projects it.
    """
    monkeypatch.setenv(FLAG, "1")
    _stale(tmp_path, ttl=30)
    order: list[str] = []
    real_write = R.write_record
    monkeypatch.setattr(R, "write_record",
                        lambda root, rec: (order.append("record"), real_write(root, rec))[1])

    class Recording(FakeGh):
        def __call__(self, args, **kw):
            order.append("label")
            return super().__call__(args, **kw)

    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:active"}},
                          now=_clock(NOW + timedelta(minutes=45)))
    RC.apply(report, tmp_path, gh_fn=Recording())
    assert order == ["record", "label"]
    assert R.read_record(R.record_path(tmp_path, ISSUE))["state"] == "ready"


def test_apply_skips_issues_that_need_nothing(monkeypatch, tmp_path):
    """Idempotence, and the reason the pass is cheap enough to run often."""
    monkeypatch.setenv(FLAG, "1")
    _done(tmp_path)
    gh = FakeGh()
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:done"}}, now=_clock())
    stats = RC.apply(report, tmp_path, gh_fn=gh)
    assert gh.calls == []
    assert stats["noop"] == 1 and stats["labels_written"] == 0


def test_a_failed_gh_edit_is_counted_not_swallowed(monkeypatch, tmp_path):
    """A silent failure here recreates the original defect one layer up.

    The record would say `done` while GitHub kept showing `ready`, and the next
    pass would report drift it had itself failed to fix.
    """
    monkeypatch.setenv(FLAG, "1")
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    stats = RC.apply(report, tmp_path, gh_fn=FakeGh(returncode=1, stderr="rate limit"))
    assert stats["errors"] == 1 and stats["labels_written"] == 0


# --------------------------------------------------------------------------
# every no-op class reports itself
# --------------------------------------------------------------------------


def test_a_pass_that_changed_nothing_still_reports_every_class(tmp_path):
    """A reconciler that prints nothing when it changed nothing is
    indistinguishable from one that failed to run.

    The report walks the DECLARED class table, not the findings it happened to
    collect, so a class can never go missing by having a count of zero.
    """
    text = RC.format_report(RC.reconcile(tmp_path, {}, now=_clock()))
    for kind, _ in RC.FINDING_KINDS:
        assert kind in text, f"class {kind} vanished from the report"
    assert "0 label write(s)" in text


def test_the_report_states_whether_writes_are_armed(tmp_path):
    """Otherwise "planned: 3 writes" is ambiguous about whether they happened."""
    report = RC.reconcile(tmp_path, {}, now=_clock())
    assert FLAG in RC.format_report(report, armed=False)
    assert "ARMED" in RC.format_report(report, armed=True)


def test_in_sync_issues_are_counted_not_dropped(tmp_path):
    """"Nothing to report" and "12 checked, all correct" are different claims."""
    _done(tmp_path)
    _write(tmp_path, R.transition(_claim(OTHER), "done", reason="c", returncode=0,
                                  now=_clock()))
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:done"},
                                     OTHER: {"dispatch:done"}}, now=_clock())
    assert report.counts()[RC.IN_SYNC] == 2


# --------------------------------------------------------------------------
# a bad record stops itself, not the pass
# --------------------------------------------------------------------------


def test_an_unparseable_record_is_reported_and_the_pass_continues(tmp_path):
    """One corrupt file must not strand the other 866.

    That pressure is exactly how a check gets disabled outright; route.py's
    per-card fail-closed takes the same line for the same reason.
    """
    (tmp_path / "broken.json").write_text("{ not json", encoding="utf-8")
    _done(tmp_path)
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    assert report.counts()[RC.UNREADABLE] == 1
    assert [o.issue for o in report.outcomes] == [ISSUE]


def test_a_record_from_a_future_writer_is_reported_not_projected(tmp_path):
    """Refusing beats guessing.

    Projecting a label from a half-understood record publishes a state this
    version invented.
    """
    _write(tmp_path, dict(_done(tmp_path), schema=999))
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}}, now=_clock())
    assert report.counts()[RC.UNREADABLE] == 1
    assert report.outcomes == []


# --------------------------------------------------------------------------
# adapters and CLI
# --------------------------------------------------------------------------


def test_fetch_labels_keys_issues_the_way_records_do():
    """A bare issue number cannot be joined to a record; the pairing would silently
    produce zero matches and the pass would report a clean 0."""
    got = RC.fetch_labels("owner/name", fetch=lambda repo: {"7": {"dispatch:ready"}})
    assert got == {"owner/name#7": {"dispatch:ready"}}


def test_an_api_failure_refuses_rather_than_returning_an_empty_snapshot():
    """`fetch_open_issues` returns None on rate-limit.

    Read as "no labels anywhere", that would propose adding a dispatch: label to
    every issue in the repo — a mass write born from an outage.
    """
    with pytest.raises(RuntimeError):
        RC.fetch_labels("owner/name", fetch=lambda repo: None)


def test_the_cli_dry_run_prints_drift_and_never_calls_gh(tmp_path, trapped, capsys):
    """End to end through argument parsing, which is where a gate gets bypassed."""
    _done(tmp_path)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({ISSUE: ["dispatch:ready"]}), encoding="utf-8")
    rc = RC.main(["--records", str(tmp_path), "--labels-json", str(labels)])
    out = capsys.readouterr().out
    assert rc == 0
    assert RC.DRIFT.upper() in out
    assert "1 label write(s)" in out


def test_the_cli_refuses_to_apply_without_the_flag(tmp_path, trapped, capsys):
    """`--apply` is not authorisation; the env var is."""
    _done(tmp_path)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({ISSUE: ["dispatch:ready"]}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        RC.main(["--records", str(tmp_path), "--labels-json", str(labels), "--apply"])
    assert FLAG in str(exc.value)
    assert RC.DRIFT.upper() in capsys.readouterr().out, (
        "the report must be printed before the gate refuses — drift surfaced only "
        "to an operator who already armed writes is surfaced too late")


# --------------------------------------------------------------------------
# the table's OTHER direction
# --------------------------------------------------------------------------


def test_an_undeclared_finding_kind_is_refused_at_emission():
    """The zero-count guarantee has an inverse, and it was the unguarded one.

    `format_report` walks FINDING_KINDS, so a declared class always prints even
    at zero. But `counts()` tallies ANY kind, so a kind emitted and never added
    to the table is counted and never shown — a complete-looking report with a
    whole class of finding invisible. Found by mutation: adding an undeclared
    Finding left all 56 tests green.
    """
    with pytest.raises(ValueError) as exc:
        RC.Finding("a-kind-nobody-declared", ISSUE, "invisible")
    assert "FINDING_KINDS" in str(exc.value), (
        "the error must name the table, or the fix is a guess")


def test_every_declared_kind_can_still_be_constructed():
    """The guard must not be so tight that the module cannot emit its own classes."""
    for kind, _ in RC.FINDING_KINDS:
        RC.Finding(kind, ISSUE, "detail")


def test_the_report_never_claims_armed_when_the_gate_is_shut(tmp_path, monkeypatch, capsys):
    """Asking for writes is not the same as being permitted them.

    Found by LIVE smoke, not by this suite: `main` passed `armed=args.apply`, so
    `--apply` without the env flag printed "WRITES ARMED (DISPATCH_APPLY_ENABLED
    is set)" on the line before refusing because it was not set. The sentence was
    true of the parameter it was handed and false about the system.

    The existing armed/unarmed test called `format_report` DIRECTLY, so the
    formatter was correct and the wiring was never exercised — which is exactly
    why it survived.
    """
    monkeypatch.delenv(FLAG, raising=False)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({}))
    with pytest.raises(SystemExit):
        RC.main(["--records", str(tmp_path), "--labels-json", str(labels), "--apply"])
    out = capsys.readouterr().out
    assert "ARMED" not in out, "the report claimed writes were armed while the gate was shut"
    assert "dry run" in out


def test_the_report_says_armed_when_it_genuinely_is(tmp_path, monkeypatch, capsys):
    """The inverse must still hold, or the fix is just a muted message."""
    monkeypatch.setenv(FLAG, "1")
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({}))
    RC.main(["--records", str(tmp_path), "--labels-json", str(labels), "--apply"])
    assert "ARMED" in capsys.readouterr().out


# --------------------------------------------------------------------------
# the vocabulary: created explicitly, separately, and never by a reconcile pass
#
# `dispatch:ready` is the only one of the four that exists on the live repo. The
# other three land with the WRITER — records.py says why: a vocabulary created
# ahead of a writer turns every WALL in chain.py into a clean-looking `0` while
# nothing writes them, so presence of vocabulary reads as capability.
# --------------------------------------------------------------------------


class FakeLabelGh:
    """A `gh` that answers `label list` and records every `label create`.

    Same injection point `apply` uses. Nothing here touches the network, and a
    call this class does not recognise raises rather than returning a plausible
    success — an unrecognised command answered with returncode 0 would let a
    changed call shape pass unnoticed.
    """

    def __init__(self, existing=(), list_rc=0, list_stdout=None,
                 create_rc=0, create_stderr=""):
        self.existing = list(existing)
        self.list_rc = list_rc
        self.list_stdout = list_stdout
        self.create_rc = create_rc
        self.create_stderr = create_stderr
        self.calls: list[list[str]] = []

    @property
    def creates(self) -> list[list[str]]:
        return [c for c in self.calls if c[:2] == ["label", "create"]]

    def __call__(self, args, **kw):
        self.calls.append(list(args))
        if args[:2] == ["label", "list"]:
            stdout = (json.dumps([{"name": n} for n in self.existing])
                      if self.list_stdout is None else self.list_stdout)
            return subprocess.CompletedProcess(args=args, returncode=self.list_rc,
                                               stdout=stdout, stderr="")
        if args[:2] == ["label", "create"]:
            return subprocess.CompletedProcess(args=args, returncode=self.create_rc,
                                               stdout="", stderr=self.create_stderr)
        raise AssertionError(f"unexpected gh call: {args}")


ALL_STATE_LABELS = tuple(f"dispatch:{s}" for s in ["ready", "active", "done", "blocked"])


def _created_names(gh) -> list[str]:
    return [c[2] for c in gh.creates]


def test_the_labels_created_are_the_ones_the_lifecycle_implies(monkeypatch, tmp_path):
    """Only `dispatch:ready` exists today; the other three are why this exists."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=["dispatch:ready", "domain:marine"])
    result = RC.ensure_labels("owner/name", gh_fn=gh)
    assert set(_created_names(gh)) == {"dispatch:active", "dispatch:done",
                                       "dispatch:blocked"}
    assert set(result["created"]) == {"dispatch:active", "dispatch:done",
                                      "dispatch:blocked"}
    assert result["present"] == ("dispatch:ready",)
    assert "domain:marine" not in _created_names(gh), "it creates dispatch: only"


def test_the_set_is_derived_from_records_STATES_not_a_typed_out_list(monkeypatch):
    """A second hand-maintained list is a second source of truth, and it drifts.

    Adding a state to the lifecycle with no style entry must REFUSE here. A
    hardcoded four-name list would create its four and notice nothing, leaving
    the reconciler projecting into a label nothing ever made — which surfaces
    later as a per-issue `gh issue edit` failure and gets blamed on GitHub.
    """
    monkeypatch.setenv(FLAG, "1")
    monkeypatch.setattr(R, "STATES", tuple(R.STATES) + ("paused",))
    gh = FakeLabelGh(existing=[])
    with pytest.raises(ValueError) as exc:
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert "paused" in str(exc.value), "the error must name the state, or it is a hunt"
    assert gh.creates == [], "it created a partial vocabulary before refusing"


def test_every_lifecycle_state_has_a_style_to_be_created_with():
    """The other direction of the same guarantee: no state is left unpaintable."""
    labels = [name for name, _, _ in RC.label_specs()]
    assert labels == [RC.LABEL_FOR_STATE[s] for s in R.STATES]
    assert set(labels) == set(ALL_STATE_LABELS)


def test_creating_a_label_that_already_exists_is_a_no_op(monkeypatch):
    """Re-running must be safe, and must not report work it did not do."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=list(ALL_STATE_LABELS))
    result = RC.ensure_labels("owner/name", gh_fn=gh)
    assert gh.creates == [], "it tried to re-create labels that were already there"
    assert result["created"] == ()
    assert set(result["present"]) == set(ALL_STATE_LABELS)
    assert result["failed"] == ()


def test_running_it_twice_creates_nothing_the_second_time(monkeypatch):
    """Idempotence end to end, against a repo that remembers the first run."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=["dispatch:ready"])
    first = RC.ensure_labels("owner/name", gh_fn=gh)
    gh.existing += list(first["created"])
    second = RC.ensure_labels("owner/name", gh_fn=gh)
    assert len(first["created"]) == 3
    assert second["created"] == ()
    assert set(second["present"]) == set(ALL_STATE_LABELS)


def test_a_label_won_by_a_racing_operator_is_present_not_failed(monkeypatch):
    """Two people arm the same command a second apart; that is not a failure.

    The list read and the create are not atomic, so `gh` answering "already
    exists" is the normal outcome of a race. Counting it as an error sends
    someone looking for a problem that does not exist — and teaches operators
    that a non-zero exit from this command can be ignored.
    """
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[], create_rc=1,
                     create_stderr='HTTP 422: Label "dispatch:done" already exists')
    result = RC.ensure_labels("owner/name", gh_fn=gh)
    assert result["created"] == ()
    assert set(result["present"]) == set(ALL_STATE_LABELS)
    assert result["failed"] == ()


def test_a_real_creation_failure_is_reported_not_absorbed(monkeypatch):
    """"Already exists" is the ONLY non-zero exit that means success.

    Absorbing the rest would report a vocabulary that is not there, and the next
    reconcile pass would fail per issue on a label nobody created.
    """
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[], create_rc=1, create_stderr="HTTP 403: Forbidden")
    result = RC.ensure_labels("owner/name", gh_fn=gh)
    assert result["created"] == () and result["present"] == ()
    assert [name for name, _ in result["failed"]] == list(ALL_STATE_LABELS)
    assert "403" in result["failed"][0][1], "the reason must survive to the operator"


def test_created_and_already_present_are_reported_as_different_facts(monkeypatch):
    """"created 0" and "all four were already there" are not the same claim.

    Conflated into one "4 labels ok", a run pointed at the wrong repo — or one
    that created nothing because the gate silently did nothing — reads exactly
    like a successful first run.
    """
    monkeypatch.setenv(FLAG, "1")
    fresh = RC.format_label_creation(
        RC.ensure_labels("owner/name", gh_fn=FakeLabelGh(existing=[])))
    rerun = RC.format_label_creation(
        RC.ensure_labels("owner/name", gh_fn=FakeLabelGh(existing=list(ALL_STATE_LABELS))))
    assert "created 4" in fresh and "already present 0" in fresh
    assert "created 0" in rerun and "already present 4" in rerun
    assert fresh != rerun, "the two runs are indistinguishable in the report"
    for name in ALL_STATE_LABELS:
        assert f"CREATED  {name}" in fresh
        assert f"PRESENT  {name}" in rerun


# --------------------------------------------------------------------------
# creation is a mutation of a public repo, so it is behind the SAME gate
# --------------------------------------------------------------------------


def test_ensure_labels_is_refused_when_the_flag_is_unset(tmp_path, trapped):
    """A creation path with its own gate — or none — is how the one control
    everybody reasons about stops covering what they assume it covers."""
    gh = FakeLabelGh(existing=[])
    with pytest.raises(SystemExit) as exc:
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert FLAG in str(exc.value), "the error must name the flag, or nobody can fix it"
    assert gh.calls == [], "the gate ran after reaching gh"


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "", " "])
def test_ensure_labels_fails_closed_on_a_non_affirmative_value(monkeypatch, value):
    """A truthiness check would read "0" and "false" as permission to write."""
    monkeypatch.setenv(FLAG, value)
    gh = FakeLabelGh(existing=[])
    with pytest.raises(SystemExit):
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert gh.calls == []


def test_an_unreadable_label_list_refuses_rather_than_creating_everything(monkeypatch):
    """route.existing_labels returns {} on failure; here that is an outage
    reported as four freshly created labels."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[], list_rc=1)
    with pytest.raises(RuntimeError):
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert gh.creates == []


def test_unparseable_label_output_is_not_read_as_no_labels(monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[], list_stdout="not json at all")
    with pytest.raises(RuntimeError):
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert gh.creates == []


def test_a_possibly_truncated_label_page_refuses(monkeypatch):
    """A label past the page limit reads as absent, and the run would report
    creating something that was already there."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[f"filler-{i}" for i in range(500)])
    with pytest.raises(RuntimeError):
        RC.ensure_labels("owner/name", gh_fn=gh)
    assert gh.creates == []


def test_an_existing_definition_is_never_overwritten(monkeypatch):
    """No --force. An existing label's colour and description may follow a
    convention this module does not know about — and 867 issues already carry
    `dispatch:ready`."""
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[])
    RC.ensure_labels("owner/name", gh_fn=gh)
    for call in gh.creates:
        assert "--force" not in call
        assert "--color" in call and "--description" in call
        assert "--repo" in call and "owner/name" in call


def test_each_label_describes_what_the_STATE_means(monkeypatch):
    """A description of `done` that says "done" is noise in a tooltip.

    route.py's generic convention would render exactly that — "Dispatch: done" —
    and `done` is the one that misleads, because it means ran-to-completion, not
    succeeded. The description must carry information the name does not.
    """
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=[])
    RC.ensure_labels("owner/name", gh_fn=gh)
    seen = {}
    for call in gh.creates:
        seen[call[2]] = (call[call.index("--color") + 1],
                         call[call.index("--description") + 1])
    assert set(seen) | {"dispatch:ready"} == set(ALL_STATE_LABELS)
    for name, (colour, description) in seen.items():
        state = name.split(":", 1)[1]
        words = description.lower().replace(",", " ").split()
        assert len(words) > 4, f"{name}: a description that short cannot say much"
        assert description.lower() not in {state, name, f"dispatch: {state}"}, (
            f"{name}: the description only repeats the label's own name")
        assert len(description) <= RC.MAX_DESCRIPTION, (
            f"{name}: GitHub truncates past {RC.MAX_DESCRIPTION} chars")
        assert len(colour) == 6 and int(colour, 16) >= 0
    colours = {c for c, _ in seen.values()}
    assert len(colours) == len(seen), "two states painted the same colour"


# --------------------------------------------------------------------------
# and the constraint that governs the whole slice: nothing automatic
# --------------------------------------------------------------------------


def test_a_normal_reconcile_and_apply_run_creates_no_labels(monkeypatch, tmp_path):
    """Labels land LAST, with the writer.

    records.py states the reason: created earlier, they turn every WALL in
    chain.py into a clean-looking `0` while nothing writes them — presence of
    vocabulary reading as capability. So even an ARMED apply must not touch the
    label vocabulary, only the issues' membership of it.
    """
    monkeypatch.setenv(FLAG, "1")
    monkeypatch.setattr(RC, "ensure_labels", _boom)
    monkeypatch.setattr(RC, "existing_labels", _boom)
    _done(tmp_path)
    _stale(tmp_path, issue=OTHER, ttl=30)
    gh = FakeGh()
    report = RC.reconcile(tmp_path, {ISSUE: {"dispatch:ready"}},
                          now=_clock(NOW + timedelta(hours=2)))
    RC.apply(report, tmp_path, gh_fn=gh)
    assert gh.calls, "the test proves nothing if the write path did not run"
    for call in gh.calls:
        assert call[0] != "label", f"a reconcile pass created vocabulary: {call}"


def test_the_dry_run_cli_creates_no_labels(tmp_path, trapped, monkeypatch, capsys):
    monkeypatch.setattr(RC, "ensure_labels", _boom)
    _done(tmp_path)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({ISSUE: ["dispatch:ready"]}), encoding="utf-8")
    assert RC.main(["--records", str(tmp_path), "--labels-json", str(labels)]) == 0
    assert "CREATED" not in capsys.readouterr().out


def test_the_live_repo_cli_path_creates_no_labels(tmp_path, monkeypatch, capsys):
    """`--repo` names a repository, which is the one input creation would need.

    That makes it the tempting place to "helpfully" ensure the vocabulary on the
    way past — and it is the same ordering error, arriving through the argument
    the operator supplied for a read.
    """
    monkeypatch.setattr(RC, "ensure_labels", _boom)
    monkeypatch.setattr(RC, "existing_labels", _boom)
    monkeypatch.setattr(ROUTE, "fetch_open_issues",
                        lambda repo: {"1885": {"dispatch:ready"}}, raising=False)
    _done(tmp_path)
    assert RC.main(["--records", str(tmp_path),
                    "--repo", "vamseeachanta/digitalmodel"]) == 0
    out = capsys.readouterr().out
    assert RC.DRIFT.upper() in out, "the read path itself must still have run"
    assert "CREATED" not in out


def test_the_cli_refuses_to_ensure_labels_during_a_reconcile_run(tmp_path, monkeypatch):
    """Standalone by construction, not by convention.

    A combined invocation would eventually be run for its side effect, and the
    vocabulary would appear ahead of the writer — the exact ordering records.py
    warns about.
    """
    monkeypatch.setenv(FLAG, "1")
    monkeypatch.setattr(RC, "ensure_labels", _boom)
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        RC.main(["--records", str(tmp_path), "--labels-json", str(labels),
                 "--ensure-labels", "owner/name"])
    assert exc.value.code == 2


def test_the_cli_ensure_labels_path_is_gated_too(monkeypatch, capsys):
    monkeypatch.delenv(FLAG, raising=False)
    monkeypatch.setattr(ROUTE, "gh", _boom, raising=False)
    with pytest.raises(SystemExit) as exc:
        RC.main(["--ensure-labels", "owner/name"])
    assert FLAG in str(exc.value)


def test_the_cli_ensure_labels_path_reports_what_it_did(monkeypatch, capsys):
    monkeypatch.setenv(FLAG, "1")
    gh = FakeLabelGh(existing=["dispatch:ready"])
    monkeypatch.setattr(ROUTE, "gh", gh, raising=False)
    assert RC.main(["--ensure-labels", "owner/name"]) == 0
    out = capsys.readouterr().out
    assert "created 3" in out and "already present 1" in out
    assert "CREATED  dispatch:done" in out


def test_reconcile_without_a_records_directory_still_refuses(tmp_path):
    """Relaxing `--records` for the standalone path must not make it optional."""
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        RC.main(["--labels-json", str(labels)])
    assert exc.value.code == 2
