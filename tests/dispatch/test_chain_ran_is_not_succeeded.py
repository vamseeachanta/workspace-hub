#!/usr/bin/env python3
"""`ran` is not `succeeded`: the chain report must be able to tell them apart.

workspace-hub#3773 rail R5, reporting half.

## The defect

`records.py` separates two things on purpose:

    state: done      the payload RAN TO COMPLETION — not that it worked
    is_success       done AND returncode == 0 — whether it actually worked

`chain.py` never called `is_success`. A card that failed three times lands as
`done`, projects `dispatch:done`, and is counted in the `executed` stage. So:

    a night that fails every card produces a report identical to a night that
    completes every card.

That is the whole finding. It is about to run unattended over 1344 cards, and
`chain.py` is what a human reads in the morning.

## What these tests pin

Properties, never rendered strings. Each one fails when a card that did not
succeed is reported as if it did — not when the wording of the report changes.

The fix must hold the standard the rest of `chain.py` holds:

  * an ABSENCE must never read as a success — `--records` not given yields
    NOT-MEASURED counts, never `failed: 0`;
  * a COUNT must never stand in for evidence — every card needing attention is
    named, with its returncode, failure_category and attempt number;
  * silence stays evidence-backed — "we read 40 records and none failed" is a
    different report from "there are no records" is a different report from "we
    never looked".

Hermetic: record dicts in `tmp_path`. No gh, no network. `chain.py` is
read-only and takes a records directory, so nothing here needs a fixture the
real writer would not produce — and the pinning test below uses the real writer.

Run: uv run --with pyyaml --with pytest pytest tests/dispatch/ -q
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest  # noqa: F401  (tmp_path fixture; parity with the suite)

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAIN_PY = REPO_ROOT / "scripts" / "dispatch" / "chain.py"
RECORDS_PY = REPO_ROOT / "scripts" / "dispatch" / "records.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load("chain", CHAIN_PY)
R = _load("chain_test_records_r5", RECORDS_PY)

FULL_VOCAB = {"machine:dev-primary", "dispatch:ready", "dispatch:active", "dispatch:done"}


# --------------------------------------------------------------------------
# fixtures — plain record dicts, the shape records.py writes
# --------------------------------------------------------------------------


def _rec(issue, state, returncode=None, **kw):
    base = {"schema": 1, "issue": issue, "state": state, "returncode": returncode,
            "failure_category": None, "attempt": 1, "max_attempts": 3,
            "host": "ace-linux-1"}
    base.update(kw)
    return base


def _ok(issue="o/r#1"):
    return _rec(issue, "done", 0)


def _failed(issue="o/r#2", rc=3):
    return _rec(issue, "done", rc, failure_category="payload-error")


def _unattested(issue="o/r#3"):
    """`done` with no exit code. drain.py promises never to write this shape.

    Which is exactly why the reporter must handle it: the guarantee lives in
    another module, and a reporter that trusts it cannot detect its breach. A
    `done` that attests nothing is a measurement defect, not a success and not a
    clean failure.
    """
    return _rec(issue, "done", None)


def _quarantined(issue="o/r#4"):
    return _rec(issue, "blocked", None, failure_category="quarantine",
                attempt=3, max_attempts=3)


def _in_flight(issue="o/r#5"):
    return _rec(issue, "active", None)


def _write(root, records):
    root.mkdir(parents=True, exist_ok=True)
    for i, rec in enumerate(records):
        (root / f"rec-{i}.json").write_text(json.dumps(rec), encoding="utf-8")
    return root


# --------------------------------------------------------------------------
# THE HEADLINE
# --------------------------------------------------------------------------


def test_a_night_that_failed_every_card_does_not_report_like_one_that_worked():
    """The defect, stated as a test.

    Two nights, same 4 cards, same labels, same stages, same everything — the
    only difference is the exit code the payload returned. If the two reports
    compare equal, the morning read cannot distinguish total success from total
    failure, which is the entire finding.
    """
    worked = [_ok(f"o/r#{n}") for n in range(4)]
    failed = [_failed(f"o/r#{n}") for n in range(4)]

    good = C.outcome_report(worked)
    bad = C.outcome_report(failed)

    assert good != bad, "a failing night and a working night print the same report"
    assert not good["attention"], "nothing to investigate when every card exited 0"
    assert len(bad["attention"]) == 4, "every failed card must be named"
    assert bad["counts"][C.OUTCOME_SUCCEEDED] == 0


def test_the_stage_counts_alone_cannot_tell_the_two_nights_apart():
    """Why the outcome axis had to be added rather than folded into a stage.

    A failed-but-done card DID execute, so it belongs in `executed`. This test
    pins that the stage histogram is deliberately blind to success — which is
    what makes reporting the outcome separately load-bearing rather than
    decorative. If this ever starts failing, the outcome has leaked into the
    stage count and one number is answering two questions again.
    """
    executed = [{"labels": ["machine:dev-primary", "dispatch:done"]}] * 4
    stages = C.chain_report(executed, FULL_VOCAB, {"done"})["stages"]
    assert stages["executed"]["count"] == 4
    assert C.outcome_report([_failed(f"o/r#{n}") for n in range(4)])["attention"]


def test_success_is_delegated_to_records_is_success_not_reimplemented():
    """Equivalence with the authority, over the whole matrix that matters.

    A second definition of "worked" is how the two drift: `records.is_success`
    could gain a condition and this file would keep answering the old question.
    Asserted as agreement on every record, not as the presence of a call.
    """
    matrix = [
        _ok(), _failed(), _failed(rc=1), _failed(rc=137), _unattested(),
        _quarantined(), _in_flight(), _rec("o/r#9", "ready"),
        _rec("o/r#10", "blocked", 0),      # exited 0 then got quarantined
        _rec("o/r#11", "active", 0),       # a 0 from a run that is not finished
    ]
    for rec in matrix:
        agrees = C.outcome_of(rec) == C.OUTCOME_SUCCEEDED
        assert agrees is R.is_success(rec), rec


# --------------------------------------------------------------------------
# the buckets, and the three-way distinction inside "not a success"
# --------------------------------------------------------------------------


def test_done_with_a_nonzero_returncode_is_a_failure_not_a_completion():
    assert C.outcome_of(_failed()) == C.OUTCOME_FAILED


def test_done_with_no_returncode_is_unattested_and_is_neither_of_the_others():
    """The absence case. It is NOT a success, and it is NOT a clean failure.

    Reporting it as either invents a fact: nobody observed an exit code, so
    nobody knows. Folding it into `failed` would accuse a card that may have
    worked; folding it into `succeeded` is the defect this rail exists for.
    """
    got = C.outcome_of(_unattested())
    assert got == C.OUTCOME_UNATTESTED
    assert got != C.OUTCOME_SUCCEEDED
    assert got != C.OUTCOME_FAILED


def test_a_blocked_record_is_terminal_quarantine_not_work_still_in_flight():
    """`blocked` will never be retried. Reading it as in-flight hides a dead card.

    Attempt-exhaustion writing a real `blocked` record is landing separately;
    this asserts the reporter is already correct for the day it does, and today
    stays honest because nothing has written one yet.
    """
    assert C.outcome_of(_quarantined()) == C.OUTCOME_QUARANTINED
    assert C.OUTCOME_QUARANTINED in C.OUTCOMES_NEEDING_ATTENTION


def test_ready_and_active_records_have_no_outcome_yet():
    for rec in (_in_flight(), _rec("o/r#9", "ready")):
        assert C.outcome_of(rec) == C.OUTCOME_IN_FLIGHT
    assert C.OUTCOME_IN_FLIGHT not in C.OUTCOMES_NEEDING_ATTENTION


def test_a_state_the_reporter_does_not_recognise_is_never_silently_dropped():
    """A record that lands in no bucket is invisible, and invisible reads as fine.

    Same failure as an unchecked absence: the histogram would still sum to a
    tidy-looking number while a record nobody classified sat outside it.
    """
    rep = C.outcome_report([_ok(), _rec("o/r#77", "wat")])
    assert rep["records_read"] == 2
    assert sum(rep["counts"].values()) == 2
    assert C.outcome_of(_rec("o/r#77", "wat")) in C.OUTCOMES_NEEDING_ATTENTION


def test_every_record_lands_in_exactly_one_bucket():
    """A histogram that does not sum to the population is silently lossy."""
    population = [_ok(), _failed(), _unattested(), _quarantined(), _in_flight(),
                  _rec("o/r#9", "ready"), _rec("o/r#77", "wat")]
    rep = C.outcome_report(population)
    assert rep["records_read"] == len(population)
    assert sum(rep["counts"].values()) == len(population)


def test_the_attention_bucket_is_exactly_the_records_that_did_not_succeed():
    population = [_ok("o/r#1"), _failed("o/r#2"), _unattested("o/r#3"),
                  _quarantined("o/r#4"), _in_flight("o/r#5")]
    rep = C.outcome_report(population)
    assert {a["issue"] for a in rep["attention"]} == {"o/r#2", "o/r#3", "o/r#4"}
    assert len(rep["attention"]) == sum(
        rep["counts"][o] for o in C.OUTCOMES_NEEDING_ATTENTION)


# --------------------------------------------------------------------------
# a count must not stand in for evidence
# --------------------------------------------------------------------------


def test_each_flagged_card_carries_its_own_evidence_not_just_a_tally():
    """"4 failed" sends nobody anywhere. The returncode and category do.

    `attempt`/`max_attempts` is on it because "failed once of three" and "failed
    the last time it will ever be tried" are different mornings.
    """
    rep = C.outcome_report([_failed("o/r#2", rc=137), _quarantined("o/r#4")])
    by_issue = {a["issue"]: a for a in rep["attention"]}

    assert by_issue["o/r#2"]["returncode"] == 137
    assert by_issue["o/r#2"]["failure_category"] == "payload-error"
    assert by_issue["o/r#2"]["attempt"] == 1
    assert by_issue["o/r#2"]["max_attempts"] == 3
    assert by_issue["o/r#2"]["outcome"] == C.OUTCOME_FAILED

    assert by_issue["o/r#4"]["outcome"] == C.OUTCOME_QUARANTINED
    assert by_issue["o/r#4"]["attempt"] == 3


def test_a_flagged_card_with_no_issue_field_is_still_reported():
    """A malformed record must not be able to delete itself from the report.

    Dropping it would be an absence produced by the very corruption the entry
    is evidence of.
    """
    rep = C.outcome_report([{"schema": 1, "state": "done", "returncode": 3}])
    assert len(rep["attention"]) == 1
    assert rep["attention"][0]["issue"] is not None


# --------------------------------------------------------------------------
# an absence must never read as a success
# --------------------------------------------------------------------------


def test_records_not_consulted_reports_NOT_MEASURED_never_zero_failures():  # noqa: N802
    """The `result`/`published` discipline, applied to the new axis.

    `failed: 0` from a run that never looked at a record is the same lie as
    `published: 0` from an unbuilt join — and it is the more dangerous of the
    two, because zero failures is the answer everyone wants to see.
    """
    rep = C.outcome_report(None)
    assert rep["consulted"] is False
    assert rep["vocabulary"] == C.VOCAB_NOT_MEASURED
    assert rep["evidence"] == C.EV_NO_RECORDS
    assert rep["counts"] is None, "an unmeasured count must be absent, not 0"
    assert rep["attention"] is None
    assert rep["records_read"] is None


def test_we_looked_and_found_nothing_differs_from_we_never_looked():
    """Preserved from the stage half, on the outcome axis.

    An empty records root — a typo in `--records` produces one — must not print
    like a clean night. Both have zero failures; only one of them checked.
    """
    never_looked = C.outcome_report(None)
    looked = C.outcome_report([])

    assert looked["consulted"] is True
    assert looked["records_read"] == 0
    assert looked["evidence"] == C.EV_RECORDS_CONSULTED
    assert looked["vocabulary"] == C.VOCAB_NEVER_OBSERVED, \
        "no records at all is not a chain that has been exercised"
    assert never_looked["vocabulary"] != looked["vocabulary"]


def test_records_consulted_and_all_of_them_worked_is_its_own_verdict():
    """The one report that is allowed to read as good — and only with evidence."""
    rep = C.outcome_report([_ok("o/r#1"), _ok("o/r#2")])
    assert rep["vocabulary"] == C.VOCAB_PRESENT
    assert rep["evidence"] == C.EV_RECORDS_CONSULTED
    assert rep["records_read"] == 2
    assert rep["attention"] == []
    assert rep["counts"][C.OUTCOME_SUCCEEDED] == 2


def test_zero_successes_out_of_zero_records_is_not_a_clean_sheet():
    """`succeeded: 0` and `failed: 0` together must not print as a good night."""
    empty = C.outcome_report([])
    good = C.outcome_report([_ok()])
    assert empty["counts"][C.OUTCOME_SUCCEEDED] == 0
    assert empty["vocabulary"] != good["vocabulary"]


# --------------------------------------------------------------------------
# the vocabulary itself
# --------------------------------------------------------------------------


def test_no_outcome_is_spellable_as_a_synonym_of_success():
    """Collapsing two of these is the cheapest mutation that restores the defect."""
    names = [C.OUTCOME_SUCCEEDED, C.OUTCOME_FAILED, C.OUTCOME_UNATTESTED,
             C.OUTCOME_QUARANTINED, C.OUTCOME_IN_FLIGHT, C.OUTCOME_UNRECOGNISED]
    assert len(set(names)) == len(names)
    assert C.OUTCOME_SUCCEEDED not in C.OUTCOMES_NEEDING_ATTENTION
    assert set(C.OUTCOMES_NEEDING_ATTENTION) < set(names)


def test_in_flight_is_not_filed_as_a_failure():
    """A card still running is not a card that failed. Crying one trains the
    reader to ignore both — the same reason NEVER-OBSERVED is not a BREAK."""
    rep = C.outcome_report([_in_flight()])
    assert rep["attention"] == []
    assert rep["counts"][C.OUTCOME_IN_FLIGHT] == 1


# --------------------------------------------------------------------------
# reading the records root — READ-ONLY, and one bad file is not fatal
# --------------------------------------------------------------------------


def test_read_records_returns_the_records_under_a_root(tmp_path):
    root = _write(tmp_path / "records", [_ok("o/r#1"), _failed("o/r#2")])
    got = C.read_records(root)
    assert {r["issue"] for r in got} == {"o/r#1", "o/r#2"}


def test_a_missing_records_root_is_empty_and_is_NOT_created(tmp_path):  # noqa: N802
    """Read-only means the reporter does not materialise what it measures."""
    absent = tmp_path / "nope"
    assert C.read_records(absent) == []
    assert not absent.exists()


def test_one_unreadable_record_does_not_strand_the_outcome_report(tmp_path):
    """Same line reconcile.py takes: fail closed on the file, not on the pass."""
    root = _write(tmp_path / "records", [_ok("o/r#1"), _failed("o/r#2")])
    (root / "bad.json").write_text("{not json", encoding="utf-8")
    rep = C.outcome_report(C.read_records(root))
    assert rep["records_read"] == 2
    assert len(rep["attention"]) == 1


def test_observed_states_still_answers_the_stage_question_unchanged(tmp_path):
    """The outcome axis must not disturb the stage axis it sits beside."""
    root = _write(tmp_path / "records", [_ok("o/r#1"), _quarantined("o/r#4")])
    assert C.observed_states(root) == {"done", "blocked"}


# --------------------------------------------------------------------------
# pinned to the real writer, not to hand-rolled dicts
# --------------------------------------------------------------------------


def test_records_written_by_records_py_are_classified_correctly(tmp_path):
    """A field rename in records.py that stopped attesting outcomes would make
    every night read as unattested forever — an alarm that cries wolf is
    disabled within a week. So the fixture is the real writer.
    """
    root = tmp_path / "records"

    won = R.transition(R.new_claim("o/r#1", machine="m", host="h", job_id="j"),
                       "done", reason="ran to completion, exit 0", returncode=0)
    lost = R.transition(R.new_claim("o/r#2", machine="m", host="h", job_id="j"),
                        "done", reason="payload exited 3", returncode=3,
                        failure_category="payload-error")
    stuck = R.transition(R.new_claim("o/r#3", machine="m", host="h", job_id="j"),
                         "blocked", reason="attempts exhausted",
                         failure_category="quarantine")
    for rec in (won, lost, stuck):
        R.write_record(root, rec)

    rep = C.outcome_report(C.read_records(root))
    assert rep["counts"][C.OUTCOME_SUCCEEDED] == 1
    assert rep["counts"][C.OUTCOME_FAILED] == 1
    assert rep["counts"][C.OUTCOME_QUARANTINED] == 1
    assert {a["issue"] for a in rep["attention"]} == {"o/r#2", "o/r#3"}


def test_drains_unknown_outcome_shape_is_not_read_as_a_success(tmp_path):
    """drain.py writes `blocked` + `unknown-outcome` + `returncode: null` for a
    run whose exit code it could not learn — "never a 0 nobody observed". The
    reporter must agree that this is not a success.
    """
    rec = R.transition(R.new_claim("o/r#1", machine="m", host="h", job_id="j"),
                       "blocked", reason="outcome could not be determined",
                       failure_category="unknown-outcome")
    assert C.outcome_of(rec) != C.OUTCOME_SUCCEEDED
    assert C.outcome_report([rec])["attention"]


# --------------------------------------------------------------------------
# the exit code — what the unattended loop reads
# --------------------------------------------------------------------------


def _clean_reports():
    return {"r": C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB,
                                {"ready", "active", "done"})}


def test_a_night_with_a_failed_card_does_not_exit_zero():
    """1344 cards run unattended; something automated reads this exit code.

    A total-failure night that exits 0 is the defect in its most expensive
    form — nobody even gets as far as reading the report.
    """
    failed = C.outcome_report([_ok(), _failed()])
    assert C.exit_code(_clean_reports(), outcomes=failed) == 1


def test_quarantined_and_unattested_cards_also_fail_the_run():
    for rep in (C.outcome_report([_quarantined()]), C.outcome_report([_unattested()])):
        assert C.exit_code(_clean_reports(), outcomes=rep) == 1


def test_a_night_where_everything_worked_exits_zero():
    ok = C.outcome_report([_ok("o/r#1"), _ok("o/r#2")])
    assert C.exit_code(_clean_reports(), outcomes=ok) == 0


def test_work_still_in_flight_does_not_fail_the_run():
    """Mid-run is not failure. Only a decided bad outcome is."""
    flight = C.outcome_report([_in_flight(), _rec("o/r#9", "ready")])
    assert C.exit_code(_clean_reports(), outcomes=flight) == 0


def test_not_consulting_records_does_not_invent_a_failure_either():
    """Absence proves nothing in BOTH directions — it is not a pass and not a
    fail. The report says NOT-MEASURED in the text; the exit code stays 0 so
    the default invocation keeps its meaning."""
    assert C.exit_code(_clean_reports(), outcomes=C.outcome_report(None)) == 0
    assert C.exit_code(_clean_reports()) == 0


def test_the_existing_break_and_strict_semantics_are_untouched():
    broken = {"r": C.chain_report([{"labels": ["machine:dev-primary", "dispatch:ready"]}],
                                  {"machine:dev-primary", "dispatch:ready"}, set())}
    unproven = {"r": C.chain_report([], FULL_VOCAB, observed=set())}
    ok = C.outcome_report([_ok()])

    assert C.exit_code(broken, outcomes=ok) == 1, "a BREAK still fails on its own"
    assert C.exit_code(unproven) == 0
    assert C.exit_code(unproven, strict=True) == 1
    assert C.exit_code(unproven, strict=True, outcomes=ok) == 1


# --------------------------------------------------------------------------
# what the human actually reads at 8am
# --------------------------------------------------------------------------


def test_the_rendered_block_distinguishes_the_two_nights():
    """The property the report exists for, at the surface a human meets.

    Not a check on wording — a check that the wording cannot be the same.
    """
    worked = C.format_outcomes(C.outcome_report([_ok(f"o/r#{n}") for n in range(4)]))
    failed = C.format_outcomes(C.outcome_report([_failed(f"o/r#{n}") for n in range(4)]))
    unmeasured = C.format_outcomes(C.outcome_report(None))

    assert worked != failed
    assert unmeasured != worked
    assert unmeasured != failed


def test_every_flagged_card_is_named_in_the_rendered_block():
    """The evidence has to reach the page, not just the JSON.

    A summary line saying "12 failed" with the identities only in `--json` is a
    count standing in for evidence at the exact moment someone needs to act.
    """
    rep = C.outcome_report([_failed("o/r#2"), _quarantined("o/r#4"),
                            _unattested("o/r#3"), _ok("o/r#1")])
    text = "\n".join(C.format_outcomes(rep))
    for issue in ("o/r#2", "o/r#3", "o/r#4"):
        assert issue in text, issue


def test_a_long_failure_list_is_capped_on_screen_but_never_in_the_data():
    """1344 cards can fail. The morning read must stay readable; the record of
    what failed must stay complete, and the block must say it was truncated."""
    rep = C.outcome_report([_failed(f"o/r#{n}") for n in range(200)])
    assert len(rep["attention"]) == 200
    lines = C.format_outcomes(rep)
    assert len(lines) < 60, "the whole 200 cannot land on the morning screen"
    assert any("200" in line for line in lines), "the true total must still be stated"


def test_the_unmeasured_block_states_the_conflation_it_is_covering_for():
    """A reader who never passes `--records` must be told what they cannot see —
    otherwise the missing section is itself an absence reading as success."""
    lines = C.format_outcomes(C.outcome_report(None))
    assert lines, "not-measured must still print something"
    assert any("--records" in line for line in lines)


def test_format_outcomes_never_prints_a_count_it_did_not_measure():
    """No digits at all in the unmeasured block: a stray `0` beside a bucket
    name is precisely the reading this rail exists to prevent.

    Colour codes are digits too, and are not counts — stripped before the check
    so this asserts the report's content, not its escape sequences.
    """
    text = re.sub(r"\033\[[0-9;]*m", "",
                  "\n".join(C.format_outcomes(C.outcome_report(None))))
    assert not any(ch.isdigit() for ch in text), text


# --------------------------------------------------------------------------
# guards on the guard
# --------------------------------------------------------------------------


def test_the_outcome_reader_reaches_no_write_primitive():
    """READ-ONLY is a property of the file, and the new half must not weaken it."""
    src = CHAIN_PY.read_text(encoding="utf-8")
    for primitive in ("write_text", ".mkdir(", "os.remove", "os.rename", "shutil",
                      ".unlink(", "rmtree", "open("):
        assert primitive not in src, f"chain.py reaches {primitive!r}"


def test_outcome_report_does_not_mutate_the_records_it_is_given():
    """A reporter that edits its evidence has changed the answer."""
    population = [_ok(), _failed(), _quarantined()]
    before = json.dumps(population, sort_keys=True)
    C.outcome_report(population)
    assert json.dumps(population, sort_keys=True) == before
