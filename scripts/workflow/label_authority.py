#!/usr/bin/env python3
"""Shared label-actor-authority helpers (#2817).

Generalized — by parameterizing the label name — from #2798's
``completeness_gate_runner._verified_label_event`` so BOTH the completeness-close gate
and the plan-approval merge gate resolve "who applied this label, and when" through one
audited primitive. This module is a pure I/O wrapper + timeline resolver; it makes NO
policy decisions (authorization / freshness / threshold) — callers own those, so the
completeness gate's existing behavior is preserved unchanged.
"""

from __future__ import annotations

import datetime as _dt
import json
import subprocess


def gh_json(*args: str):
    """Run ``gh <args>`` and return parsed JSON (or None for empty output)."""
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip() else None


def parse_iso(ts: str | None):
    """Parse a GitHub ISO-8601 timestamp (``...Z``) to an aware datetime, or None."""
    if not ts:
        return None
    return _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def verified_label_event(repo: str, issue: int, label: str):
    """``(actor, applied_at)`` for the most recent application of ``label`` on ``issue``.

    Reads the issue **timeline** (audit-attributed). Returns ``(None, None)`` when the label
    was never applied — callers fail closed on that. ``unlabeled`` events are ignored: only
    a ``labeled`` event counts as an application. The timeline is chronological, so the last
    matching ``labeled`` event is the most recent application.
    """
    events = gh_json("api", f"repos/{repo}/issues/{issue}/timeline",
                     "--paginate", "-H", "Accept: application/vnd.github+json") or []
    actor, applied_at = None, None
    for ev in events:
        if ev.get("event") == "labeled" and (ev.get("label") or {}).get("name") == label:
            actor = (ev.get("actor") or {}).get("login")
            applied_at = parse_iso(ev.get("created_at"))
    return actor, applied_at
