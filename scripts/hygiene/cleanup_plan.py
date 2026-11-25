#!/usr/bin/env python3
"""Tier a host baseline into a cleanup plan; optionally apply the safe tiers (#4532).

    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots D:/ws C:/ws-pm
    python -I scripts/hygiene/cleanup_plan.py BASELINE.json --own-roots ... \
        --apply --this-host <label> --log <private log.jsonl> [--tiers regenerable,safe-checkout]

Tiers:
  regenerable    package caches with a path-bound clean command (uv, pip, npm); the
                 tool performs the deletion. Nothing is ever removed recursively here.
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
import math
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

GB = 1024 ** 3
APPLYABLE = {"regenerable", "safe-checkout"}
BOUND_CACHES = {"uv"}                        # path-bound, link-checked clean command
REVIEW_CACHES = {"huggingface", "torch", "conda-pkgs", "playwright", "cargo-registry",
                 "go-mod", "gradle", "maven", "yarn", "pnpm", "pip", "npm"}
LEAK_REASONS = {"posix-path-leak", "drive-letter-mirror", "test-fixture-leak"}
BIG_DATA_BYTES = 10 * GB
IDLE_DAYS = 30


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
        elif name == "pytest-tmp" and c["bytes"] >= 1 * GB:
            # Never applied: a run can start between plan and apply, and a recursive
            # delete cannot be made race-free against link swaps or bind mounts here.
            items.append(item("review", path, "pytest temp root (pytest keeps the last "
                              "three runs itself)", "remove by hand when no tests run",
                              c["bytes"]))
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
        if co.get("unborn"):
            items.append(item("review", path, "git repo with no commits (often test-fixture "
                              "residue)", "check for files worth keeping, then remove"))
            continue
        if co.get("error"):
            what = "broken .git" if co.get("broken") else "unreadable"
            items.append(item("review", path, f"{what}: {co['error']}", "inspect"))
            continue
        on_remote = co.get("head_on_remote") is True
        archived = (not on_remote) and bool(co.get("head")) and co.get("head") in preserved
        ignored = co.get("ignored_other")
        hidden = co.get("hidden_state")
        clean = (co.get("dirty") == 0 and co.get("stashes", 0) == 0 and ignored == 0
                 and hidden == [])
        if co["kind"] == "clone":
            if clean and on_remote and co.get("unpublished_commits") == 0:
                continue  # nothing local: kept, not listed
            items.append(item("review", path, f"clone: {co.get('dirty')} uncommitted, "
                              f"{ignored} ignored non-regenerable, "
                              f"{co.get('unpublished_commits')} unpublished commits, "
                              f"HEAD on remote={on_remote}"
                              f"{'; ' + '; '.join(hidden) if hidden else ''}",
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
                              f"HEAD on remote={on_remote}"
                              f"{'; ' + '; '.join(hidden) if hidden else ''}",
                              "commit+push or bundle, then remove"))

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

    gs = doc.get("git_scan") or {}
    git_roots = gs.get("roots", []) if gs.get("done") else []

    def holds_checkout(p: str) -> bool:
        return any(q.startswith(p.rstrip("/") + "/") for q in checkout_paths)

    big = []
    for scan in doc.get("roots", []):
        for d in scan["dirs"]:
            p = norm(d["path"], windows)
            if (d["git"] or d["bytes"] < BIG_DATA_BYTES or d.get("denied")
                    or not d.get("newest_utc") or d["newest_utc"][:10] >= cutoff
                    or not under(d["path"], own_roots, windows)
                    # positive evidence only: git discovery covered this path ...
                    or not under(d["path"], git_roots, windows)
                    # ... and it neither sits inside nor contains a checkout
                    or inside(p, checkout_paths) or holds_checkout(p)):
                continue
            big.append(d)
    big.sort(key=lambda d: d["depth"])
    for d in big:
        p = norm(d["path"], windows)
        if inside(p, listed):
            continue
        listed.add(p)
        # Not "outside any checkout": discovery stops at a depth, so a repository may sit
        # below it. The finding is a large idle folder to inspect, nothing more.
        items.append(item("review", d["path"], f"large idle folder, newest file "
                          f"{d['newest_utc'][:10]}; checkout discovery limited to depth "
                          f"{gs.get('depth')}", "inspect: may hold repositories below that "
                          "depth; then data store (manifest-and-fetch) or owner decision",
                          d["bytes"]))
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


def git_common(common: str, *args: str) -> tuple[int, str]:
    """Address the shared repository by its verified git dir (works for bare repos too).

    Replacement objects are disabled: a local refs/replace entry must not be able to
    rewrite ancestry and make a local-only commit look contained in a remote tip.
    """
    return run_cmd(["git", "--no-replace-objects", "-c", "safe.directory=*",
                    f"--git-dir={common}", *args])


def remote_contains(common: str, head: str) -> tuple[bool, str]:
    """Fetch origin's branch tips into a fresh private namespace and test containment
    against exactly those tips, so stale remote-tracking refs cannot vouch for HEAD."""
    if os.path.exists(os.path.join(common, "info", "grafts")):
        return False, "repository uses legacy grafts; ancestry cannot be trusted"
    ns = f"refs/hygiene-verify/{uuid.uuid4().hex}"
    try:
        rc, out = git_common(common, "fetch", "--quiet", "--no-tags", "origin",
                             f"+refs/heads/*:{ns}/*")
        if rc:
            return False, f"fetch failed: {out}"
        rc, refs = git_common(common, "for-each-ref", "--count=1", "--contains", head,
                              "--format=%(refname)", ns)
        return (rc == 0 and bool(refs.strip())), "HEAD not in any branch tip fetched now"
    finally:
        rc, refs = git_common(common, "for-each-ref", "--format=%(refname)", ns)
        for ref in refs.split():
            git_common(common, "update-ref", "-d", ref)


if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    class _FileBasicInfo(ctypes.Structure):
        _fields_ = [("CreationTime", ctypes.c_longlong), ("LastAccessTime", ctypes.c_longlong),
                    ("LastWriteTime", ctypes.c_longlong), ("ChangeTime", ctypes.c_longlong),
                    ("FileAttributes", wintypes.DWORD)]

    _K32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _K32.CreateFileW.restype = wintypes.HANDLE
    _K32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE]
    _K32.GetFileInformationByHandleEx.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                  ctypes.c_void_p, wintypes.DWORD]
    _K32.CloseHandle.argtypes = [wintypes.HANDLE]
    _INVALID = wintypes.HANDLE(-1).value

    def _change_time(path: str) -> float:
        """NTFS ChangeTime (any data or metadata change), as Unix seconds.

        os.stat on Windows exposes only creation time as st_ctime; an in-place overwrite
        that restores the old mtime (robocopy does this) moves only ChangeTime.
        """
        # The \\?\ prefix lifts the 260-character MAX_PATH limit (error 3 otherwise);
        # it needs an absolute path with backslashes. UNC paths use \\?\UNC\.
        full = os.path.abspath(path).replace("/", "\\")
        if not full.startswith("\\\\?\\"):
            full = ("\\\\?\\UNC\\" + full[2:]) if full.startswith("\\\\") else ("\\\\?\\" + full)
        h = _K32.CreateFileW(full, 0x80,            # FILE_READ_ATTRIBUTES
                             0x7, None, 3,          # share all, OPEN_EXISTING
                             0x02000000 | 0x00200000,  # BACKUP_SEMANTICS | OPEN_REPARSE_POINT
                             None)
        if h in (None, _INVALID):
            raise OSError(ctypes.get_last_error(), "cannot open for change time", path)
        try:
            info = _FileBasicInfo()
            if not _K32.GetFileInformationByHandleEx(h, 0, ctypes.byref(info),
                                                     ctypes.sizeof(info)):
                raise OSError(ctypes.get_last_error(), "cannot read change time", path)
            return info.ChangeTime / 1e7 - 11644473600.0   # FILETIME epoch 1601 -> 1970
        finally:
            _K32.CloseHandle(h)
else:
    def _change_time(path: str) -> float:
        return os.lstat(path).st_ctime   # POSIX st_ctime is the inode change time


def last_activity(path: str, git_dir: str) -> float:
    """Newest mtime of the worktree's index, HEAD and every entry in the tree.

    The whole tree is walked (links not followed) because a job can rewrite a file deep
    inside an ignored folder without touching anything near the top. Raises OSError if
    anything cannot be inspected, so the caller refuses rather than guesses.

    Limitation: a job that only reads files changes no mtime. Such jobs are expected to
    `git worktree lock` their worktree (workstation-hygiene rule, item 1).
    """
    def stamp(p: str, st) -> float:
        # mtime, creation time (Windows st_ctime) and the true change time: a write that
        # preserves or restores mtime (`cp -p`, robocopy) still moves the change time.
        return max(st.st_mtime, st.st_ctime, _change_time(p))

    newest = 0.0
    for p in (os.path.join(git_dir, "index"), os.path.join(git_dir, "HEAD")):
        if os.path.exists(p):
            newest = max(newest, stamp(p, os.stat(p)))
    stack = [path]
    while stack:
        cur = stack.pop()
        newest = max(newest, stamp(cur, os.lstat(cur)))
        with os.scandir(cur) as it:
            for e in it:
                newest = max(newest, stamp(e.path, e.stat(follow_symlinks=False)))
                # No name is exempt: a nested folder called .git inside a cache is
                # still activity (the worktree's own .git is a file, not walked).
                if e.is_dir(follow_symlinks=False) and not HB.is_link_entry(e):
                    stack.append(e.path)
    return newest


def check_idle(path: str, gd: str, min_idle_hours: float) -> str | None:
    try:
        idle_h = (datetime.now(timezone.utc).timestamp() - last_activity(path, gd)) / 3600
    except OSError as exc:
        return f"activity check failed: {exc.strerror or exc}"
    if idle_h < min_idle_hours:
        return f"recently active ({idle_h:.1f} h ago; minimum {min_idle_hours:g} h)"
    return None


def verify_and_remove_worktree(i: dict, preserved: set, min_idle_hours: float = 48.0) -> tuple[str, str]:
    """Network step first; every local check runs after it, immediately before removal.

    Stashes are not checked: they live in the shared repository and survive the removal
    of a worktree.
    """
    path, planned = i["path"], i.get("head")
    if not planned or HB.is_link_path(path):
        return "refused", "no planned HEAD, or path is a link"
    rc, gd = git(path, "rev-parse", "--path-format=absolute", "--git-dir")
    rc2, common = git(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    gd, common = gd.strip(), common.strip()
    if rc or rc2 or os.path.normcase(gd) == os.path.normcase(common):
        return "refused", "not a linked worktree"
    busy = check_idle(path, gd, min_idle_hours)   # cheap early refusal, before the fetch
    if busy:
        return "refused", busy
    if planned not in preserved:
        ok, why = remote_contains(common, planned)
        if not ok:
            return "refused", why
    rc, head = git(path, "rev-parse", "--verify", "-q", "HEAD")
    if rc or head.strip() != planned:
        return "refused", "HEAD changed since the plan or unreadable"
    if HB.worktree_lock_state(path):
        return "refused", "worktree is locked"
    rc, status = git(path, "status", "--porcelain=v1", "--untracked-files=normal")
    if rc or status.strip():
        return "refused", "worktree has changes"
    if HB.ignored_unregenerable(path):
        return "refused", "ignored non-regenerable files present"
    hidden = HB.hidden_or_in_progress(path)
    if hidden:
        return "refused", "; ".join(hidden)
    busy = check_idle(path, gd, min_idle_hours)   # again, immediately before removal
    if busy:
        return "refused", busy
    rc, out = git_common(common, "worktree", "remove", path)
    return ("removed", out) if rc == 0 else ("refused", out)


def cache_command(name: str, path: str):
    """Command bound to exactly the planned cache path. uv only: pip and npm purge by
    walking subfolders that can be links into someone else's data, so they stay review."""
    import shutil
    env = dict(os.environ)
    if name == "uv" and shutil.which("uv"):
        # prune (unreferenced entries only), not clean: safe while other sessions on a
        # shared host are installing from the same cache.
        return [shutil.which("uv"), "cache", "prune", "--cache-dir", path], env
    return None, env


def linked_entries(path: str, depth: int = 2) -> list[str]:
    """Links or junctions within the top `depth` levels of a cache folder."""
    found, frontier = [], [(path, 0)]
    while frontier:
        cur, level = frontier.pop()
        with os.scandir(cur) as it:
            for e in it:
                if HB.is_link_entry(e):
                    found.append(e.name)
                elif level + 1 < depth and e.is_dir(follow_symlinks=False):
                    frontier.append((e.path, level + 1))
    return found


def apply_item(i: dict, preserved: set, min_idle_hours: float = 48.0) -> tuple[str, str]:
    if i["tier"] == "safe-checkout":
        return verify_and_remove_worktree(i, preserved, min_idle_hours)
    if HB.is_link_path(i["path"]):
        return "refused", "cache path is a link"
    links = linked_entries(i["path"])
    if links:
        return "refused", f"cache holds link/junction entries: {', '.join(links[:3])}"
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
    ap.add_argument("--min-idle-hours", type=float, default=48.0,
                    help="refuse worktrees with activity more recent than this (default 48)")
    args = ap.parse_args(argv)
    if not (math.isfinite(args.min_idle_hours) and args.min_idle_hours >= 0):
        print("refused: --min-idle-hours must be finite and >= 0", file=sys.stderr)
        return 2

    doc = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    preserved = set()
    if args.preserved:
        preserved = {line.strip() for line in
                     Path(args.preserved).read_text(encoding="utf-8").splitlines() if line.strip()}
    items = plan(doc, args.own_roots, preserved)
    if args.out:
        try:  # never overwrite: a typo must not replace the baseline it was read from
            with open(args.out, "x", encoding="utf-8") as fh:
                fh.write(json.dumps(items, indent=1))
        except FileExistsError:
            print("refused: --out already exists", file=sys.stderr)
            return 2
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
    # The home allowance comes from the executing account, and only when it is the
    # account that collected the baseline; worktrees are confined to --own-roots.
    my_home = os.path.normcase(os.path.realpath(str(Path.home())))
    same_account = bool(doc.get("home")) and \
        os.path.normcase(os.path.realpath(doc["home"])) == my_home
    with open(args.log, "a", encoding="utf-8") as log:
        for i in items:
            if i["tier"] not in tiers:
                continue
            roots = list(args.own_roots)
            if i["tier"] == "regenerable" and same_account:
                roots.append(str(Path.home()))
            try:
                if not real_inside(i["path"], roots):
                    result, detail = "refused", "real path outside own roots"
                else:
                    result, detail = apply_item(i, preserved, args.min_idle_hours)
            except Exception as exc:  # one failed probe must not stop independent items
                result, detail = "error", f"{type(exc).__name__}: {exc}"
            rec = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "host": doc["label"], **i, "result": result, "detail": detail}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"{result:8} {i['tier']:14} {i['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
