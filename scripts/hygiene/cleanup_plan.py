#!/usr/bin/env python3
"""Tier a host baseline into a cleanup plan; optionally apply the safe tiers (#4532).

    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots D:/ws C:/ws-pm
    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots ... \
        --apply --this-host <label> --log <private log.jsonl> [--tiers regenerable,safe-checkout]

Tiers:
  regenerable    package caches with a path-bound clean command (uv, pip, npm) and this
                 user's pytest temp root when idle for a day
  safe-checkout  linked worktree, no changes, no ignored non-regenerable files, no stash,
                 HEAD on a remote (or in a named archive), not locked
  review         everything that needs a person
  other-tenant   outside --own-roots and the baseline user's home: reported, never touched
  keep           locked worktrees

The baseline only nominates candidates. --apply re-derives every safety fact on the live
host before acting: host identity (one-way hash, not the label), real-path containment,
HEAD unchanged since the plan, clean status including ignored files, and HEAD contained in
a freshly fetched remote ref or in the --preserved list given at apply time. Worktrees are
removed with an unforced `git worktree remove`. Each action appends one JSON line to --log.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

GB = 1024 ** 3
APPLYABLE = {"regenerable", "safe-checkout"}
BOUND_CACHES = {"uv", "pip", "npm"}          # clean command takes an explicit target
REVIEW_CACHES = {"huggingface", "torch", "conda-pkgs", "playwright", "cargo-registry",
                 "go-mod", "gradle", "maven", "yarn", "pnpm"}
LEAK_REASONS = {"posix-path-leak", "drive-letter-mirror", "test-fixture-leak"}
BIG_DATA_BYTES = 10 * GB
IDLE_DAYS = 30
PYTEST_IDLE = timedelta(days=1)


def _collector():
    spec = importlib.util.spec_from_file_location(
        "host_baseline", Path(__file__).resolve().parent / "host_baseline.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HB = _collector()
GIT_ENV = dict(HB.GIT_ENV)  # GIT_* bindings (GIT_DIR, GIT_INDEX_FILE, ...) already removed


# ---------------------------------------------------------------- path rules (planning)

def is_absolute(path: str, windows: bool) -> bool:
    return bool(re.match(r"^[A-Za-z]:/", path)) if windows else path.startswith("/")


def norm(path: str, windows: bool) -> str:
    # On POSIX a backslash is a literal filename character, so it is left alone.
    p = path.replace("\\", "/") if windows else path
    p = p.rstrip("/") or "/"
    return p.lower() if windows else p


def unsafe_path(path: str, windows: bool) -> str | None:
    if not is_absolute(norm(path, windows), windows):
        return "path is not absolute"
    if ".." in norm(path, windows).split("/"):
        return "path contains '..'"
    return None


def under(path: str, roots: list[str], windows: bool) -> bool:
    p = norm(path, windows)
    for r in roots:
        r = norm(r, windows)
        if p == r or p.startswith(r.rstrip("/") + "/"):
            return True
    return False


def item(tier, path, reason, action, nbytes=None, **extra):
    return {"tier": tier, "path": path, "reason": reason, "action": action,
            "bytes": nbytes, **extra}


# ---------------------------------------------------------------- planning

def plan(doc: dict, own_roots: list[str], preserved: set | None = None) -> list[dict]:
    windows = doc.get("os") == "Windows"
    preserved = preserved or set()
    mine = list(own_roots) + ([doc["home"]] if doc.get("home") else [])
    gen = datetime.strptime(doc["generated_utc"], "%Y-%m-%dT%H:%M:%SZ")
    items = []

    for c in doc.get("caches", []):
        name, path = c["name"], c["path"]
        if name == "temp-dir" or c.get("linked"):
            continue
        if unsafe_path(path, windows) or not under(path, mine, windows):
            items.append(item("other-tenant", path, f"{name} cache outside own roots", "none",
                              c["bytes"]))
        elif name in BOUND_CACHES:
            items.append(item("regenerable", path, f"{name} package cache",
                              f"clean {name} cache (path-bound)", c["bytes"], cache=name))
        elif name == "pytest-tmp":
            newest = c.get("newest_utc")
            idle = newest is None or datetime.strptime(newest, "%Y-%m-%dT%H:%M:%SZ") < gen - PYTEST_IDLE
            if idle and not c.get("denied"):
                items.append(item("regenerable", path, "pytest temp root, idle >1 day",
                                  "remove (no link, no mount crossing)", c["bytes"],
                                  cache=name))
            else:
                items.append(item("review", path, "pytest temp root in recent use or "
                                  "partly unreadable", "leave", c["bytes"]))
        elif name in REVIEW_CACHES and c["bytes"] >= 1 * GB:
            items.append(item("review", path, f"{name} cache: no path-bound clean or "
                              "costly to rebuild", "prune if unused", c["bytes"]))

    checkout_paths = []
    for co in doc.get("checkouts", []):
        path = co["path"]
        checkout_paths.append(norm(path, windows))
        bad = unsafe_path(path, windows)
        if bad:
            items.append(item("review", path, f"unsafe path: {bad}", "inspect"))
            continue
        if not under(path, own_roots, windows):
            items.append(item("other-tenant", path, "checkout outside own roots", "none"))
            continue
        if co.get("error"):
            items.append(item("review", path, f"unreadable: {co['error']}", "inspect"))
            continue
        on_remote = co.get("head_on_remote") is True
        archived = (not on_remote) and bool(co.get("head")) and co.get("head") in preserved
        ignored = co.get("ignored_other")
        clean = (co.get("dirty") == 0 and co.get("stashes", 0) == 0 and ignored == 0)
        if co["kind"] == "clone":
            if clean and on_remote:
                continue  # nothing local: kept, not listed
            items.append(item("review", path, f"clone: {co.get('dirty')} uncommitted, "
                              f"{ignored} ignored non-regenerable, HEAD on remote={on_remote}",
                              "push or archive, then decide"))
            continue
        if co.get("locked"):
            items.append(item("keep", path, "worktree is locked", "none"))
        elif clean and (on_remote or archived) and co.get("head"):
            why = "HEAD in a named archive" if archived else "HEAD on a remote"
            items.append(item("safe-checkout", path, f"clean worktree, {why}",
                              "git worktree remove (unforced, re-verified)", head=co["head"]))
        else:
            sample = ", ".join(co.get("ignored_sample") or [])
            items.append(item("review", path, f"worktree: {co.get('dirty')} uncommitted, "
                              f"{ignored} ignored non-regenerable{' (' + sample + ')' if sample else ''}, "
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

    cutoff = (gen - timedelta(days=IDLE_DAYS)).strftime("%Y-%m-%d")
    listed = {norm(i["path"], windows) for i in items}

    def inside(p: str, pool) -> bool:
        return any(p == q or p.startswith(q.rstrip("/") + "/") for q in pool)

    big = []
    for scan in doc.get("roots", []):
        for d in scan["dirs"]:
            p = norm(d["path"], windows)
            if (d["git"] or d["bytes"] < BIG_DATA_BYTES or d.get("denied")
                    or not d.get("newest_utc") or d["newest_utc"][:10] >= cutoff
                    or not under(d["path"], own_roots, windows)
                    or inside(p, checkout_paths)):  # checkout contents may be tracked
                continue
            big.append(d)
    big.sort(key=lambda d: d["depth"])
    for d in big:
        p = norm(d["path"], windows)
        if inside(p, listed):
            continue
        listed.add(p)
        items.append(item("review", d["path"], f"data outside any checkout, idle since "
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


# ---------------------------------------------------------------- apply (live checks)

def run_cmd(cmd: list[str], env=None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, env=env or GIT_ENV,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout + p.stderr).strip()[-500:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, str(exc)


def real_inside(path: str, roots: list[str]) -> bool:
    """Containment by resolved real path, so a junction or symlink cannot alias out."""
    rp = os.path.normcase(os.path.realpath(path))
    for r in roots:
        rr = os.path.normcase(os.path.realpath(r))
        if rp == rr or rp.startswith(rr.rstrip(os.sep) + os.sep):
            return True
    return False


def git(path: str, *args: str) -> tuple[int, str]:
    return run_cmd(["git", "-c", "safe.directory=*", "-C", path, *args])


def verify_and_remove_worktree(i: dict, preserved: set) -> tuple[str, str]:
    path = i["path"]
    if HB.is_link_path(path):
        return "refused", "path is a link"
    rc, head = git(path, "rev-parse", "HEAD")
    if rc or head.strip() != i.get("head"):
        return "refused", "HEAD changed since the plan or unreadable"
    rc, gd = git(path, "rev-parse", "--path-format=absolute", "--git-dir")
    rc2, common = git(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if rc or rc2 or os.path.normcase(gd.strip()) == os.path.normcase(common.strip()):
        return "refused", "not a linked worktree"
    if HB.worktree_lock_state(path):
        return "refused", "worktree is locked"
    rc, status = git(path, "status", "--porcelain=v1", "--untracked-files=normal")
    if rc or status.strip():
        return "refused", "worktree has changes"
    try:
        if HB.ignored_unregenerable(path):
            return "refused", "ignored non-regenerable files present"
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        return "refused", f"ignored-file check failed: {exc}"
    main = str(Path(common.strip()).parent)
    if head.strip() not in preserved:
        rc, out = git(main, "fetch", "--prune", "--quiet", "origin")
        if rc:
            return "refused", f"fetch failed, remote containment unverified: {out}"
        rc, refs = git(path, "for-each-ref", "--count=1", "--contains", "HEAD",
                       "--format=%(refname)", "refs/remotes/origin")
        if rc or not refs.strip():
            return "refused", "HEAD not in any freshly fetched origin ref"
    rc, out = git(main, "worktree", "remove", path)
    return ("removed", out) if rc == 0 else ("refused", out)


def guarded_rmtree(root: str) -> tuple[str, str]:
    """Remove a tree bottom-up without following links or crossing a mount boundary.

    Refuses the whole operation before deleting anything if any directory lies on a
    different device than the root.
    """
    if HB.is_link_path(root):
        return "refused", "root is a link"
    dev = os.lstat(root).st_dev
    order, stack = [], [root]
    while stack:
        cur = stack.pop()
        order.append(cur)
        with os.scandir(cur) as it:
            for e in it:
                if HB.is_link_entry(e):
                    continue
                st = e.stat(follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode):
                    if os.name != "nt" and st.st_dev != dev:
                        return "refused", "mount boundary inside tree"
                    stack.append(e.path)
    errors = []
    for d in reversed(order):
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if HB.is_link_entry(e):
                            # remove the link node itself, never its target
                            os.rmdir(e.path) if (os.name == "nt" and e.is_dir()) else os.unlink(e.path)
                        elif not e.is_dir(follow_symlinks=False):
                            os.unlink(e.path)
                    except OSError as exc:
                        errors.append(f"{e.name}: {exc.strerror}")
            os.rmdir(d)
        except OSError as exc:
            errors.append(f"{os.path.basename(d)}: {exc.strerror}")
    return ("removed", "") if not errors else ("partial", "; ".join(errors[:5]))


def cache_command(name: str, path: str):
    """Command and environment bound to exactly the planned cache path."""
    import shutil
    env = dict(os.environ)
    if name == "uv" and shutil.which("uv"):
        return [shutil.which("uv"), "cache", "clean", "--cache-dir", path], env
    if name == "pip":
        env["PIP_CACHE_DIR"] = path
        return [sys.executable, "-m", "pip", "cache", "purge"], env
    if name == "npm" and shutil.which("npm"):
        base = str(Path(path).parent) if Path(path).name == "_cacache" else path
        return [shutil.which("npm"), "cache", "clean", "--force", "--cache", base], env
    return None, env


def apply_item(i: dict, preserved: set) -> tuple[str, str]:
    if i["tier"] == "safe-checkout":
        return verify_and_remove_worktree(i, preserved)
    if i.get("cache") == "pytest-tmp":
        return guarded_rmtree(i["path"])
    cmd, env = cache_command(i.get("cache", ""), i["path"])
    if not cmd:
        return "skipped", "no path-bound command for this cache"
    rc, out = run_cmd(cmd, env=env)
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
    if doc.get("host_id") != HB.host_id():
        print("refused: baseline host_id does not match the executing host", file=sys.stderr)
        return 2
    if not args.log:
        print("refused: --apply needs --log", file=sys.stderr)
        return 2
    roots = list(args.own_roots) + ([doc["home"]] if doc.get("home") else [])
    with open(args.log, "a", encoding="utf-8") as log:
        for i in items:
            if i["tier"] not in tiers:
                continue
            if not real_inside(i["path"], roots):
                result, detail = "refused", "real path outside own roots"
            else:
                result, detail = apply_item(i, preserved)
            rec = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "host": doc["label"], **i, "result": result, "detail": detail}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"{result:8} {i['tier']:14} {i['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
