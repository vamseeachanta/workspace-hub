#!/usr/bin/env python3
"""chain.py — traceability from issue to published capability (deckhand#584 §3).

READ-ONLY. Reports where the chain BREAKS, which is the requirement:
"surface where the chain breaks, not just where it completes — a result with no
capability is the interesting case."

## The distinction this tool is built around

A stage with zero occupancy has two completely different causes:

    UNREPRESENTABLE   the label does not exist — nothing COULD be here
    EMPTY             the label exists and nobody is in it

`executed: 0` invites "nothing has finished yet". If `dispatch:done` does not
exist, the truth is "finishing cannot be recorded" — a defect in the chain, not a
measurement of progress. Every stage therefore carries its vocabulary status, and
a missing one is reported as a break rather than a count.

## What it found on first run

`SCHEMA.yaml:125` documents `dispatch:<state>` as `ready | active | done`. Only
`dispatch:ready` exists. 867 open issues sit in it and cannot move, because the
next two states have no vocabulary.

Usage:
    chain.py                    # all default repos
    chain.py --repo owner/name
    chain.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

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

#: These stages cannot be determined from labels. `result` needs a join against
#: the licensed-run queue (queue/results/<id>.json); `published` needs the
#: aceengineer-website capability pages. Reported as NOT-MEASURED rather than
#: zero, because a zero here would be indistinguishable from "nothing shipped" —
#: the exact conflation this tool exists to prevent.
NOT_LABEL_BORNE = ("result", "published")

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


def chain_report(issues: list[dict], vocabulary: set[str]) -> dict:
    """Population per stage, plus the breaks. Pure: no IO."""
    counts = {s: 0 for s in STAGES}
    for iss in issues:
        counts[stage_of(iss)] += 1

    stages = {}
    for s in STAGES:
        if s in NOT_LABEL_BORNE:
            vocab = "not-measured"
        elif s in STAGE_MARKER:
            vocab = "present" if STAGE_MARKER[s] in vocabulary else "MISSING"
        else:
            vocab = "present"   # unassigned/assigned are label-presence, not a marker
        stages[s] = {"count": counts[s], "vocabulary": vocab}

    breaks = [
        {"stage": s, "kind": "unrepresentable",
         "detail": f"{STAGE_MARKER[s]} does not exist — nothing can reach this stage"}
        for s in STAGES if stages[s]["vocabulary"] == "MISSING"
    ]

    # The wall: the most-populated stage whose NEXT stage is unreachable. A
    # pile-up in front of a missing state is a different problem from a pile-up
    # in front of a busy one, and only the first is a vocabulary defect.
    wall = None
    for i, s in enumerate(STAGES[:-1]):
        nxt = STAGES[i + 1]
        if stages[nxt]["vocabulary"] == "MISSING" and counts[s] > 0:
            if wall is None or counts[s] > wall["count"]:
                wall = {"stage": s, "count": counts[s], "next_stage": nxt,
                        "next_stage_vocabulary": "MISSING"}

    return {"stages": stages, "breaks": breaks, "wall": wall, "total": len(issues)}


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out = {}
    for repo in ([args.repo] if args.repo else list(DEFAULT_REPOS)):
        issues, vocab = fetch(repo)
        out[repo] = chain_report(issues, vocab)

    if args.json:
        print(json.dumps(out, indent=2))
        return 1 if any(r["breaks"] for r in out.values()) else 0

    for repo, rep in out.items():
        print(f"\n\033[1m{repo}\033[0m  open={rep['total']}")
        for s in STAGES:
            st = rep["stages"][s]
            mark = {"MISSING": "\033[31mNO LABEL\033[0m",
                    "not-measured": "\033[2mnot measured here\033[0m",
                    "present": ""}[st["vocabulary"]]
            print(f"    {s:<12}{st['count']:>6}   {mark}")
        if rep["wall"]:
            w = rep["wall"]
            print(f"  \033[1;31mWALL: {w['count']} issue(s) at '{w['stage']}' — "
                  f"'{w['next_stage']}' has no label, so none can advance\033[0m")
        for b in rep["breaks"]:
            print(f"  \033[31mBREAK\033[0m {b['stage']}: {b['detail']}")

    print("\n\033[2mREAD-ONLY. `result` and `published` need a join against the "
          "licensed-run queue and the website; reported as not-measured rather "
          "than zero so an unbuilt join cannot read as 'nothing shipped'.\033[0m")
    return 1 if any(r["breaks"] for r in out.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
