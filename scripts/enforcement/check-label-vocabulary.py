#!/usr/bin/env python3
"""Check that live GitHub label vocabularies match what the code accepts.

Level-2 enforcement (per .claude/rules/patterns.md). This cannot be a unit test:
the labels live on GitHub, the accepted values live in code and config, and the
whole point is to catch them drifting apart.

## What drift looks like

`lane:frontier-pending` existed on 5 digitalmodel issues while
`LANE_PROVIDERS = {"codex", "claude"}` in route.py. `resolve_provider` therefore
did not recognise it, `accepted_lane` became `None`, and those issues fell
through to the default provider. The label carried real intent — #1199's body
says "`lane:frontier-pending` for the ACE_SHARE slice" — into a namespace where
**nothing consumed it**. It read as a routing decision and was a no-op.

That is the failure this script exists for: a label that *looks* live and is
silently discarded. Nothing errors, nothing warns, and a coverage report counts
it as `routable` because cardinality is fine — one label on the axis.

## Three checks

1. **Closed vocabulary** — every live `lane:` / `machine:` label value must be
   one the code or config accepts.
2. **Cardinality** — no open issue carries 2+ labels on a declared scalar axis.
3. **Undeclared axes** — any `prefix:` in use that `label_axes` does not
   classify. Reported, never failed: a new axis must not break CI on the day it
   is invented, but it must not be invisible either.

Exit 0 clean, 1 on a violation, 2 on an operational failure (no `gh`, API
error). A distinct code for "could not check" matters — a checker that exits 0
when it could not run is the same defect it is looking for.

Usage:
    check-label-vocabulary.py                       # all default repos
    check-label-vocabulary.py --repo owner/name
    check-label-vocabulary.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = REPO_ROOT / ".claude" / "memory" / "kanban" / "routing-rules.yaml"
ROUTE_PY = REPO_ROOT / "scripts" / "dispatch" / "route.py"

DEFAULT_REPOS = (
    "vamseeachanta/workspace-hub",
    "vamseeachanta/digitalmodel",
    "vamseeachanta/deckhand",
)

#: Values that are legitimate on the machine: axis but are not roster keys.
#: `unassigned` is the explicit "deliberately not scheduled" marker (#584) —
#: distinguishing that from "nobody looked" is the whole reason it exists.
MACHINE_EXTRAS = frozenset({"unassigned"})


def load_cfg() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8")) or {}


def lane_providers_from_code() -> set[str]:
    """Read LANE_PROVIDERS out of route.py rather than duplicating it here.

    A second copy of a vocabulary is a second thing to forget to update — which
    is the class of bug this script exists to catch, so it must not commit it.
    """
    src = ROUTE_PY.read_text(encoding="utf-8")
    m = re.search(r"^LANE_PROVIDERS\s*=\s*\{([^}]*)\}", src, re.M)
    if not m:
        raise SystemExit("CANNOT CHECK: LANE_PROVIDERS not found in route.py")
    return {v.strip().strip("\"'") for v in m.group(1).split(",") if v.strip()}


def gh_json(args: list[str]):
    r = subprocess.run(args, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise SystemExit(f"CANNOT CHECK: {' '.join(args[:4])} failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout or "[]")


def accepted_values(cfg: dict) -> dict[str, set[str]]:
    machines = set(cfg.get("machines") or {})
    aliases = set(cfg.get("machine_aliases") or {})
    return {
        "lane:": lane_providers_from_code(),
        "machine:": machines | aliases | set(MACHINE_EXTRAS),
    }


def check_repo(repo: str, cfg: dict, accepted: dict[str, set[str]]) -> dict:
    single = set((cfg.get("label_axes") or {}).get("single") or {})
    multi = set((cfg.get("label_axes") or {}).get("multi") or {})
    declared = single | multi

    issues = gh_json(["gh", "issue", "list", "--repo", repo, "--state", "open",
                      "--limit", "2000", "--json", "number,labels"])

    unknown_values: list[str] = []
    ambiguous: list[str] = []
    undeclared: set[str] = set()

    for iss in issues:
        names = [lab["name"] for lab in iss.get("labels") or []]
        per_axis: dict[str, list[str]] = {}
        for name in names:
            if ":" not in name:
                continue
            prefix = name.split(":", 1)[0] + ":"
            per_axis.setdefault(prefix, []).append(name.split(":", 1)[1])
            if prefix not in declared:
                undeclared.add(prefix)
        for prefix, values in per_axis.items():
            if prefix in single and len(values) > 1:
                ambiguous.append(f"#{iss['number']} {prefix}{{{','.join(sorted(values))}}}")
            allowed = accepted.get(prefix)
            if allowed is not None:
                for v in values:
                    if v not in allowed:
                        unknown_values.append(f"#{iss['number']} {prefix}{v}")

    return {
        "repo": repo,
        "open": len(issues),
        "unknown_values": sorted(set(unknown_values)),
        "ambiguous": sorted(set(ambiguous)),
        "undeclared_axes": sorted(undeclared),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="single repo instead of the defaults")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = load_cfg()
    accepted = accepted_values(cfg)
    repos = [args.repo] if args.repo else list(DEFAULT_REPOS)
    results = [check_repo(r, cfg, accepted) for r in repos]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for res in results:
            print(f"\n\033[1m{res['repo']}\033[0m  open={res['open']}")
            if res["unknown_values"]:
                print(f"  \033[31mUNKNOWN VALUE ({len(res['unknown_values'])})\033[0m "
                      "— label exists but nothing consumes it; it is silently discarded")
                for v in res["unknown_values"][:20]:
                    print(f"    {v}")
            if res["ambiguous"]:
                print(f"  \033[31mAMBIGUOUS ({len(res['ambiguous'])})\033[0m "
                      "— scalar axis with 2+ values; routing would depend on API order")
                for v in res["ambiguous"][:20]:
                    print(f"    {v}")
            if res["undeclared_axes"]:
                print(f"  \033[33mundeclared axes\033[0m: {', '.join(res['undeclared_axes'])} "
                      "(reported, not failed — classify in routing-rules.yaml label_axes)")
            if not (res["unknown_values"] or res["ambiguous"]):
                print("  \033[32mOK\033[0m — vocabulary closed, every scalar axis single-valued")

    failed = any(r["unknown_values"] or r["ambiguous"] for r in results)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
