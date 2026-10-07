#!/usr/bin/env python3
"""chain.py — traceability from issue to published capability (deckhand#584 §3).

READ-ONLY. Reports where the chain BREAKS, which is the requirement:
"surface where the chain breaks, not just where it completes — a result with no
capability is the interesting case."

## The distinction this tool is built around

A stage with zero occupancy has THREE completely different causes:

    UNREPRESENTABLE   the label does not exist — nothing COULD be here
    NEVER-OBSERVED    the label exists, nobody is in it, and nothing has ever
                      been recorded reaching it — created, never exercised
    EMPTY             the label exists and has been used; it is idle right now

`executed: 0` invites "nothing has finished yet". If `dispatch:done` does not
exist, the truth is "finishing cannot be recorded" — a defect in the chain, not a
measurement of progress.

The middle state exists because of what happens the moment slice 5 CREATES
`dispatch:active` and `dispatch:done`: both BREAKs vanish and both stages read a
clean `0` while nothing has ever written them. The report would look healthier
precisely because it stopped measuring anything — this epic's signature defect,
presence of vocabulary reading as capability. NEVER-OBSERVED is not an error. It
is the normal state of a label the day it is created and an alarming one a month
later, and the report must be able to say which.

## Evidence, and the absence of it

Occupancy of a live label proves a stage is reachable NOW. It cannot prove a
stage was EVER reached, because a label can be added and removed without trace.
The durable evidence is the dispatch record (`records.py`): it survives the
label, and it carries `previous_state` and `attempts`, so it says where an issue
has BEEN and not merely where it is.

Records are optional. With no records root, this tool reports NEVER-OBSERVED
with `evidence: no-records-consulted` — distinct from `records-consulted`, so
"we looked and found nothing" can never be confused with "we never looked",
which is the same defect one level up.

## `ran` is not `succeeded` — the second axis (#3773 rail R5)

`records.py` keeps two things apart on purpose:

    state: done      the payload RAN TO COMPLETION — NOT that it worked
    is_success       `done` AND `returncode == 0` — whether it actually worked

The STAGE axis above answers *how far did this card get*, and a card that ran
and failed did reach `executed` — it is counted there, correctly. But until
this file consulted `records.is_success`, that was the ONLY thing it reported,
so **a night that failed every card printed exactly the same report as a night
that completed every card.** Over an unattended run of 1344 cards, that is the
whole morning read saying nothing.

The fix is a second axis rather than a correction to the first: folding failure
into a stage count would put two questions behind one number again. `executed`
still counts what RAN; the OUTCOMES block says what WORKED, and it holds the
same standard as the rest of this file —

  * an absence never reads as a success: no `--records` yields NOT-MEASURED
    counts, never `failed: 0`, for the same reason `published` is not a zero;
  * a count never stands in for evidence: every card needing attention is
    named, with its returncode, failure_category and attempt number;
  * silence stays evidence-backed: "read N records, none failed", "there are no
    records", and "we never looked" are three different reports.

`done` with no returncode is its own verdict (UNATTESTED), not a success and
not a clean failure: nobody observed an exit code, so nobody knows. drain.py
promises never to write that shape — which is exactly why the reporter cannot
assume it, since a guarantee held in another module is one this one cannot see
break.

## What it found on first run

`SCHEMA.yaml:125` documents `dispatch:<state>` as `ready | active | done`. Only
`dispatch:ready` exists. 867 open issues sit in it and cannot move, because the
next two states have no vocabulary.

Usage:
    chain.py                          # all default repos
    chain.py --repo owner/name
    chain.py --records .dispatch/records   # also measures ran-vs-succeeded
    chain.py --json                        # {"repos": {...}, "outcomes": {...}}
    chain.py --strict                 # exit non-zero on NEVER-OBSERVED too
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Sibling scripts, not a package — same loader shape as reconcile.py and
# drain.py, so `records` resolves whether chain.py is run directly, imported by
# a test, or exec'd from another cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import records  # noqa: E402

#: Ordered chain. An issue is reported at its FURTHEST stage — reporting the
#: earliest would make progress invisible.
STAGES = ("unassigned", "assigned", "queued", "executing", "executed", "result", "published")

#: The label that puts an issue at each stage. `unassigned` is the absence of a
#: machine, so it has no marker; `result` and `published` are not label-borne at
#: all — see NOT_LABEL_BORNE below.
STAGE_MARKER = {
    "queued": "dispatch:ready",
    "executing": "dispatch:active",
    "executed": "dispatch:done",
}

#: The dispatch RECORD state (records.py `STATES`) that corresponds to each
#: label-borne stage. The label is a projection of the record; the record is the
#: durable half, so it is what "has this ever happened" is asked of.
STAGE_RECORD_STATE = {
    "queued": "ready",
    "executing": "active",
    "executed": "done",
}

#: These stages cannot be determined from labels. `result` needs a join against
#: the licensed-run queue (queue/results/<id>.json); `published` needs the
#: aceengineer-website capability pages. Reported as NOT-MEASURED rather than
#: zero, because a zero here would be indistinguishable from "nothing shipped" —
#: the exact conflation this tool exists to prevent.
NOT_LABEL_BORNE = ("result", "published")

#: Vocabulary states, worst to best. `NEVER_OBSERVED` is deliberately not
#: spellable as a synonym of `present`: anything that reads it as "fine" has
#: reintroduced the defect the state was added to expose.
VOCAB_NOT_MEASURED = "not-measured"
VOCAB_MISSING = "MISSING"
VOCAB_NEVER_OBSERVED = "NEVER-OBSERVED"
VOCAB_PRESENT = "present"

#: Why a stage carries the vocabulary state it does. Reported alongside it so a
#: NEVER-OBSERVED with `no-records-consulted` cannot be mistaken for a
#: NEVER-OBSERVED that survived a real check.
EV_OCCUPIED = "live-label-occupied"        # issues carry it right now
EV_RECORD = "record"                       # a durable record reached this state
EV_RECORDS_CONSULTED = "records-consulted"  # records were read; none reached it
EV_NO_RECORDS = "no-records-consulted"      # nothing was read; absence proves nothing
EV_UNREPRESENTABLE = "no-label"
EV_NOT_APPLICABLE = "not-label-borne"

#: The OUTCOME axis. Deliberately not spellable as flavours of one another: the
#: cheapest mutation that restores this rail's defect is collapsing two of these
#: into a single "finished" bucket. Benign verdicts are lowercase, the ones that
#: want a human are shouted — the same convention `MISSING` and `NEVER-OBSERVED`
#: already use against `present`.
OUTCOME_SUCCEEDED = "succeeded"          # records.is_success: done AND exit 0
OUTCOME_FAILED = "FAILED"                # ran to completion, nonzero exit
OUTCOME_UNATTESTED = "UNATTESTED"        # done, no exit code — nobody observed one
OUTCOME_QUARANTINED = "QUARANTINED"      # blocked: terminal, will not be retried
OUTCOME_IN_FLIGHT = "in-flight"          # ready/active — no outcome YET
OUTCOME_UNRECOGNISED = "UNRECOGNISED"    # a state this reporter does not know

#: Fixed order so the histogram reads the same every morning, and so a new
#: outcome cannot be added without deciding where it sits.
OUTCOME_ORDER = (OUTCOME_SUCCEEDED, OUTCOME_FAILED, OUTCOME_UNATTESTED,
                 OUTCOME_QUARANTINED, OUTCOME_UNRECOGNISED, OUTCOME_IN_FLIGHT)

#: Everything that is not a success and not still running. Ordered worst-first:
#: a quarantined card is dead, a failed one gets another attempt, an unattested
#: one may have worked and we cannot tell. `in-flight` is NOT here — mid-run is
#: not failure, and crying one trains the reader to ignore both, the same reason
#: NEVER-OBSERVED is not filed as a BREAK.
OUTCOMES_NEEDING_ATTENTION = (OUTCOME_QUARANTINED, OUTCOME_UNATTESTED,
                              OUTCOME_FAILED, OUTCOME_UNRECOGNISED)

#: How many flagged cards land on the morning screen. The DATA keeps all of
#: them; only the render is capped, and it states the true total when it cuts.
ATTENTION_PRINT_LIMIT = 12

DEFAULT_REPOS = (
    "vamseeachanta/workspace-hub",
    "vamseeachanta/digitalmodel",
    "vamseeachanta/deckhand",
)


def stage_of(issue: dict) -> str:
    """Furthest stage this issue has demonstrably reached.

    Deliberately does NOT treat `state: closed` as executed: closing an issue is
    not evidence it ran, and inferring so would fabricate the completion the
    chain exists to verify.
    """
    labels = set(issue.get("labels") or [])
    furthest = "unassigned"
    if any(lab.startswith("machine:") for lab in labels):
        furthest = "assigned"
    for stage in ("queued", "executing", "executed"):
        if STAGE_MARKER[stage] in labels:
            furthest = stage
    return furthest


def states_evidenced_by(record: dict) -> set[str]:
    """Record states this ONE record proves were reached, ever.

    Read from the record's own history, never inferred from chain order:

      `state`           where it is now.
      `previous_state`  where it came from — the whole reason the field exists.
      `attempts`        each entry is a claim, and `new_claim`/`reclaim` set
                        `state: active` when they append one. A record with
                        attempts has demonstrably been `active`, even if it has
                        since moved on and overwritten both fields above.

    What this deliberately does NOT do is walk backwards down STAGES — "it is
    done, so it must have been active" assumes a writer that cannot skip, which
    is exactly the kind of assumption this file exists to stop making.
    """
    seen: set[str] = set()
    for field in ("state", "previous_state"):
        value = record.get(field)
        if isinstance(value, str):
            seen.add(value)
    if record.get("attempts"):
        seen.add("active")
    return seen


def read_records(records_root) -> list[dict]:
    """Every readable record under the root, in a stable order. READ-ONLY.

    A missing root yields an empty list rather than an error, and — importantly
    — is not created on the way past: a reporter that materialises the directory
    it is measuring has changed the answer. A single unreadable record is
    skipped rather than fatal, for the reason `reconcile.reconcile` gives: one
    corrupt file must not strand the other 866.

    Both axes read the records ONCE through here. Two readers with two skip
    rules would let a record count toward the stage evidence and vanish from the
    outcome tally, and the disagreement would be invisible in either report.
    """
    root = Path(records_root)
    out: list[dict] = []
    if not root.is_dir():
        return out
    for path in sorted(root.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(record, dict):
            out.append(record)
    return out


def observed_in(records: list[dict]) -> set[str]:
    """Every record state this population can PROVE was reached. Pure: no IO."""
    seen: set[str] = set()
    for record in records:
        seen |= states_evidenced_by(record)
    return seen


def observed_states(records_root) -> set[str]:
    """Every record state this system can PROVE it has reached. READ-ONLY."""
    return observed_in(read_records(records_root))


# ---------------------------------------------------------------------------
# the outcome axis: did it WORK, as distinct from did it RUN
# ---------------------------------------------------------------------------


def outcome_of(record: dict) -> str:
    """What this ONE record says about whether the work succeeded.

    Success is asked of `records.is_success` and never re-derived here. A second
    definition of "worked" is how the two drift: that function could gain a
    condition tomorrow and a local copy would go on answering yesterday's
    question while looking maintained.

    The three ways of not succeeding are kept apart because the follow-up
    differs. `FAILED` has an exit code to investigate. `QUARANTINED` is terminal
    — attempts are exhausted and nothing will retry it, so it needs a human, not
    a rerun. `UNATTESTED` is a `done` carrying no exit code: nobody observed one,
    so calling it a failure accuses a card that may well have worked, and calling
    it a success is this rail's defect exactly. It is a measurement defect, and
    it is reported as one.
    """
    if records.is_success(record):
        return OUTCOME_SUCCEEDED
    state = record.get("state")
    if state == "done":
        rc = record.get("returncode")
        # bool is an int in Python, and a `returncode: true` is not an exit code.
        if isinstance(rc, int) and not isinstance(rc, bool):
            return OUTCOME_FAILED
        return OUTCOME_UNATTESTED
    if state == "blocked":
        return OUTCOME_QUARANTINED
    if state in records.STATES:
        return OUTCOME_IN_FLIGHT
    # No bucket, no count, no line in the report — a record nobody classified is
    # invisible, and invisible reads as fine. Named instead.
    return OUTCOME_UNRECOGNISED


def _attention_entry(record: dict, outcome: str) -> dict:
    """The evidence that travels with a flagged card.

    "4 failed" sends nobody anywhere; the returncode and the category do.
    `attempt`/`max_attempts` is on it because "failed once of three" and "failed
    the last time it will ever be tried" are different mornings.

    A record with no `issue` is still reported. Dropping it would be an absence
    manufactured by the very corruption the entry is evidence of.
    """
    return {
        "issue": record.get("issue") or "<record carries no issue field>",
        "outcome": outcome,
        "state": record.get("state"),
        "returncode": record.get("returncode"),
        "failure_category": record.get("failure_category"),
        "attempt": record.get("attempt"),
        "max_attempts": record.get("max_attempts"),
        "host": record.get("host"),
    }


def outcome_report(consulted: list[dict] | None) -> dict:
    """Ran-vs-succeeded over a records population. Pure: no IO.

    `None` means records were NOT consulted, and is reported as NOT-MEASURED
    with `counts: None` — never as a dict of zeros. `failed: 0` from a run that
    never read a record is the same lie as `published: 0` from an unbuilt join,
    and it is the more dangerous of the two: zero failures is the answer
    everyone wants to see.

    An EMPTY population is a third answer again. A typo in `--records` produces
    one, and it must not print like a clean night — it is NEVER-OBSERVED, on the
    same three-way distinction the stage axis draws.
    """
    if consulted is None:
        return {"consulted": False, "vocabulary": VOCAB_NOT_MEASURED,
                "evidence": EV_NO_RECORDS, "records_read": None,
                "counts": None, "attention": None}

    counts = {o: 0 for o in OUTCOME_ORDER}
    attention = []
    for record in consulted:
        outcome = outcome_of(record)
        counts[outcome] += 1
        if outcome in OUTCOMES_NEEDING_ATTENTION:
            attention.append(_attention_entry(record, outcome))

    # Worst first, then by issue: the cards that will never retry themselves are
    # the ones worth reading if the reader stops after the first few lines.
    attention.sort(key=lambda a: (OUTCOMES_NEEDING_ATTENTION.index(a["outcome"]),
                                  str(a["issue"])))

    return {
        "consulted": True,
        "vocabulary": VOCAB_PRESENT if consulted else VOCAB_NEVER_OBSERVED,
        "evidence": EV_RECORDS_CONSULTED,
        "records_read": len(consulted),
        "counts": counts,
        "attention": attention,
    }


def chain_report(issues: list[dict], vocabulary: set[str],
                 observed: set[str] | None = None) -> dict:
    """Population per stage, plus the breaks. Pure: no IO.

    `observed` is the set of record states proven to have been reached (see
    `observed_states`). `None` means records were NOT consulted, which is
    reported as such rather than as an empty set — "we looked and found nothing"
    and "we never looked" are different findings and must not print the same.
    """
    counts = {s: 0 for s in STAGES}
    for iss in issues:
        counts[stage_of(iss)] += 1

    stages = {}
    for s in STAGES:
        if s in NOT_LABEL_BORNE:
            # Never given a count-derived verdict. A zero here would read as
            # "nothing shipped" when it means "the join is unbuilt".
            vocab, evidence = VOCAB_NOT_MEASURED, EV_NOT_APPLICABLE
        elif s in STAGE_MARKER:
            if STAGE_MARKER[s] not in vocabulary:
                vocab, evidence = VOCAB_MISSING, EV_UNREPRESENTABLE
            elif counts[s] > 0:
                vocab, evidence = VOCAB_PRESENT, EV_OCCUPIED
            elif observed is not None and STAGE_RECORD_STATE[s] in observed:
                # Empty now, but a durable record has been here. Idle, not unused.
                vocab, evidence = VOCAB_PRESENT, EV_RECORD
            else:
                vocab = VOCAB_NEVER_OBSERVED
                evidence = EV_RECORDS_CONSULTED if observed is not None else EV_NO_RECORDS
        else:
            # unassigned/assigned are label-PRESENCE, not a marker: there is no
            # single label whose existence could be missing or unexercised.
            vocab, evidence = VOCAB_PRESENT, EV_OCCUPIED
        stages[s] = {"count": counts[s], "vocabulary": vocab, "evidence": evidence}

    breaks = [
        {"stage": s, "kind": "unrepresentable",
         "detail": f"{STAGE_MARKER[s]} does not exist — nothing can reach this stage"}
        for s in STAGES if stages[s]["vocabulary"] == VOCAB_MISSING
    ]

    # NOT a break. The vocabulary is there; it has simply never carried anything.
    # Kept out of `breaks` on purpose — a fresh label is not a defect, and
    # crying one would train the reader to ignore both.
    unproven = [
        {"stage": s, "kind": "never-observed", "evidence": stages[s]["evidence"],
         "detail": f"{STAGE_MARKER[s]} exists but no open issue carries it and "
                   + ("no dispatch record has ever reached "
                      f"{STAGE_RECORD_STATE[s]!r}" if stages[s]["evidence"] == EV_RECORDS_CONSULTED
                      else "no records were consulted, so nothing attests to it")
                   + " — created, never exercised"}
        for s in STAGES if stages[s]["vocabulary"] == VOCAB_NEVER_OBSERVED
    ]

    # The wall: the most-populated stage whose NEXT stage is unreachable. A
    # pile-up in front of a missing state is a different problem from a pile-up
    # in front of a busy one, and only the first is a vocabulary defect.
    wall = None
    for i, s in enumerate(STAGES[:-1]):
        nxt = STAGES[i + 1]
        if stages[nxt]["vocabulary"] == VOCAB_MISSING and counts[s] > 0:
            if wall is None or counts[s] > wall["count"]:
                wall = {"stage": s, "count": counts[s], "next_stage": nxt,
                        "next_stage_vocabulary": VOCAB_MISSING}

    # The stall: the same pile-up, in front of a stage that COULD take it and
    # never has. Reported separately from the wall because the fix is different
    # — the wall needs a label created, the stall needs a writer that runs.
    stall = None
    for i, s in enumerate(STAGES[:-1]):
        nxt = STAGES[i + 1]
        if stages[nxt]["vocabulary"] == VOCAB_NEVER_OBSERVED and counts[s] > 0:
            if stall is None or counts[s] > stall["count"]:
                stall = {"stage": s, "count": counts[s], "next_stage": nxt,
                         "next_stage_vocabulary": VOCAB_NEVER_OBSERVED,
                         "evidence": stages[nxt]["evidence"]}

    return {"stages": stages, "breaks": breaks, "unproven": unproven,
            "wall": wall, "stall": stall, "total": len(issues),
            "records_consulted": observed is not None}


def format_outcomes(block: dict) -> list[str]:
    """The OUTCOMES section as printed lines. Pure: no IO.

    Separate from the per-repo loop on purpose. A records root spans every repo,
    so printing this per repo would show the same failures three times and imply
    a per-repo join that was never made.
    """
    lines = [""]
    if not block["consulted"]:
        # No numbers here at all. A stray `0` beside a bucket name is precisely
        # the reading this section exists to prevent.
        lines.append("\033[1mOUTCOMES\033[0m  \033[2mnot measured here\033[0m")
        lines.append("\033[33m  Whether any card SUCCEEDED is unmeasured. The stages above say how far")
        lines.append("  each card got, not whether it worked — a night that fails every card and a")
        lines.append("  night that completes every card print identical stage counts. Pass")
        lines.append("  --records <dir> to measure it.\033[0m")
        return lines

    read = block["records_read"]
    counts = block["counts"]
    attention = block["attention"]

    if not read:
        lines.append("\033[1mOUTCOMES\033[0m  \033[33mno records under the root — "
                     "LABEL EXISTS, NEVER USED\033[0m")
        lines.append("\033[33m  Nothing attests to any outcome. This is not a clean night;")
        lines.append("  it is an unexercised one, or a --records path that points "
                     "somewhere empty.\033[0m")
        return lines

    lines.append(f"\033[1mOUTCOMES\033[0m  records={read}  "
                 f"\033[2m(ran ≠ succeeded; {EV_RECORDS_CONSULTED})\033[0m")
    for outcome in OUTCOME_ORDER:
        # Pad the NAME, then colour it. Padding the coloured string counts the
        # escape bytes, which are zero-width on screen — the count column would
        # sit several places left on exactly the rows that matter most.
        cell = f"{outcome:<14}"
        colour = ""
        if counts[outcome]:
            if outcome in (OUTCOME_FAILED, OUTCOME_QUARANTINED, OUTCOME_UNRECOGNISED):
                colour = "\033[1;31m"
            elif outcome == OUTCOME_UNATTESTED:
                colour = "\033[1;33m"
        lines.append(f"    {colour}{cell}\033[0m{counts[outcome]:>6}"
                     if colour else f"    {cell}{counts[outcome]:>6}")

    if not attention:
        lines.append(f"  \033[2mevery one of the {read} record(s) consulted reached "
                     f"exit 0 — verdict from records.is_success\033[0m")
        return lines

    lines.append(f"  \033[1;31mNOT SUCCEEDED: {len(attention)} of {read} record(s).\033[0m "
                 "\033[1mThe 'executed' stage counts cards that RAN;\033[0m")
    lines.append("  \033[1mthese ran and did not work. `done` is completion, not success.\033[0m")
    for entry in attention[:ATTENTION_PRINT_LIMIT]:
        rc = entry["returncode"]
        # An em-dash, never a 0: "no exit code was observed" and "it exited 0"
        # are the two readings this whole section exists to keep apart.
        rc_text = "—" if rc is None else str(rc)
        lines.append(
            f"    {str(entry['issue']):<34} {entry['outcome']:<13} "
            f"rc={rc_text:<6} {str(entry['failure_category'] or '—'):<16} "
            f"attempt {entry['attempt']}/{entry['max_attempts']}")
    if len(attention) > ATTENTION_PRINT_LIMIT:
        lines.append(f"    \033[2m… and {len(attention) - ATTENTION_PRINT_LIMIT} more "
                     f"({len(attention)} flagged in total; --json carries every one)\033[0m")
    return lines


def fetch(repo: str) -> tuple[list[dict], set[str]]:
    def gh(args):
        r = subprocess.run(args, capture_output=True, text=True, check=False)
        if r.returncode != 0:
            sys.exit(f"CANNOT CHECK: {' '.join(args[:4])}: {r.stderr.strip()[:160]}")
        return json.loads(r.stdout or "[]")

    raw = gh(["gh", "issue", "list", "--repo", repo, "--state", "open",
              "--limit", "2000", "--json", "number,labels,state"])
    issues = [{"number": i["number"], "state": i.get("state"),
               "labels": [l["name"] for l in i.get("labels") or []]} for i in raw]
    vocab = {l["name"] for l in gh(["gh", "label", "list", "--repo", repo,
                                    "--limit", "400", "--json", "name"])}
    return issues, vocab


def exit_code(reports: dict, strict: bool = False, *, outcomes: dict | None = None) -> int:
    """1 on a broken chain OR a card that did not succeed; `--strict` adds the
    unexercised one.

    NEVER-OBSERVED is not an error by default: right after the labels are
    created it is the only honest answer. `--strict` is for the caller who has
    decided enough time has passed that "never used" is a failure.

    A failed card IS an error in either mode. Something automated reads this
    exit code after an unattended run, and a total-failure night that exits 0 is
    this rail's defect in its most expensive form — nobody gets as far as
    reading the report. Cards still in flight are not failures, and an
    unconsulted records root is not one either: absence proves nothing in both
    directions, so it stays 0 and says NOT-MEASURED in the text instead.
    """
    if any(r["breaks"] for r in reports.values()):
        return 1
    if outcomes is not None and outcomes.get("attention"):
        return 1
    if strict and any(r["unproven"] for r in reports.values()):
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--records", help="dispatch records root; durable evidence "
                                      "that a stage was EVER reached")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when a label exists but was never observed")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # Read the records ONCE; both axes are derived from the same population so
    # they cannot disagree about which files were legible.
    consulted = read_records(args.records) if args.records else None
    observed = observed_in(consulted) if consulted is not None else None
    outcomes = outcome_report(consulted)

    out = {}
    for repo in ([args.repo] if args.repo else list(DEFAULT_REPOS)):
        issues, vocab = fetch(repo)
        out[repo] = chain_report(issues, vocab, observed)

    if args.json:
        print(json.dumps({"repos": out, "outcomes": outcomes}, indent=2))
        return exit_code(out, args.strict, outcomes=outcomes)

    for repo, rep in out.items():
        print(f"\n\033[1m{repo}\033[0m  open={rep['total']}")
        for s in STAGES:
            st = rep["stages"][s]
            mark = {VOCAB_MISSING: "\033[31mNO LABEL\033[0m",
                    VOCAB_NEVER_OBSERVED: "\033[33mLABEL EXISTS, NEVER USED\033[0m",
                    VOCAB_NOT_MEASURED: "\033[2mnot measured here\033[0m",
                    VOCAB_PRESENT: ""}[st["vocabulary"]]
            # A constant pointer, never a per-repo failure count: the records
            # root spans every repo, so any number spliced in here would be a
            # join this tool has not made.
            if s == "executed" and st["count"]:
                mark = (mark + "  " if mark else "") + \
                    "\033[2m← cards that RAN; see OUTCOMES for whether they worked\033[0m"
            print(f"    {s:<12}{st['count']:>6}   {mark}")
        if rep["wall"]:
            w = rep["wall"]
            print(f"  \033[1;31mWALL: {w['count']} issue(s) at '{w['stage']}' — "
                  f"'{w['next_stage']}' has no label, so none can advance\033[0m")
        if rep["stall"]:
            st = rep["stall"]
            print(f"  \033[1;33mSTALL: {st['count']} issue(s) at '{st['stage']}' — "
                  f"'{st['next_stage']}' has a label that nothing has ever "
                  f"entered ({st['evidence']})\033[0m")
        for b in rep["breaks"]:
            print(f"  \033[31mBREAK\033[0m {b['stage']}: {b['detail']}")
        for u in rep["unproven"]:
            print(f"  \033[33mUNPROVEN\033[0m {u['stage']}: {u['detail']}")

    for line in format_outcomes(outcomes):
        print(line)

    if not any(r["records_consulted"] for r in out.values()):
        print("\n\033[33mNo records root given (--records): 'never observed' above "
              "rests on live labels alone, which forget. Records are the durable "
              "evidence that a stage was ever reached.\033[0m")

    print("\n\033[2mREAD-ONLY. `result` and `published` need a join against the "
          "licensed-run queue and the website; reported as not-measured rather "
          "than zero so an unbuilt join cannot read as 'nothing shipped'. The "
          "same rule governs OUTCOMES: `done` means ran to completion, and "
          "whether it WORKED is records.is_success, never a stage count.\033[0m")
    return exit_code(out, args.strict, outcomes=outcomes)


if __name__ == "__main__":
    sys.exit(main())
