#!/usr/bin/env python3
"""Read-only storage baseline for one host (#4532).

Single file, standard library only, Python 3.9+, so it can be piped to any fleet
host:  ssh <alias> python3 - --label <label> < scripts/hygiene/host_baseline.py

It reports disks, folder sizes to a fixed depth, stray drive-root/home folders,
package caches and git checkouts. It never writes, moves or deletes anything; git
queries run with GIT_OPTIONAL_LOCKS=0 so they do not refresh the index.

The host label comes only from --label. The script does not read the hostname,
so a public repository can carry the code while the output goes somewhere private.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1
IS_WINDOWS = os.name == "nt"
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)

# Folders Windows or common vendors place at a drive root. Matched case-insensitively.
WINDOWS_SYSTEM_ROOTS = {
    "windows", "program files", "program files (x86)", "programdata", "users",
    "perflogs", "recovery", "$recycle.bin", "system volume information",
    "$winreagent", "documents and settings", "inetpub", "config.msi", "msocache",
    "intel", "amd", "nvidia", "onedrivetemp", "$sysreset", "$windows.~bt",
    "$windows.~ws", "esd", "drivers", "swsetup", "windows.old", "$getcurrent", "boot",
}
# A POSIX absolute path handed to a native Windows program resolves against the
# current drive root, so `/tmp/x` becomes `C:\tmp\x`. These names at a drive root
# are that signature.
POSIX_LEAK_NAMES = {
    "tmp", "mnt", "etc", "usr", "var", "opt", "home", "dev", "proc", "root",
    "srv", "bin", "lib", "media", "run",
}
# Names test suites use for "a path that does not exist", created by mistake.
TEST_FIXTURE_NAMES = {"invalid", "nonexistent", "does-not-exist", "doesnotexist"}


def utc_iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_link_entry(entry: os.DirEntry) -> bool:
    """Symlinks, junctions and other reparse points are never followed."""
    try:
        if entry.is_symlink():
            return True
        if IS_WINDOWS:
            st = entry.stat(follow_symlinks=False)
            return bool(getattr(st, "st_file_attributes", 0) & REPARSE)
    except OSError:
        return True
    return False


def walk_totals(path: str, root_dev: int | None) -> dict:
    """Total bytes/files/newest mtime of a subtree, not following links.

    On POSIX the walk does not cross into another filesystem (like `du -x`).
    """
    total = files = denied = 0
    newest = None
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            denied += 1
            continue
        for entry in entries:
            try:
                if is_link_entry(entry):
                    continue
                st = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode):
                    if root_dev is not None and st.st_dev != root_dev:
                        continue
                    stack.append(entry.path)
                elif stat.S_ISREG(st.st_mode):
                    total += st.st_size
                    files += 1
                    if newest is None or st.st_mtime > newest:
                        newest = st.st_mtime
            except OSError:
                denied += 1
    return {"bytes": total, "files": files, "newest": newest, "denied": denied}


def git_kind(path: str) -> str:
    marker = os.path.join(path, ".git")
    if os.path.isdir(marker):
        return "clone"
    if os.path.isfile(marker):
        return "worktree"
    return ""


def root_device(path: str) -> int | None:
    if IS_WINDOWS:
        return None
    try:
        return os.stat(path).st_dev
    except OSError:
        return None


def scan_root(root: str, depth: int = 2, workers: int = 8) -> dict:
    """Sizes of every directory 1..depth levels below root.

    Each row carries `direct_bytes` (files directly in it) so a reader can check
    conservation: bytes == direct_bytes + sum(child bytes) for non-leaf rows.
    """
    depth = max(1, depth)
    dev = root_device(root)
    nodes: dict[str, dict] = {}
    children: dict[str, list[str]] = {}
    frontier = [(root, 0)]
    leaves = []
    denied = 0
    while frontier:
        current, level = frontier.pop()
        kids = []
        direct = direct_files = 0
        newest = None
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            denied += 1
            entries = []
        for entry in entries:
            try:
                if is_link_entry(entry):
                    continue
                st = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(st.st_mode):
                    if dev is not None and st.st_dev != dev:
                        continue
                    kids.append(entry.path)
                elif stat.S_ISREG(st.st_mode):
                    direct += st.st_size
                    direct_files += 1
                    if newest is None or st.st_mtime > newest:
                        newest = st.st_mtime
            except OSError:
                denied += 1
        if level >= 1:
            nodes[current] = {
                "path": Path(current).as_posix(), "depth": level,
                "direct_bytes": direct, "direct_files": direct_files,
                "newest": newest, "denied": 0, "git": git_kind(current),
            }
        children[current] = kids
        for kid in kids:
            if level + 1 < depth:
                frontier.append((kid, level + 1))
            else:
                leaves.append(kid)

    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = dict(zip(leaves, pool.map(lambda p: walk_totals(p, dev), leaves)))
    for leaf, res in results.items():
        nodes[leaf] = {
            "path": Path(leaf).as_posix(), "depth": depth,
            "direct_bytes": None, "direct_files": None,
            "bytes": res["bytes"], "files": res["files"],
            "newest": res["newest"], "denied": res["denied"], "git": git_kind(leaf),
        }

    def total(path: str) -> tuple:
        node = nodes[path]
        if "bytes" in node:
            return node["bytes"], node["files"], node["newest"], node["denied"]
        b, f, n, d = node["direct_bytes"], node["direct_files"], node["newest"], node["denied"]
        for kid in children.get(path, []):
            kb, kf, kn, kd = total(kid)
            b, f, d = b + kb, f + kf, d + kd
            if kn is not None and (n is None or kn > n):
                n = kn
        node.update(bytes=b, files=f, newest=n, denied=d)
        return b, f, n, d

    for top in children.get(root, []):
        total(top)
    rows = []
    for node in nodes.values():
        row = dict(node)
        row["newest_utc"] = utc_iso(row.pop("newest"))
        rows.append(row)
    rows.sort(key=lambda r: (-r["bytes"], r["path"]))
    return {"root": Path(root).as_posix(), "denied": denied, "dirs": rows}


def classify_stray(name: str, windows_drive_root: bool, expected=None):
    """Return (reason, note) for a suspicious top-level folder name, else None."""
    low = name.lower()
    if expected and low in {e.lower() for e in expected}:
        return None
    if windows_drive_root and low in WINDOWS_SYSTEM_ROOTS:
        return None
    if low in TEST_FIXTURE_NAMES:
        return ("test-fixture-leak", "a test's 'path that does not exist' was created")
    if not windows_drive_root:
        return None
    if low in POSIX_LEAK_NAMES:
        return ("posix-path-leak", f"/{low}/... resolved against a Windows drive root")
    if len(low) == 1 and low.isalpha():
        return ("drive-letter-mirror", f"/{low}/... (Git Bash style) resolved as a folder")
    return ("unclassified", "not a system folder and not in the expected list")


def list_disks() -> list[dict]:
    disks = []
    if IS_WINDOWS:
        import ctypes  # noqa: PLC0415 - Windows only
        get_type = ctypes.windll.kernel32.GetDriveTypeW
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            mount = f"{letter}:\\"
            if not os.path.exists(mount) or get_type(mount) != 3:  # 3 = fixed disk
                continue
            usage = shutil.disk_usage(mount)
            disks.append({"mount": mount, "total_bytes": usage.total,
                          "used_bytes": usage.used, "free_bytes": usage.free})
    else:
        try:
            out = subprocess.run(["df", "-kP"], capture_output=True, text=True,
                                 timeout=30).stdout
        except (OSError, subprocess.TimeoutExpired):
            out = ""
        seen = set()
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 6 or not parts[0].startswith("/dev/"):
                continue
            device, mount = parts[0], " ".join(parts[5:])
            if device.startswith("/dev/loop") or device in seen:
                continue
            if mount.startswith(("/boot", "/snap", "/System/Volumes/")) and \
                    mount != "/System/Volumes/Data":
                continue
            seen.add(device)
            try:
                usage = shutil.disk_usage(mount)
            except OSError:
                continue
            disks.append({"mount": mount, "total_bytes": usage.total,
                          "used_bytes": usage.used, "free_bytes": usage.free})
        # APFS: "/" (sealed system snapshot) and its Data volume share one container,
        # so disk_usage reports the same space twice. Keep the Data volume only.
        if any(d["mount"] == "/System/Volumes/Data" for d in disks):
            disks = [d for d in disks if d["mount"] != "/"]
    for d in disks:
        d["free_pct"] = round(100.0 * d["free_bytes"] / d["total_bytes"], 1) if d["total_bytes"] else None
    return disks


def default_roots(disks: list[dict]) -> list[str]:
    if IS_WINDOWS:
        return [d["mount"] for d in disks]
    roots = [str(Path.home())]
    home = Path.home().resolve()
    for d in disks:
        mount = d["mount"]
        if mount in ("/", "/System/Volumes/Data") or d["total_bytes"] < 20 * 1024 ** 3:
            continue
        try:
            if home.is_relative_to(Path(mount)):  # home's own mount is already covered
                continue
        except AttributeError:  # Python < 3.9 has no is_relative_to
            pass
        roots.append(mount)
    return roots


def cache_candidates() -> list[tuple[str, str]]:
    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    tmp = Path(tempfile.gettempdir())
    c = []
    if os.environ.get("UV_CACHE_DIR"):
        c.append(("uv", os.environ["UV_CACHE_DIR"]))
    if IS_WINDOWS:
        c += [("uv", local / "uv" / "cache"), ("pip", local / "pip" / "Cache"),
              ("npm", local / "npm-cache"), ("playwright", local / "ms-playwright"),
              ("yarn", local / "Yarn" / "Cache"), ("pnpm", local / "pnpm" / "store")]
    else:
        lib = home / "Library" / "Caches"
        c += [("uv", home / ".cache" / "uv"), ("pip", home / ".cache" / "pip"),
              ("pip", lib / "pip"), ("npm", home / ".npm" / "_cacache"),
              ("playwright", home / ".cache" / "ms-playwright"),
              ("playwright", lib / "ms-playwright"), ("yarn", lib / "Yarn"),
              ("pnpm", home / ".local" / "share" / "pnpm" / "store")]
    c += [("huggingface", home / ".cache" / "huggingface"),
          ("torch", home / ".cache" / "torch"),
          ("conda-pkgs", home / "miniconda3" / "pkgs"),
          ("conda-pkgs", home / "anaconda3" / "pkgs"),
          ("cargo-registry", home / ".cargo" / "registry"),
          ("go-mod", home / "go" / "pkg" / "mod"),
          ("gradle", home / ".gradle" / "caches"),
          ("maven", home / ".m2" / "repository")]
    c += [("pytest-tmp", p) for p in sorted(tmp.glob("pytest-of-*"))]
    c.append(("temp-dir", tmp))
    seen, out = set(), []
    for name, path in c:
        key = os.path.normcase(str(path))
        if key not in seen and os.path.isdir(path):
            seen.add(key)
            out.append((name, str(path)))
    return out


def measure_caches(workers: int) -> list[dict]:
    cands = cache_candidates()
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        res = list(pool.map(lambda nc: walk_totals(nc[1], None), cands))
    rows = [{"name": n, "path": Path(p).as_posix(), "bytes": r["bytes"],
             "files": r["files"], "newest_utc": utc_iso(r["newest"])}
            for (n, p), r in zip(cands, res)]
    rows.sort(key=lambda r: -r["bytes"])
    return rows


GIT_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GIT_ENV["GIT_OPTIONAL_LOCKS"] = "0"
GIT_ENV["GIT_TERMINAL_PROMPT"] = "0"


def git_out(path: str, *args: str, timeout: int = 120) -> str:
    proc = subprocess.run(
        ["git", "-c", "safe.directory=*", "-c", "core.fsmonitor=false",
         "-C", path, *args],
        capture_output=True, text=True, env=GIT_ENV, timeout=timeout,
        encoding="utf-8", errors="replace",
    )
    if proc.returncode:
        raise RuntimeError(f"git {args[0]} rc={proc.returncode}")
    return proc.stdout


def strip_userinfo(url: str) -> str:
    return re.sub(r"^(\w+://)[^/@]+@", r"\1", url.strip())


def describe_checkout(path: str) -> dict:
    row = {"path": Path(path).as_posix(), "kind": git_kind(path)}
    try:
        row["branch"] = git_out(path, "rev-parse", "--abbrev-ref", "HEAD").strip()
        status = git_out(path, "status", "--porcelain=v1", "--untracked-files=normal")
        row["dirty"] = sum(1 for line in status.splitlines() if line.strip())
        remotes = git_out(path, "for-each-ref", "--count=1", "--contains", "HEAD",
                          "--format=%(refname)", "refs/remotes")
        row["head_on_remote"] = bool(remotes.strip())
        row["last_commit_utc"] = git_out(path, "log", "-1", "--format=%cI").strip() or None
        try:
            row["origin"] = strip_userinfo(git_out(path, "remote", "get-url", "origin"))
        except RuntimeError:
            row["origin"] = None
        row["stashes"] = len(git_out(path, "stash", "list").splitlines()) if row["kind"] == "clone" else 0
        lock = Path(path) / ".git"
        row["locked"] = False
        if row["kind"] == "worktree":
            gitdir = lock.read_text(encoding="utf-8", errors="replace").split("gitdir:", 1)[-1].strip()
            row["locked"] = (Path(gitdir) / "locked").exists()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        row["error"] = str(exc)
    return row


def find_checkouts(roots: list[str], max_depth: int = 3, workers: int = 8) -> list[dict]:
    found = []
    for root in roots:
        stack = [(root, 0)]
        while stack:
            current, level = stack.pop()
            if level > 0 and git_kind(current):
                found.append(current)
                continue
            if level >= max_depth:
                continue
            try:
                with os.scandir(current) as it:
                    for entry in it:
                        if entry.name.startswith(("$", ".")) or is_link_entry(entry):
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append((entry.path, level + 1))
            except OSError:
                continue
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = list(pool.map(describe_checkout, sorted(set(found))))
    return rows


def stray_rows(roots: list[str], scans: list[dict], expected) -> list[dict]:
    sizes = {}
    for scan in scans:
        for row in scan["dirs"]:
            if row["depth"] == 1:
                sizes[row["path"]] = row
    home = os.path.normcase(str(Path.home()))
    out = []
    for root in roots:
        drive_root = IS_WINDOWS and len(Path(root).parts) == 1
        if not drive_root and os.path.normcase(root) != home:
            continue
        try:
            entries = [e for e in os.scandir(root) if e.is_dir(follow_symlinks=False)]
        except OSError:
            continue
        for entry in entries:
            hit = classify_stray(entry.name, windows_drive_root=drive_root, expected=expected)
            if not hit:
                continue
            size = sizes.get(Path(entry.path).as_posix(), {})
            out.append({"path": Path(entry.path).as_posix(), "reason": hit[0],
                        "note": hit[1], "bytes": size.get("bytes"),
                        "files": size.get("files"), "newest_utc": size.get("newest_utc")})
    out.sort(key=lambda r: (r["reason"], r["path"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--label", required=True, help="fleet label for this host")
    ap.add_argument("--roots", nargs="*", help="roots to size (default: fixed drives on "
                    "Windows; home plus large data mounts elsewhere)")
    ap.add_argument("--checkout-roots", nargs="*", help="roots searched for git checkouts "
                    "(default: same as --roots)")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--checkout-depth", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--min-bytes", type=int, default=256 * 1024 ** 2,
                    help="omit rows deeper than 1 below this size (default 256 MiB)")
    ap.add_argument("--expected", default="", help="comma list of top-level names "
                    "that are expected at drive roots / home")
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--no-caches", action="store_true")
    args = ap.parse_args(argv)

    started = datetime.now(timezone.utc)
    disks = list_disks()
    roots = args.roots or default_roots(disks)
    expected = {e.strip() for e in args.expected.split(",") if e.strip()}
    scans = [scan_root(r, args.depth, args.workers) for r in roots if os.path.isdir(r)]
    strays = stray_rows(roots, scans, expected)
    for scan in scans:
        scan["dirs"] = [d for d in scan["dirs"] if d["depth"] == 1 or d["bytes"] >= args.min_bytes]
    doc = {
        "schema": SCHEMA,
        "label": args.label,
        "generated_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "os": platform.system(),
        "python": platform.python_version(),
        "disks": disks,
        "roots": scans,
        "stray": strays,
        "caches": [] if args.no_caches else measure_caches(args.workers),
        "checkouts": [] if args.no_git else find_checkouts(
            args.checkout_roots or roots, args.checkout_depth, args.workers),
        "elapsed_s": None,
    }
    doc["elapsed_s"] = round((datetime.now(timezone.utc) - started).total_seconds(), 1)
    json.dump(doc, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
