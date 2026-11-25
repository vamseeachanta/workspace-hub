#!/usr/bin/env python3
"""Tier a host baseline into a cleanup plan; optionally apply the safe tiers (#4532).

    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots D:/ws C:/ws-pm
    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots ... \
        --apply --this-host <label> --log <private log.jsonl> [--tiers regenerable,safe-checkout]

Tiers:
  regenerable    package caches the tool can rebuild (uv, pip, npm, yarn, pnpm, pytest temp)
  safe-checkout  linked worktree, no local changes, HEAD on a remote (or in a named archive),
                 not locked; removed with an unforced `git worktree remove`, which itself
                 refuses dirty or locked worktrees
  review         everything that needs a person: dirty or local-only checkouts, stray leak
                 folders, large untracked data idle > 30 days, model caches
  other-tenant   outside --own-roots (shared hosts): reported, never touched
  keep           locked worktrees

Only `regenerable` and `safe-checkout` can be applied. Apply refuses to run unless the
baseline's label equals --this-host, and appends one JSON line per action to --log.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

GB = 1024 ** 3
APPLYABLE = {"regenerable", "safe-checkout"}
PACKAGE_CACHES = {"uv", "pip", "npm", "yarn", "pnpm", "pytest-tmp"}
REVIEW_CACHES = {"huggingface", "torch", "conda-pkgs", "playwright", "cargo-registry",
                 "go-mod", "gradle", "maven"}
LEAK_REASONS = {"posix-path-leak", "drive-letter-mirror", "test-fixture-leak"}
BIG_DATA_BYTES = 10 * GB
IDLE_DAYS = 30


def norm(path: str, windows: bool) -> str:
    p = path.replace("\\", "/").rstrip("/")
    return p.lower() if windows else p


def under(path: str, roots: list[str], windows: bool) -> bool:
    p = norm(path, windows)
    return any(p == r or p.startswith(r + "/") for r in (norm(x, windows) for x in roots))


def item(tier, path, reason, action, nbytes=None):
    return {"tier": tier, "path": path, "reason": reason, "action": action, "bytes": nbytes}


def plan(doc: dict, own_roots: list[str], preserved: set | None = None) -> list[dict]:
    windows = doc.get("os") == "Windows"
    preserved = preserved or set()
    items = []

    for c in doc.get("caches", []):
        if c["name"] in PACKAGE_CACHES:
            items.append(item("regenerable", c["path"], f"{c['name']} package cache",
                              f"clean {c['name']} cache", c["bytes"]))
        elif c["name"] in REVIEW_CACHES and c["bytes"] >= 1 * GB:
            items.append(item("review", c["path"], f"{c['name']} cache: rebuild costs "
                              "downloads", "prune if unused", c["bytes"]))

    for co in doc.get("checkouts", []):
        path = co["path"]
        if not under(path, own_roots, windows):
            items.append(item("other-tenant", path, "checkout outside own roots", "none"))
            continue
        if co.get("error"):
            items.append(item("review", path, f"unreadable: {co['error']}", "inspect"))
            continue
        on_remote = co.get("head_on_remote") is True
        archived = (not on_remote) and co.get("head") in preserved
        clean = co.get("dirty") == 0 and co.get("stashes", 0) == 0
        if co["kind"] == "clone":
            if clean and on_remote:
                continue  # canonical or duplicate clone with nothing local: kept, not listed
            items.append(item("review", path, f"clone: {co.get('dirty')} uncommitted, "
                              f"HEAD on remote={on_remote}", "push or archive, then decide"))
            continue
        if co.get("locked"):
            items.append(item("keep", path, "worktree is locked", "none"))
        elif clean and (on_remote or archived):
            why = "HEAD in a named archive" if archived else "HEAD on a remote"
            items.append(item("safe-checkout", path, f"clean worktree, {why}",
                              "git worktree remove (unforced)"))
        else:
            items.append(item("review", path, f"worktree: {co.get('dirty')} uncommitted, "
                              f"HEAD on remote={on_remote}", "commit+push or bundle, then remove"))

    for s in doc.get("stray", []):
        if not under(s["path"], own_roots, windows):
            items.append(item("other-tenant", s["path"], s["reason"], "none", s.get("bytes")))
        elif s["reason"] in LEAK_REASONS:
            items.append(item("review", s["path"], s["reason"],
                              "move anything worth keeping into a repo or the data store, "
                              "then remove", s.get("bytes")))
        else:
            items.append(item("review", s["path"], s["reason"], "decide a home",
                              s.get("bytes")))

    gen = datetime.strptime(doc["generated_utc"], "%Y-%m-%dT%H:%M:%SZ")
    cutoff = (gen - timedelta(days=IDLE_DAYS)).strftime("%Y-%m-%d")
    listed = {norm(i["path"], windows) for i in items}
    big = []
    for scan in doc.get("roots", []):
        for d in scan["dirs"]:
            if (d["git"] or d["bytes"] < BIG_DATA_BYTES or not d.get("newest_utc")
                    or d["newest_utc"][:10] >= cutoff or not under(d["path"], own_roots, windows)):
                continue
            big.append(d)
    big.sort(key=lambda d: d["depth"])
    for d in big:
        p = norm(d["path"], windows)
        if any(p == q or p.startswith(q + "/") for q in listed):
            continue
        listed.add(p)
        items.append(item("review", d["path"], f"untracked data, idle since "
                          f"{d['newest_utc'][:10]}", "data store (manifest-and-fetch) or "
                          "delete with owner", d["bytes"]))
    order = ["regenerable", "safe-checkout", "review", "keep", "other-tenant"]
    items.sort(key=lambda i: (order.index(i["tier"]), -(i["bytes"] or 0), i["path"]))
    return items


def render(doc: dict, items: list[dict]) -> str:
    lines = [f"# Cleanup plan: {doc['label']} (baseline {doc['generated_utc']})", "",
             "| Tier | Path | GB | Reason | Action |", "|---|---|---:|---|---|"]
    for i in items:
        size = "-" if i["bytes"] is None else f"{i['bytes'] / GB:,.1f}"
        lines.append(f"| {i['tier']} | `{i['path']}` | {size} | {i['reason']} | {i['action']} |")
    totals = {}
    for i in items:
        totals[i["tier"]] = totals.get(i["tier"], 0) + (i["bytes"] or 0)
    lines += ["", "Totals (GB, sized items only): " + ", ".join(
        f"{k} {v / GB:,.1f}" for k, v in totals.items())]
    return "\n".join(lines) + "\n"


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout + p.stderr).strip()[-500:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, str(exc)


def apply_item(i: dict) -> tuple[str, str]:
    path = i["path"]
    if i["tier"] == "safe-checkout":
        rc, common = run_cmd(["git", "-C", path, "rev-parse", "--path-format=absolute",
                              "--git-common-dir"])
        if rc:
            return "skipped", f"not a git worktree: {common}"
        main = str(Path(common.splitlines()[-1]).parent)
        rc, out = run_cmd(["git", "-C", main, "worktree", "remove", path])
        return ("removed", out) if rc == 0 else ("refused", out)
    name = i["reason"].split()[0]
    if name == "pytest-tmp":
        shutil.rmtree(path, ignore_errors=True)
        return ("removed", "") if not os.path.exists(path) else ("partial", "files in use")
    cmds = {"uv": ["uv", "cache", "clean"], "pip": [sys.executable, "-m", "pip", "cache", "purge"],
            "npm": ["npm", "cache", "clean", "--force"], "yarn": ["yarn", "cache", "clean"],
            "pnpm": ["pnpm", "store", "prune"]}
    cmd = cmds.get(name)
    if not cmd or not shutil.which(cmd[0]):
        return "skipped", f"no tool for {name}"
    rc, out = run_cmd(cmd)
    return ("cleaned" if rc == 0 else "failed"), out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tier a host baseline into a cleanup plan.")
    ap.add_argument("baseline")
    ap.add_argument("--own-roots", nargs="+", required=True,
                    help="roots this team owns on the host; everything else is other-tenant")
    ap.add_argument("--preserved", help="file of commit SHAs held in a named archive "
                    "(for example the pre-lean bundles), one per line")
    ap.add_argument("--out", help="write the plan as JSON here")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--tiers", default="regenerable,safe-checkout")
    ap.add_argument("--this-host", help="label of the host running --apply")
    ap.add_argument("--log", help="append-only JSONL log of applied actions")
    args = ap.parse_args(argv)

    doc = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    preserved = set()
    if args.preserved:
        preserved = {line.strip() for line in
                     Path(args.preserved).read_text(encoding="utf-8").splitlines() if line.strip()}
    items = plan(doc, args.own_roots, preserved)
    if args.out:
        Path(args.out).write_text(json.dumps(items, indent=1), encoding="utf-8")
    if not args.apply:
        sys.stdout.write(render(doc, items))
        return 0

    tiers = {t.strip() for t in args.tiers.split(",") if t.strip()}
    if not tiers <= APPLYABLE:
        print(f"refused: only {sorted(APPLYABLE)} can be applied", file=sys.stderr)
        return 2
    if args.this_host != doc["label"]:
        print("refused: baseline label does not match --this-host", file=sys.stderr)
        return 2
    if not args.log:
        print("refused: --apply needs --log", file=sys.stderr)
        return 2
    with open(args.log, "a", encoding="utf-8") as log:
        for i in items:
            if i["tier"] not in tiers:
                continue
            result, detail = apply_item(i)
            rec = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "host": doc["label"], **i, "result": result, "detail": detail}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"{result:8} {i['tier']:14} {i['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
