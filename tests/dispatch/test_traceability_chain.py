#!/usr/bin/env python3
"""Traceability chain: issue → assigned → dispatched → executed → result → published.

deckhand#584 §3. The requirement is explicit that the interesting output is the
BREAK, not the completion: *"surface where the chain breaks, not just where it
completes — a result with no capability is the interesting case."*

## What building it found

`SCHEMA.yaml:125` documents the lifecycle as **`ready | active | done`**. Only
`dispatch:ready` exists as a label, in any repo. `dispatch:active` and
`dispatch:done` were never created.

Measured 2026-07-31: **867 open issues carry `dispatch:ready`** (525
workspace-hub, 342 digitalmodel). Nothing can move them out of it, because the
next two states have no vocabulary. SCHEMA.yaml:150 says as much in passing —
*"route.py only ever moves a card to dispatch:ready"* — but reads as a note about
route.py's scope rather than a dead end for 867 issues.

So the chain breaks at its second link, and every issue in the system is parked
one step past the start.

## The distinction this reporter is built around

A stage with zero occupancy has THREE completely different causes:

    UNREPRESENTABLE  the label does not exist — nothing COULD be here
    NEVER-OBSERVED   the label exists, nobody is in it, and nothing has ever
                     been recorded reaching it — created, never exercised
    EMPTY            the label exists and has been used; it is idle right now

Conflating them is the failure this whole epic keeps meeting: absence of signal
reading as success. A chain report that just prints `executed: 0` invites
"nothing has finished yet"; the truth is "finishing cannot be recorded".

So every stage carries its vocabulary status, and a stage whose label is missing
is reported as a **defect in the chain itself**, not as a count.

## Why the middle state had to exist

Slice 5 CREATES `dispatch:active` and `dispatch:done`. The instant it does, both
BREAKs above vanish and both stages report a clean `0` — while nothing has ever
written them. The report would look healthier precisely because it stopped
measuring anything, and slice 5 would commit this epic's signature defect
(presence of vocabulary reading as capability) as its final act.

Live labels cannot settle it: a label can be added and removed without trace.
The durable evidence is the dispatch record (`records.py`), which outlives the
label and carries `previous_state` and `attempts` — so it says where an issue
has BEEN, not only where it is. Records are optional, and "records consulted,
none reached this state" is reported distinctly from "no records consulted",
because an unchecked absence reading like a checked one is the same defect one
level up.

Hermetic: pure functions over issue dicts, a label inventory, and a tmp_path
records root. No gh, no network.

Run: uv run --with pyyaml pytest tests/dispatch/test_traceability_chain.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest  # noqa: F401  (tmp_path fixture; kept for parity with the suite)

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAIN_PY = REPO_ROOT / "scripts" / "dispatch" / "chain.py"


def _load():
    spec = importlib.util.spec_from_file_location("chain", CHAIN_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["chain"] = mod
    spec.loader.exec_module(mod)
    return mod


C = _load()

FULL_VOCAB = {"machine:dev-primary", "dispatch:ready", "dispatch:active", "dispatch:done"}
REAL_VOCAB = {"machine:dev-primary", "dispatch:ready"}   # what actually exists today


# --------------------------------------------------------------------------
# stage assignment
# --------------------------------------------------------------------------


def test_issue_with_no_machine_is_unassigned():
    assert C.stage_of({"labels": ["domain:cfd"]}) == "unassigned"


def test_issue_with_a_machine_is_assigned():
    assert C.stage_of({"labels": ["machine:dev-primary"]}) == "assigned"


def test_dispatch_ready_is_queued():
    assert C.stage_of({"labels": ["machine:dev-primary", "dispatch:ready"]}) == "queued"


def test_furthest_stage_wins():
    """An issue carrying several markers is at its FURTHEST point, not its first.

    Reporting the earliest would make progress invisible — the chain is about how
    far work got.
    """
    labels = ["machine:dev-primary", "dispatch:ready", "dispatch:done"]
    assert C.stage_of({"labels": labels}) == "executed"


def test_closed_issue_without_markers_is_not_silently_executed():
    """Closing an issue is not evidence it ran.

    Treating `state: closed` as "executed" would fabricate the very completion
    the chain exists to verify.
    """
    got = C.stage_of({"labels": ["machine:dev-primary"], "state": "closed"})
    assert got == "assigned"


# --------------------------------------------------------------------------
# the core distinction: unrepresentable vs empty
# --------------------------------------------------------------------------


def test_a_stage_whose_label_does_not_exist_is_UNREPRESENTABLE():  # noqa: N802
    """The defect this file exists for.

    `dispatch:done` does not exist in any repo. A report saying `executed: 0`
    would read as "nothing has finished"; the truth is "finishing cannot be
    recorded".
    """
    rep = C.chain_report([{"labels": ["machine:dev-primary", "dispatch:ready"]}], REAL_VOCAB)
    assert rep["stages"]["executed"]["vocabulary"] == "MISSING"
    assert rep["stages"]["queued"]["vocabulary"] == "present"


def test_a_stage_with_vocabulary_and_nobody_in_it_is_not_MISSING():  # noqa: N802
    """Having the label is enough to stop it being a BREAK — and no more.

    This test used to assert `present` here, which is the reading slice 5 was
    about to make free: create the two labels, and a stage nothing has ever
    written reports exactly like a healthy idle one. It now asserts the weaker,
    true thing; `NEVER-OBSERVED` is pinned by the section below.
    """
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB)
    assert rep["stages"]["executed"]["vocabulary"] != C.VOCAB_MISSING
    assert rep["stages"]["executed"]["count"] == 0
    assert not [b for b in rep["breaks"] if b["stage"] == "executed"]


def test_missing_vocabulary_is_reported_as_a_break_not_a_count():
    """A count of zero invites a shrug. A named break invites a fix."""
    rep = C.chain_report([{"labels": ["machine:dev-primary", "dispatch:ready"]}], REAL_VOCAB)
    breaks = rep["breaks"]
    assert any(b["stage"] == "executed" and b["kind"] == "unrepresentable" for b in breaks), breaks


def test_no_break_reported_when_the_whole_vocabulary_exists():
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB)
    assert not [b for b in rep["breaks"] if b["kind"] == "unrepresentable"]


# --------------------------------------------------------------------------
# drop-off: where does the population actually stop
# --------------------------------------------------------------------------


def _population():
    return [
        {"labels": []},                                                    # unassigned
        {"labels": ["machine:dev-primary"]},                               # assigned
        {"labels": ["machine:dev-primary"]},                               # assigned
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
        {"labels": ["machine:dev-primary", "dispatch:ready"]},             # queued
    ]


def test_report_counts_every_issue_exactly_once():
    """A histogram that does not sum to the population is silently lossy."""
    rep = C.chain_report(_population(), REAL_VOCAB)
    assert sum(s["count"] for s in rep["stages"].values()) == len(_population())


def test_report_identifies_the_wall(_pop=None):
    """The stage where the most work is stuck AND the next step is impossible.

    That pairing is the actionable finding: a pile-up in front of a missing
    state is a different problem from a pile-up in front of a busy one.
    """
    rep = C.chain_report(_population(), REAL_VOCAB)
    assert rep["wall"] is not None
    assert rep["wall"]["stage"] == "queued"
    assert rep["wall"]["count"] == 3
    assert rep["wall"]["next_stage_vocabulary"] == "MISSING"


def test_no_wall_when_the_chain_is_traversable():
    rep = C.chain_report(_population(), FULL_VOCAB)
    assert rep["wall"] is None, "a full vocabulary means work can always move on"


# --------------------------------------------------------------------------
# guards on the guard
# --------------------------------------------------------------------------


def test_stage_order_is_declared_and_non_empty():
    assert C.STAGES and C.STAGES[0] == "unassigned"
    assert "published" in C.STAGES, "the terminal state is a published capability (#584 §4)"


def test_empty_input_does_not_fabricate_a_wall():
    """Zero issues must not read as a healthy chain OR a broken one."""
    rep = C.chain_report([], FULL_VOCAB)
    assert rep["wall"] is None
    assert sum(s["count"] for s in rep["stages"].values()) == 0


# --------------------------------------------------------------------------
# the third state: created, never exercised
#
# Slice 5 creates `dispatch:active` and `dispatch:done`. At that instant both
# BREAKs disappear and both stages read a clean `0` while nothing has ever
# written them — the report gets healthier by ceasing to measure. These tests
# are the reason it cannot.
# --------------------------------------------------------------------------


def _write_record(root, name, record):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
    return root


def test_creating_the_labels_must_not_make_the_report_look_healthier():
    """The headline. Same 3 queued issues; the only change is the vocabulary.

    Before slice 5 the report says BREAK. After, it must still say something —
    because nothing about the actual system changed. A stage that goes straight
    from MISSING to `present` on label creation has been silenced, not fixed.
    """
    before = C.chain_report(_population(), REAL_VOCAB, observed=set())
    after = C.chain_report(_population(), FULL_VOCAB, observed=set())

    assert before["stages"]["executed"]["vocabulary"] == C.VOCAB_MISSING
    assert before["breaks"], "the pre-slice-5 BREAK is the behaviour being preserved"

    assert after["stages"]["executed"]["vocabulary"] == C.VOCAB_NEVER_OBSERVED
    assert not after["breaks"], "an existing label is not a break"
    assert after["unproven"], "…but it is still not evidence that anything ran"
    assert after["stall"] is not None, "3 issues are still parked in front of it"


def test_never_observed_is_its_own_state_not_a_flavour_of_present():
    """If this ever compares equal to `present`, the distinction is gone.

    Collapsing the two is the single mutation that most cheaply restores the
    defect, so it is asserted directly rather than only through behaviour.
    """
    assert C.VOCAB_NEVER_OBSERVED != C.VOCAB_PRESENT
    assert C.VOCAB_NEVER_OBSERVED != C.VOCAB_MISSING
    assert C.VOCAB_NEVER_OBSERVED != C.VOCAB_NOT_MEASURED
    assert "never" in C.VOCAB_NEVER_OBSERVED.lower()


def test_a_label_nobody_has_ever_written_is_NEVER_OBSERVED():  # noqa: N802
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB,
                         observed=set())
    for stage in ("queued", "executing", "executed"):
        assert rep["stages"][stage]["vocabulary"] == C.VOCAB_NEVER_OBSERVED, stage


def test_never_observed_is_reported_as_unproven_and_never_as_a_break():
    """It is not an error. A fresh label is the normal state on day one.

    Filing it as a BREAK would train the reader to ignore BREAKs, which costs
    more than the thing it reports.
    """
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB,
                         observed=set())
    assert not rep["breaks"]
    assert {u["stage"] for u in rep["unproven"]} == {"queued", "executing", "executed"}
    assert all(u["kind"] == "never-observed" for u in rep["unproven"])


def test_an_occupied_stage_is_present_with_no_records_at_all():
    """Live occupancy is proof enough of *this* stage; records are for history."""
    rep = C.chain_report(_population(), FULL_VOCAB, observed=set())
    assert rep["stages"]["queued"]["vocabulary"] == C.VOCAB_PRESENT
    assert rep["stages"]["queued"]["evidence"] == C.EV_OCCUPIED


# --------------------------------------------------------------------------
# "we looked and found nothing" vs "we never looked"
# --------------------------------------------------------------------------


def test_not_consulting_records_is_distinguishable_from_finding_none():
    """Same verdict, different standing behind it.

    An unchecked absence reported identically to a checked one is the same
    defect one level up — a missing check reading greener than a failing one.
    """
    unchecked = C.chain_report([], FULL_VOCAB)                 # no records arg
    checked = C.chain_report([], FULL_VOCAB, observed=set())   # consulted, empty

    assert unchecked["stages"]["executed"]["vocabulary"] == C.VOCAB_NEVER_OBSERVED
    assert checked["stages"]["executed"]["vocabulary"] == C.VOCAB_NEVER_OBSERVED
    assert unchecked["stages"]["executed"]["evidence"] == C.EV_NO_RECORDS
    assert checked["stages"]["executed"]["evidence"] == C.EV_RECORDS_CONSULTED
    assert unchecked["records_consulted"] is False
    assert checked["records_consulted"] is True


def test_the_unproven_detail_says_which_kind_of_absence_it_is():
    checked = C.chain_report([], FULL_VOCAB, observed=set())["unproven"][0]
    unchecked = C.chain_report([], FULL_VOCAB)["unproven"][0]
    assert "no records were consulted" in unchecked["detail"]
    assert "no records were consulted" not in checked["detail"]


# --------------------------------------------------------------------------
# records as the durable evidence
# --------------------------------------------------------------------------


def test_a_record_that_reached_done_makes_executed_present_though_empty():
    """Zero issues carry the label right now, and the stage is still exercised.

    This is the case live labels cannot answer: `dispatch:done` was added and
    removed, and the label inventory has forgotten. The record has not.
    """
    observed = C.states_evidenced_by({"issue": "o/r#1", "state": "done"})
    rep = C.chain_report([{"labels": ["machine:dev-primary"]}], FULL_VOCAB, observed)
    assert rep["stages"]["executed"]["count"] == 0
    assert rep["stages"]["executed"]["vocabulary"] == C.VOCAB_PRESENT
    assert rep["stages"]["executed"]["evidence"] == C.EV_RECORD
    assert not rep["unproven"] or "executed" not in {u["stage"] for u in rep["unproven"]}


def test_previous_state_is_evidence_the_stage_was_passed_through():
    """`previous_state` exists precisely so a record says where it has BEEN."""
    assert "active" in C.states_evidenced_by({"state": "done", "previous_state": "active"})


def test_attempts_prove_active_even_after_both_state_fields_moved_on():
    """A claim IS the active state — `new_claim` sets `state: active` writing it.

    Without this, a record that was claimed, ran, failed and got quarantined
    (`state: blocked`, `previous_state: active` overwritten by a later hop)
    could stop attesting to the one thing it definitely did.
    """
    rec = {"state": "blocked", "previous_state": "ready",
           "attempts": [{"attempt": 1, "host": "h", "claimed_at": "t"}]}
    assert "active" in C.states_evidenced_by(rec)


def test_a_record_in_ready_does_not_credit_the_later_stages():
    """No walking backwards down the chain. `done` must be recorded, not implied."""
    seen = C.states_evidenced_by({"state": "ready", "attempts": []})
    assert "done" not in seen
    assert "active" not in seen


def test_reaching_done_is_not_read_as_having_passed_through_active():
    """Deliberate: it assumes a writer that cannot skip a state.

    The record is asked what it recorded, not what the chain diagram implies —
    inferring the middle stage would manufacture exactly the unobserved
    transition this file exists to expose.
    """
    seen = C.states_evidenced_by({"state": "done", "previous_state": "done"})
    assert "active" not in seen


def test_observed_states_reads_a_records_directory(tmp_path):
    root = _write_record(tmp_path / "records", "o-r-1",
                         {"schema": 1, "issue": "o/r#1", "state": "done",
                          "previous_state": "active"})
    assert C.observed_states(root) == {"done", "active"}


def test_a_missing_records_root_is_empty_and_is_NOT_created(tmp_path):  # noqa: N802
    """Read-only means the reporter does not materialise what it measures."""
    absent = tmp_path / "nope"
    assert C.observed_states(absent) == set()
    assert not absent.exists()


def test_one_unreadable_record_does_not_strand_the_others(tmp_path):
    """Same line reconcile.py takes: fail closed on the file, not on the pass."""
    root = tmp_path / "records"
    _write_record(root, "good", {"schema": 1, "issue": "o/r#1", "state": "done"})
    (root / "bad.json").write_text("{not json", encoding="utf-8")
    assert C.observed_states(root) == {"done"}


def test_records_written_by_records_py_are_understood(tmp_path):
    """The evidence reader is pinned to the real writer, not to a hand-rolled dict.

    A field rename in records.py that silently stopped attesting anything would
    make every stage read NEVER-OBSERVED forever — an alarm that cries wolf is
    disabled within a week.
    """
    spec = importlib.util.spec_from_file_location(
        "chain_test_records", REPO_ROOT / "scripts" / "dispatch" / "records.py")
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)

    root = tmp_path / "records"
    claim = R.new_claim("o/r#1", machine="m", host="h", job_id="j")
    R.write_record(root, claim)
    assert C.observed_states(root) == {"ready", "active"}

    R.write_record(root, R.transition(claim, "done", reason="ok", returncode=0))
    assert C.observed_states(root) >= {"active", "done"}

    rep = C.chain_report([], FULL_VOCAB, C.observed_states(root))
    assert rep["stages"]["executed"]["vocabulary"] == C.VOCAB_PRESENT
    assert rep["stages"]["executing"]["vocabulary"] == C.VOCAB_PRESENT


# --------------------------------------------------------------------------
# the new state must not weaken the old ones
# --------------------------------------------------------------------------


def test_a_missing_label_still_BREAKS_even_when_a_record_proves_the_state():  # noqa: N802
    """Records are evidence of history, never a substitute for vocabulary.

    A record saying `done` with no `dispatch:done` label is a chain that cannot
    show its own state in the UI. Letting the record satisfy the check would
    hide precisely that.
    """
    rep = C.chain_report(_population(), REAL_VOCAB, {"ready", "active", "done"})
    assert rep["stages"]["executed"]["vocabulary"] == C.VOCAB_MISSING
    assert any(b["stage"] == "executed" for b in rep["breaks"])
    assert rep["wall"] is not None and rep["wall"]["stage"] == "queued"


def test_records_never_change_the_counts():
    """Evidence answers "ever", not "how many". Occupancy stays label-derived."""
    plain = C.chain_report(_population(), FULL_VOCAB)
    with_records = C.chain_report(_population(), FULL_VOCAB,
                                  {"ready", "active", "done"})
    assert ({s: v["count"] for s, v in plain["stages"].items()}
            == {s: v["count"] for s, v in with_records["stages"].items()})


def test_stall_names_the_pile_up_in_front_of_an_unexercised_stage():
    """A wall needs a label created; a stall needs a writer that runs.

    Same 525-at-queued shape, different fix, so they are reported separately
    rather than one being folded into the other.
    """
    rep = C.chain_report(_population(), FULL_VOCAB, observed=set())
    assert rep["wall"] is None, "the vocabulary is complete — this is not a wall"
    assert rep["stall"]["stage"] == "queued"
    assert rep["stall"]["count"] == 3
    assert rep["stall"]["next_stage"] == "executing"
    assert rep["stall"]["next_stage_vocabulary"] == C.VOCAB_NEVER_OBSERVED


def test_no_stall_once_the_next_stage_has_actually_been_reached():
    rep = C.chain_report(_population(), FULL_VOCAB, {"ready", "active"})
    assert rep["stall"] is None
    assert rep["wall"] is None


def test_result_and_published_stay_not_measured_whatever_the_records_say():
    """They are NOT label-borne. No amount of evidence promotes or zeroes them.

    A `done` record must not be allowed to leak into `result`: "it ran" and "it
    produced a result someone can use" are the two things #584 §4 exists to
    keep apart.
    """
    for observed in (None, set(), {"ready", "active", "done", "blocked"}):
        rep = C.chain_report(_population(), FULL_VOCAB, observed)
        for stage in C.NOT_LABEL_BORNE:
            assert rep["stages"][stage]["vocabulary"] == C.VOCAB_NOT_MEASURED
            assert rep["stages"][stage]["evidence"] == C.EV_NOT_APPLICABLE
        assert not [u for u in rep["unproven"] if u["stage"] in C.NOT_LABEL_BORNE]
        assert not [b for b in rep["breaks"] if b["stage"] in C.NOT_LABEL_BORNE]


# --------------------------------------------------------------------------
# exit code and read-only posture
# --------------------------------------------------------------------------


def test_never_observed_alone_does_not_fail_the_run_by_default():
    """Day one after slice 5, "never used" is the only honest answer, not a fault."""
    rep = {"r": C.chain_report([], FULL_VOCAB, observed=set())}
    assert rep["r"]["unproven"]
    assert C.exit_code(rep) == 0


def test_strict_fails_the_run_on_never_observed():
    """For the caller who has decided enough time has passed."""
    rep = {"r": C.chain_report([], FULL_VOCAB, observed=set())}
    assert C.exit_code(rep, strict=True) == 1


def test_a_break_fails_the_run_in_either_mode():
    rep = {"r": C.chain_report(_population(), REAL_VOCAB, observed=set())}
    assert C.exit_code(rep) == 1
    assert C.exit_code(rep, strict=True) == 1


def test_a_fully_exercised_chain_passes_in_strict_mode():
    rep = {"r": C.chain_report(_population(), FULL_VOCAB,
                               {"ready", "active", "done"})}
    assert C.exit_code(rep, strict=True) == 0


def test_the_module_reaches_no_write_primitive():
    """READ-ONLY is a property of the file, not an intention in its docstring."""
    src = CHAIN_PY.read_text(encoding="utf-8")
    for primitive in ("write_text", ".mkdir(", "os.remove", "os.rename", "shutil",
                      ".unlink(", "rmtree", "open("):
        assert primitive not in src, f"chain.py reaches {primitive!r}"


def test_every_gh_call_in_the_module_is_a_read():
    """The subprocess surface, checked as argv rather than as prose.

    A substring scan over the whole file cannot tell `gh label create` in a
    comment from one in an argv — so the argv is what gets read.
    """
    src = CHAIN_PY.read_text(encoding="utf-8")
    calls = re.findall(r'"gh",\s*"(\w+)",\s*"(\w+)"', src)
    assert calls, "no gh invocation found — the scan is looking at the wrong shape"
    assert set(calls) <= {("issue", "list"), ("label", "list")}, calls


def test_every_stage_carries_both_a_verdict_and_its_evidence():
    """A verdict with no stated basis is how an unchecked check passes review."""
    rep = C.chain_report(_population(), FULL_VOCAB, observed=set())
    for stage, entry in rep["stages"].items():
        assert set(entry) == {"count", "vocabulary", "evidence"}, stage
        assert entry["vocabulary"] in {
            C.VOCAB_PRESENT, C.VOCAB_MISSING,
            C.VOCAB_NEVER_OBSERVED, C.VOCAB_NOT_MEASURED}, stage
