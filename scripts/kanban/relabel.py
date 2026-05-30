#!/usr/bin/env python3
"""relabel.py — safe, label-first kanban card migration (workspace-hub#2878).

Hermes kanban places a card by its GitHub issue's `domain:<name>` label
(reconcile.py target_board), and the */20 cron rebuilds every board's card list
from labels (git reset --hard origin -> reconcile). So the ONLY durable way to
move a card between sub-boards is to relabel its GitHub issue — hand-editing a
board YAML is clobbered within 20 minutes. This tool performs that relabel
SAFELY for a reviewed batch:

  * dry-run by DEFAULT — prints the exact (remove/add) plan per issue; --apply writes
  * removes obsolete `domain:` labels and enforces EXACTLY ONE `domain:` per issue
  * assigns a `domain:` when the issue has none
  * idempotent — an already-correct issue is a no-op (no gh call, no churn)
  * one repo per remap; epic children must each be listed explicitly (clusters do
    NOT move together automatically — reconcile routes every issue independently)
  * throttle/backoff on the GitHub "was submitted too quickly" secondary limit

Input: a remap YAML —
    repo: vamseeachanta/digitalmodel
    remap:
      - issue: 605
        domain: solver-orcaflex
      - issue: 500
        domain: solver-orcaflex

The planning core (plan_relabel) is pure; the gh calls are isolated behind an
injectable runner so the whole tool is hermetically testable.

Usage:
  relabel.py <remap.yaml>            dry-run plan
  relabel.py <remap.yaml> --apply    write the labels (gh)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: `uv run --with pyyaml`")


DOMAIN_PREFIX = "domain:"
_DOMAIN_RE = re.compile(r"^[a-z0-9-]+$")
_THROTTLE_RE = re.compile(r"submitted too quickly|secondary rate|rate limit", re.I)


def validate_domain(domain: str) -> bool:
    """A domain slug is lowercase alphanumerics + hyphens, no prefix/space/case."""
    return bool(domain) and bool(_DOMAIN_RE.match(domain))


def plan_relabel(labels: list[str], target_domain: str) -> dict:
    """Pure: the label delta to make `target_domain` the issue's ONLY domain.

    Removes every other `domain:` label (enforcing one-domain), adds the target
    only when absent (assign-missing + idempotent). Non-`domain:` labels are
    never touched. Returns {"add": [...], "remove": [...]}.
    """
    target = f"{DOMAIN_PREFIX}{target_domain}"
    existing_domains = [l for l in labels if l.startswith(DOMAIN_PREFIX)]
    remove = [l for l in existing_domains if l != target]
    add = [] if target in labels else [target]
    return {"add": add, "remove": remove}


def is_noop(plan: dict) -> bool:
    return not plan.get("add") and not plan.get("remove")


def _is_throttle(text: str) -> bool:
    return bool(_THROTTLE_RE.search(text or ""))


def apply_relabel(
    repo: str,
    issue: int,
    plan: dict,
    *,
    runner=subprocess.run,
    sleep=time.sleep,
    max_retries: int = 5,
    pace: float = 0.0,
) -> bool:
    """Apply one issue's label plan via `gh issue edit`, with throttle backoff.

    A no-op plan makes no gh call. A non-throttle error fails fast (no retry). A
    throttle ("was submitted too quickly") backs off exponentially and retries up
    to max_retries total attempts. Returns True on success.
    """
    if is_noop(plan):
        return True
    cmd = ["gh", "issue", "edit", str(issue), "--repo", repo]
    for lab in plan["add"]:
        cmd += ["--add-label", lab]
    for lab in plan["remove"]:
        cmd += ["--remove-label", lab]

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        r = runner(cmd, capture_output=True, text=True, check=False)
        if r.returncode == 0:
            if pace:
                sleep(pace)
            return True
        err = (r.stderr or "") + (r.stdout or "")
        if _is_throttle(err) and attempt < max_retries:
            sleep(min(60, 2 ** attempt))
            continue
        return False  # non-throttle error, or throttle on the final attempt
    return False


def load_remap(path: Path) -> dict:
    """Parse + validate a remap YAML. Raises on missing repo, non-int issue,
    invalid domain slug, or a duplicate issue (ambiguous target)."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    repo = data.get("repo")
    if not repo:
        raise ValueError("remap: missing 'repo'")
    seen: set[int] = set()
    out = []
    for entry in data.get("remap") or []:
        issue = entry.get("issue")
        domain = entry.get("domain")
        if not isinstance(issue, int):
            raise ValueError(f"remap: issue must be an int, got {issue!r}")
        if not validate_domain(domain or ""):
            raise ValueError(f"remap: invalid domain {domain!r} for issue #{issue}")
        if issue in seen:
            raise ValueError(f"remap: duplicate issue #{issue} (ambiguous target)")
        seen.add(issue)
        out.append({"issue": issue, "domain": domain})
    return {"repo": repo, "remap": out}


def fetch_labels(repo: str, issue: int, runner=subprocess.run) -> list[str]:
    """Live label set for an issue (don't trust the remap's possibly-stale view)."""
    r = runner(
        ["gh", "issue", "view", str(issue), "--repo", repo, "--json", "labels"],
        capture_output=True, text=True, check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f"gh issue view {issue} ({repo}) failed: {r.stderr.strip()}")
    data = json.loads(r.stdout or "{}")
    return [l.get("name") for l in data.get("labels", []) if l.get("name")]


def print_plan_table(repo: str, plans: list[tuple]) -> None:
    print(f"# relabel plan for {repo}  ({len(plans)} issue(s))")
    moved = 0
    for issue, domain, plan in plans:
        if is_noop(plan):
            print(f"  #{issue:<6} domain:{domain:<22} = already correct")
            continue
        moved += 1
        rem = ",".join(plan["remove"]) or "-"
        add = ",".join(plan["add"]) or "-"
        print(f"  #{issue:<6} -> domain:{domain:<22} +[{add}] -[{rem}]")
    print(f"# {moved} change(s), {len(plans) - moved} already-correct")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Label-first kanban card migration (#2878)")
    ap.add_argument("remap", help="path to a remap YAML (repo + issue->domain list)")
    ap.add_argument("--apply", action="store_true", help="write labels via gh (default: dry-run)")
    ap.add_argument("--pace", type=float, default=0.5, help="seconds to sleep between writes")
    ap.add_argument("--max-retries", type=int, default=5, help="throttle-retry attempts per issue")
    args = ap.parse_args(argv)

    spec = load_remap(Path(args.remap))
    repo = spec["repo"]

    plans = []
    for entry in spec["remap"]:
        labels = fetch_labels(repo, entry["issue"])
        plans.append((entry["issue"], entry["domain"], plan_relabel(labels, entry["domain"])))

    print_plan_table(repo, plans)

    if not args.apply:
        print("DRY-RUN: no labels written (use --apply)")
        return 0

    fails = 0
    for issue, _domain, plan in plans:
        if is_noop(plan):
            continue
        if not apply_relabel(repo, issue, plan, max_retries=args.max_retries, pace=args.pace):
            fails += 1
            print(f"  FAILED to relabel #{issue}", file=sys.stderr)
    print(f"# applied; {fails} failure(s)")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
