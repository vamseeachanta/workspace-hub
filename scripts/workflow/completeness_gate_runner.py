#!/usr/bin/env python3
"""I/O wrapper around the #2798 close-gate decision.

Gathers issue context via ``gh`` and calls the pure, unit-tested
``completeness_gate_check.evaluate_close``. Exit 0 = close allowed; exit 1 =
denied (the GitHub Action reopens + comments; the advisory pre-flight just warns).

This wrapper is I/O-bound and validated in CI (live close-revert), not under
pytest-socket — the decision it delegates to IS unit-tested.

Computed record source: a fenced ```completeness {json}``` block stamped on the
issue body (also mirrored to kanban `complete --metadata`). The verified-label
actor is read from the issue timeline's `labeled` events.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from completeness_gate_check import VERIFIED_LABEL, evaluate_close  # noqa: E402

_RECORD_RE = re.compile(r"```completeness\s*(\{.*?\})\s*```", re.DOTALL)


def _gh_json(*args: str):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip() else None


def _parse_record(body: str) -> dict | None:
    m = _RECORD_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _verified_label_actor(repo: str, issue: int) -> str | None:
    """Most recent actor who applied the verified label, from the timeline."""
    events = _gh_json("api", f"repos/{repo}/issues/{issue}/timeline",
                      "--paginate", "-H", "Accept: application/vnd.github+json") or []
    actor = None
    for ev in events:
        if ev.get("event") == "labeled" and (ev.get("label") or {}).get("name") == VERIFIED_LABEL:
            actor = (ev.get("actor") or {}).get("login")
    return actor


def main() -> int:
    repo = os.environ["GH_REPO"] if "GH_REPO" in os.environ else os.environ.get("REPO", "")
    issue = int(os.environ.get("ISSUE_NUMBER") or sys.argv[1])
    closing_actor = os.environ.get("CLOSING_ACTOR", "")
    owners = {a.strip() for a in os.environ.get("COMPLETENESS_OWNERS", "").split(",") if a.strip()}

    data = _gh_json("issue", "view", str(issue), "--repo", repo,
                    "--json", "body,labels") or {}
    labels = [l["name"] for l in data.get("labels", [])]
    record = _parse_record(data.get("body", ""))
    label_actor = _verified_label_actor(repo, issue)

    decision = evaluate_close(
        record=record, labels=labels, label_actor=label_actor,
        closing_actor=closing_actor, authorized_appliers=owners,
    )
    print(f"[completeness-gate] issue #{issue}: "
          f"{'ALLOW' if decision.allowed else 'DENY'} — {decision.reason}", file=sys.stderr)
    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
