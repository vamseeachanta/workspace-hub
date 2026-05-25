#!/usr/bin/env python3
"""dispatch.py — write per-machine queue files + show capacity (supply vs demand).

Consumes route.py's proposals and materializes git-tracked queue files at
.claude/dispatch/<machine>.yaml. Each machine's Claude/Codex session drains
its OWN queue file — pull-based, no SSH, no daemon, no auto-spawn. This matches
the cross-machine-via-git pattern and keeps the runaway-pipeline door shut.

SAFETY: default is dry-run (prints what it would write). `--write` materializes
the queue files (Phase B). It still NEVER spawns a worker.

Usage:
  dispatch.py                 dry-run: show queue files that would be written
  dispatch.py --write         materialize .claude/dispatch/<machine>.yaml
  dispatch.py --capacity      supply (live agents) vs demand (assigned cards)
"""
from __future__ import annotations
import argparse, subprocess, sys, types
from collections import defaultdict
from pathlib import Path

import route  # sibling module — reuses repo_root(), propose(), load_rules()

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required")

ROOT = route.ROOT
DISPATCH_DIR = ROOT / ".claude/dispatch"


def get_proposals(repo=None):
    args = types.SimpleNamespace(repo=repo)
    return route.propose(args)


def build_queues(proposals):
    """Full per-machine BACKLOG: every assigned card goes into its machine's
    queue. `wip_eligible` flags the cards a session may claim NOW (within the
    WIP cap); the rest wait in the same file. WIP is enforced at claim time by
    the consuming session, not by truncating the queue."""
    queues = defaultdict(list)
    for p in proposals:
        queues[p["machine"]].append({
            "gh": p["key"].replace("gh:", ""),
            "repo": p["repo"],
            "domain": p["domain"],
            "provider": p["provider"],
            "title": p["title"],
            "url": p["url"],
            "dispatch_status": "ready",
            "wip_eligible": p["slot"] == "active-eligible",
            "routed_by": p["routed_by"],
        })
    return queues


def cmd_build(write: bool):
    proposals = get_proposals()
    queues = build_queues(proposals)
    print(f"\n\033[1mQueue files\033[0m ({'WRITING' if write else 'dry-run'}) "
          f"-> {DISPATCH_DIR.relative_to(ROOT)}/")
    for machine in sorted(queues):
        cards = queues[machine]
        elig = sum(1 for c in cards if c["wip_eligible"])
        print(f"  {machine:<16} {len(cards):>4} backlog  ({elig} wip-eligible now)")
        if write:
            DISPATCH_DIR.mkdir(parents=True, exist_ok=True)
            payload = {"machine": machine, "generated_by": "dispatch.py",
                       "cards": cards}
            with open(DISPATCH_DIR / f"{machine}.yaml", "w") as f:
                yaml.safe_dump(payload, f, sort_keys=False, width=100)
    if not write:
        print("\n\033[2mDRY-RUN — no files written. Re-run with --write (Phase B).\033[0m")
    else:
        print(f"\n\033[32mWrote {len(queues)} queue file(s).\033[0m "
              "Each machine drains its own; nothing was spawned.")


def live_agents_by_provider():
    """Best-effort supply signal: live claude/codex/hermes processes on THIS box."""
    counts = defaultdict(int)
    def n(pattern, exclude=None):
        out = subprocess.run(["pgrep", "-af", pattern], capture_output=True, text=True)
        lines = [l for l in out.stdout.splitlines()
                 if (exclude is None or exclude not in l)]
        return len(lines)
    counts["claude"] = len(subprocess.run(["pgrep", "-x", "claude"],
                                          capture_output=True, text=True).stdout.split())
    counts["codex"] = n("bin/codex", exclude="codex-update-manager")
    counts["hermes"] = n("tui_gateway.slash_worker")
    return counts


def cmd_capacity():
    proposals = get_proposals()
    # demand: assigned cards per machine/provider (active-eligible = ready now)
    demand_m = defaultdict(int); ready_m = defaultdict(int)
    demand_p = defaultdict(int)
    for p in proposals:
        demand_m[p["machine"]] += 1
        demand_p[p["provider"]] += 1
        if p["slot"] == "active-eligible":
            ready_m[p["machine"]] += 1
    cfg = route.load_rules()
    caps = cfg.get("wip_caps", {}).get("per_machine", {})

    print("\n\033[1mCapacity — demand vs WIP cap (per machine)\033[0m")
    print(f"  {'machine':<16}{'assigned':>9}{'ready-now':>11}{'wip-cap':>9}")
    print("  " + "─" * 43)
    for m in sorted(demand_m):
        print(f"  {m:<16}{demand_m[m]:>9}{ready_m[m]:>11}{caps.get(m, '–'):>9}")

    print("\n\033[1mSupply — live agents on this box (ace-linux-1)\033[0m")
    supply = live_agents_by_provider()
    for prov in ("claude", "codex", "hermes"):
        print(f"  {prov:<8} live={supply.get(prov,0):<3} demand={demand_p.get(prov,0)}")
    note = cfg.get("budget_pools", {}).get("codex_pool", {})
    print(f"\n  \033[2mnote: codex+hermes share one budget pool "
          f"(max_concurrent={note.get('max_concurrent','?')}); "
          f"gemini is manual-only.\033[0m")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--capacity", action="store_true")
    args = ap.parse_args()
    if args.capacity:
        cmd_capacity()
    else:
        cmd_build(write=args.write)


if __name__ == "__main__":
    main()
