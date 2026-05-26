#!/usr/bin/env python3
"""I/O wrapper around the #2798 close-gate decision (hardened per code review).

Gathers issue context via ``gh`` and calls the pure, unit-tested
``completeness_gate_check.evaluate_close``. Exit 0 = close allowed; exit 1 = denied
(the GitHub Action reopens + comments; the advisory pre-flight just warns).

Hardening:
- only enforces issues that reached implementation (`status:plan-approved`); un-planned
  closes are not gated (closes the over-scope MAJOR);
- computes ``body_verified_fresh`` = verified-label applied at/after the issue body's
  last edit, so editing the body after verification invalidates the label (Codex#1);
- binds via ``expected_issue``; threshold comes from server-side config, not the record.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from completeness_gate_check import VERIFIED_LABEL, evaluate_close  # noqa: E402

_RECORD_RE = re.compile(r"```completeness\s*(\{.*?\})\s*```", re.DOTALL)
PLAN_APPROVED = "status:plan-approved"


def _gh_json(*args: str):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip() else None


def _parse_iso(ts: str | None):
    if not ts:
        return None
    return _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _parse_record(body: str) -> dict | None:
    m = _RECORD_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None  # fail-closed: unparseable record => no record


def _verified_label_event(repo: str, issue: int):
    """(actor, applied_at) for the most recent application of the verified label."""
    events = _gh_json("api", f"repos/{repo}/issues/{issue}/timeline",
                      "--paginate", "-H", "Accept: application/vnd.github+json") or []
    actor, applied_at = None, None
    for ev in events:
        if ev.get("event") == "labeled" and (ev.get("label") or {}).get("name") == VERIFIED_LABEL:
            actor = (ev.get("actor") or {}).get("login")
            applied_at = _parse_iso(ev.get("created_at"))
    return actor, applied_at


def main() -> int:
    repo = os.environ.get("GH_REPO") or os.environ.get("REPO", "")
    issue = int(os.environ.get("ISSUE_NUMBER") or sys.argv[1])
    closing_actor = os.environ.get("CLOSING_ACTOR", "")
    owners = {a.strip() for a in os.environ.get("COMPLETENESS_OWNERS", "").split(",") if a.strip()}
    if not owners:
        print("[completeness-gate] CONFIG ERROR: COMPLETENESS_OWNERS repo variable is unset — "
              "set it (comma-separated logins) or every close will be blocked.", file=sys.stderr)
        return 1

    data = _gh_json("issue", "view", str(issue), "--repo", repo,
                    "--json", "body,labels,updatedAt") or {}
    labels = [l["name"] for l in data.get("labels", [])]

    # not gated: issues that never reached implementation
    if PLAN_APPROVED not in labels:
        print(f"[completeness-gate] issue #{issue}: not {PLAN_APPROVED} — completeness gate not applicable, ALLOW",
              file=sys.stderr)
        return 0

    record = _parse_record(data.get("body", ""))
    label_actor, label_at = _verified_label_event(repo, issue)
    body_edited_at = _parse_iso(data.get("updatedAt"))
    body_verified_fresh = bool(label_at and body_edited_at and label_at >= body_edited_at)

    decision = evaluate_close(
        record=record, labels=labels, label_actor=label_actor,
        closing_actor=closing_actor, authorized_appliers=owners,
        expected_issue=issue, body_verified_fresh=body_verified_fresh,
    )
    print(f"[completeness-gate] issue #{issue}: "
          f"{'ALLOW' if decision.allowed else 'DENY'} — {decision.reason}", file=sys.stderr)
    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
