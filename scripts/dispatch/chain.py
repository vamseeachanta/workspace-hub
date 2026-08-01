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

## What it found on first run

`SCHEMA.yaml:125` documents `dispatch:<state>` as `ready | active | done`. Only
`dispatch:ready` exists. 867 open issues sit in it and cannot move, because the
next two states have no vocabulary.

Usage:
    chain.py                          # all default repos
    chain.py --repo owner/name
    chain.py --records .dispatch/records
    chain.py --json
    chain.py --strict                 # exit non-zero on NEVER-OBSERVED too
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

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


def observed_states(records_root) -> set[str]:
    """Every record state this system can PROVE it has reached. READ-ONLY.

    A missing root yields an empty set rather than an error, and — importantly —
    is not created on the way past: a reporter that materialises the directory
    it is measuring has changed the answer. A single unreadable record is
    skipped rather than fatal, for the reason `reconcile.reconcile` gives: one
    corrupt file must not strand the other 866.
    """
    root = Path(records_root)
    seen: set[str] = set()
    if not root.is_dir():
        return seen
    for path in sorted(root.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(record, dict):
            seen |= states_evidenced_by(record)
    return seen


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


def exit_code(reports: dict, strict: bool = False) -> int:
    """1 on a broken chain; under `--strict`, also on an unexercised one.

    NEVER-OBSERVED is not an error by default: right after the labels are
    created it is the only honest answer. `--strict` is for the caller who has
    decided enough time has passed that "never used" is a failure.
    """
    if any(r["breaks"] for r in reports.values()):
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

    observed = observed_states(args.records) if args.records else None

    out = {}
    for repo in ([args.repo] if args.repo else list(DEFAULT_REPOS)):
        issues, vocab = fetch(repo)
        out[repo] = chain_report(issues, vocab, observed)

    if args.json:
        print(json.dumps(out, indent=2))
        return exit_code(out, args.strict)

    for repo, rep in out.items():
        print(f"\n\033[1m{repo}\033[0m  open={rep['total']}")
        for s in STAGES:
            st = rep["stages"][s]
            mark = {VOCAB_MISSING: "\033[31mNO LABEL\033[0m",
                    VOCAB_NEVER_OBSERVED: "\033[33mLABEL EXISTS, NEVER USED\033[0m",
                    VOCAB_NOT_MEASURED: "\033[2mnot measured here\033[0m",
                    VOCAB_PRESENT: ""}[st["vocabulary"]]
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

    if not any(r["records_consulted"] for r in out.values()):
        print("\n\033[33mNo records root given (--records): 'never observed' above "
              "rests on live labels alone, which forget. Records are the durable "
              "evidence that a stage was ever reached.\033[0m")

    print("\n\033[2mREAD-ONLY. `result` and `published` need a join against the "
          "licensed-run queue and the website; reported as not-measured rather "
          "than zero so an unbuilt join cannot read as 'nothing shipped'.\033[0m")
    return exit_code(out, args.strict)


if __name__ == "__main__":
    sys.exit(main())
