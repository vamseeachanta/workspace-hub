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

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from completeness_gate_check import (  # noqa: E402
    OPT_IN_LABEL, PLAN_APPROVED_LABEL, VERIFIED_LABEL,
    body_is_fresh, evaluate_close, gate_applies,
)
from label_authority import gh_json, parse_iso, verified_label_event  # noqa: E402

_RECORD_RE = re.compile(r"```completeness\s*(\{.*?\})\s*```", re.DOTALL)


def _parse_record(body: str) -> dict | None:
    m = _RECORD_RE.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None  # fail-closed: unparseable record => no record


def main() -> int:
    repo = os.environ.get("GH_REPO") or os.environ.get("REPO", "")
    issue = int(os.environ.get("ISSUE_NUMBER") or sys.argv[1])
    closing_actor = os.environ.get("CLOSING_ACTOR", "")

    data = gh_json("issue", "view", str(issue), "--repo", repo,
                   "--json", "body,labels,updatedAt") or {}
    labels = [l["name"] for l in data.get("labels", [])]

    # OPT-IN SCOPE FIRST: the gate only enforces on issues that explicitly opted in
    # (gate:completeness + status:plan-approved). Checking this BEFORE the owners config
    # means an unconfigured gate is inert for everything else — no retroactive disruption.
    if not gate_applies(labels):
        print(f"[completeness-gate] issue #{issue}: not opted in ({OPT_IN_LABEL}+{PLAN_APPROVED_LABEL}) "
              f"— gate not applicable, ALLOW", file=sys.stderr)
        return 0

    owners = {a.strip() for a in os.environ.get("COMPLETENESS_OWNERS", "").split(",") if a.strip()}
    if not owners:
        print(f"[completeness-gate] issue #{issue}: CONFIG ERROR — opted-in but COMPLETENESS_OWNERS "
              "repo variable is unset; set it (comma-separated logins).", file=sys.stderr)
        return 1

    record = _parse_record(data.get("body", ""))
    label_actor, label_at = verified_label_event(repo, issue, VERIFIED_LABEL)
    # Freshness anchors on the BODY edit time (lastEditedAt), NOT updatedAt — the close
    # itself bumps updatedAt past the label and would falsely fail freshness (fix #5).
    owner, name = repo.split("/", 1)
    ts = gh_json("api", "graphql", "-f", f'query={{repository(owner:"{owner}",name:"{name}")'
                  f'{{issue(number:{issue}){{lastEditedAt createdAt}}}}}}') or {}
    issue_ts = (((ts.get("data") or {}).get("repository") or {}).get("issue")) or {}
    body_verified_fresh = body_is_fresh(
        label_at, parse_iso(issue_ts.get("lastEditedAt")), parse_iso(issue_ts.get("createdAt")))

    require_separate = os.environ.get("COMPLETENESS_REQUIRE_SEPARATE_CLOSER", "").lower() in ("1", "true", "yes")
    decision = evaluate_close(
        record=record, labels=labels, label_actor=label_actor,
        closing_actor=closing_actor, authorized_appliers=owners,
        expected_issue=issue, body_verified_fresh=body_verified_fresh,
        require_separate_closer=require_separate,
    )
    print(f"[completeness-gate] issue #{issue}: "
          f"{'ALLOW' if decision.allowed else 'DENY'} — {decision.reason}", file=sys.stderr)
    return 0 if decision.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
