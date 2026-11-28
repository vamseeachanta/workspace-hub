"""Read-only discovery of work roots on local Windows and Linux volumes."""
import argparse
import ctypes
import json
import socket
import subprocess
import os
import re
import stat
from pathlib import Path

REMOTE_TYPES = {"9p", "afs", "ceph", "cifs", "davfs", "glusterfs", "nfs",
                "nfs4", "smb3", "smbfs", "sshfs", "virtiofs"}
LOCAL_TYPES = {"apfs", "btrfs", "exfat", "ext2", "ext3", "ext4", "f2fs",
               "fat", "fat32", "hfs", "hfsplus", "jfs", "ntfs", "ntfs3",
               "overlay", "refs", "ufs", "vfat", "xfs", "zfs"}
RESERVED = ("_wt", "_pm", "_backups", "_archive")


def merge_private(config, private):
    """Add the private layout (client and personal repositories, private host names).

    The public configuration lives in a public repository, so it must not name client or
    personal repositories. Those entries come from a private file at run time.
    """
    if not isinstance(config, dict) or not isinstance(private, dict):
        raise ValueError("layout must be an object")
    for layout in (config, private):
        for section in ("origins", "repositories", "hosts"):
            if not isinstance(layout.get(section, {}), dict):
                raise ValueError(f"{section} must be an object")
        for entry in layout.get("hosts", {}).values():
            if not isinstance(entry, dict):
                raise ValueError("host entry must be an object")
            for field in ("hostnames", "aliases", "extra_roots", "excluded_parents"):
                values = entry.get(field, [])
                if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                    raise ValueError(f"{field} must be a list of strings")
            if "w" in entry and not isinstance(entry["w"], str):
                raise ValueError("w must be a string")
    for section in ("origins", "repositories"):
        config.setdefault(section, {}).update(private.get(section, {}))
    for host, extra in private.get("hosts", {}).items():
        entry = config.setdefault("hosts", {}).setdefault(host, {})
        names = list(dict.fromkeys([*entry.get("hostnames", []), *extra.get("hostnames", [])]))
        entry.update(extra)
        entry["hostnames"] = names
    return config


def is_local(kind):
    """Worktree placement types. A local fuseblk disk is scanned but disallowed."""
    return kind.lower() in LOCAL_TYPES


def filesystem_type(path, mounts):
    for mount in sorted(mounts, key=lambda p: len(p.parts), reverse=True):
        if Path(path).is_relative_to(mount):
            return mounts[mount]
    raise OSError(f"no filesystem evidence for {path}")


def _windows_volumes():
    # Volume GUID enumeration includes volumes mounted solely in an NTFS directory.
    from ctypes import wintypes

    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.FindFirstVolumeW.restype = wintypes.HANDLE
    api.FindNextVolumeW.argtypes = (wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD)
    api.FindVolumeClose.argtypes = (wintypes.HANDLE,)
    guid = ctypes.create_unicode_buffer(1024)
    handle = api.FindFirstVolumeW(guid, len(guid))
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    mounts = {}
    unavailable = []
    try:
        while True:
            if api.GetDriveTypeW(guid.value) in (2, 3, 6):
                size = wintypes.DWORD(256)
                while True:
                    paths = ctypes.create_unicode_buffer(size.value)
                    if api.GetVolumePathNamesForVolumeNameW(
                        guid.value, paths, len(paths), ctypes.byref(size)
                    ):
                        break
                    if ctypes.get_last_error() != 234:  # ERROR_MORE_DATA
                        unavailable.append(guid.value)
                        break
                for name in paths[:size.value].rstrip("\0").split("\0"):
                    if not name:
                        continue
                    kind = ctypes.create_unicode_buffer(256)
                    if not api.GetVolumeInformationW(name, None, 0, None, None, None,
                                                     kind, len(kind)):
                        unavailable.append(name)
                        mounts[Path(name)] = "unknown"
                        continue
                    mounts[Path(name)] = kind.value.lower()
            if not api.FindNextVolumeW(handle, guid, len(guid)):
                if ctypes.get_last_error() != 18:  # ERROR_NO_MORE_FILES
                    raise ctypes.WinError(ctypes.get_last_error())
                break
    finally:
        api.FindVolumeClose(handle)
    return [p for p in mounts if mounts[p] != "unknown"], mounts, unavailable


def volume_inventory():
    if os.name == "nt":
        return _windows_volumes()
    roots, mounts = [], {}
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        before, after = line.split(" - ", 1)
        name = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m[1], 8)), before.split()[4])
        mount = Path(name)
        kind, source = after.split()[:2]
        mounts[mount] = kind
        if (source.startswith("/dev/") or is_local(kind) or kind == "fuseblk"
                or (mount == Path("/") and kind not in REMOTE_TYPES)):
            # Bind mounts of individual files are not directory roots.
            if stat.S_ISDIR(mount.lstat().st_mode):
                roots.append(mount)
    if not roots:
        raise OSError("no local filesystem roots enumerated")
    return roots, mounts, []


def _excluded(path, home, workspace, excluded_parents=()):
    # Apply exclusions to independently enumerated mount roots as well as children.
    for part in (path, *path.parents):
        name = part.name.casefold()
        if (name == ".git" or name.endswith(".git") or
                re.search(r"(?:^|[-_.])(archives?|backups?|mirrors?)(?:$|[-_.])", name)):
            return True
        if part.parent.name.casefold() in {"users", "home"} and not home.is_relative_to(part):
            return True
        if part.parent in excluded_parents and not workspace.is_relative_to(part):
            return True
        if part == Path("/root") and not home.is_relative_to(part):
            return True
    return False


def _is_link(info):
    return (stat.S_ISLNK(info.st_mode) or
            bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT))


def scan_roots(roots, home, workspace, aliases, extra_roots, mounts, excluded_parents=()):
    """Inspect each seed and three child levels. Never recurse through links."""
    allowed = {workspace, *(workspace / name for name in RESERVED), *extra_roots}
    aliases = set(aliases)
    excluded_parents = set(excluded_parents)
    seeds = set(roots) | {home}
    seen = {}
    findings = {}

    def report(reason, path, expected):
        findings[(path, reason)] = dict(reason=reason, observed=str(path),
                                        expected=str(expected), repository=None)

    def visit(path, remaining, seed=False):
        if _excluded(path, home, workspace, excluded_parents) or seen.get(path, -1) >= remaining:
            return
        seen[path] = remaining
        if path in mounts and path not in roots:
            return
        try:
            info = path.lstat()
            link = _is_link(info)
            if path in aliases:
                if not link or path.resolve(strict=True) != workspace:
                    report("alias target mismatch", path, workspace)
                return
            name = path.name.casefold()
            # workspace_children reports direct _scratch entries even outside scan depth.
            if name == "_scratch" and path.parent != workspace:
                report("unexpected scratch entry", path, "OS temp or repository .tmp")
            candidate = (name in {"ws", "_wt", "_worktrees", "_pm"}
                         or name.startswith(("ws-", "wt-")))
            if candidate and (link or stat.S_ISDIR(info.st_mode)) and path not in allowed:
                report("extra root", path, workspace)
            if link and (path in allowed or seed):
                # A Windows volume mount is itself a reparse point. Its GUID and
                # mount path were obtained from the local volume registry above.
                if not (os.name == "nt" and path in mounts and path in roots):
                    report("unexpected linked root", path, "physical local directory")
                    return
            elif link:
                return
            if not stat.S_ISDIR(info.st_mode):
                if seed:
                    report("scan root is not a directory", path, "accessible directory")
                return
            if remaining:
                for child in path.iterdir():
                    visit(child, remaining - 1)
        except (OSError, RuntimeError) as exc:
            report(f"missing evidence ({type(exc).__name__})", path, "accessible directory")

    for seed in sorted(seeds):
        if mounts and seed not in roots:
            try:
                kind = filesystem_type(seed, mounts)
                if kind in REMOTE_TYPES or kind.startswith("fuse."):
                    report("foreign scan root", seed, "local filesystem")
                    continue
            except OSError:
                report("unknown scan filesystem", seed, "local filesystem evidence")
                continue
        visit(seed, 3, True)
    for alias in aliases - seen.keys():
        if os.path.lexists(alias):
            visit(alias, 0)
    return [findings[k] for k in sorted(findings)]


def finding(reason, observed, expected, repository=None):
    return dict(reason=reason, observed=str(observed), expected=str(expected),
                repository=repository)


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(repo), *args],
        env=env, capture_output=True, timeout=45,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode:
        raise OSError(f"git {args[0]} failed (exit {result.returncode})")
    return os.fsdecode(result.stdout)


def origin_name(url):
    return re.split(r"[/\\:]", url)[-1].removesuffix(".git")


def repository(repo, policy, strict):
    top = git(repo, "rev-parse", "--show-toplevel").rstrip("\r\n")
    if Path(top).resolve() != repo.resolve():
        return [finding("not repository root", repo, top, repo.name)]
    listing = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    names = {s.partition("/")[0] for s in listing.split("\0") if s}
    allowed = set(policy["core" if strict else "allowed"])
    findings = []
    for name in sorted(names):
        path = repo / name
        if name not in allowed:
            findings.append(finding("unexpected repository root name", path,
                                    "configured root names", repo.name))
        elif name in policy.get("types", {}):
            expected = policy["types"][name]
            info = path.lstat()
            actual = ("symlink" if _is_link(info) else "dir" if stat.S_ISDIR(info.st_mode)
                      else "file" if stat.S_ISREG(info.st_mode) else "other")
            if actual != expected:
                findings.append(finding("repository root type mismatch", path,
                                        f"{path} ({expected})", repo.name))
    return findings


def ledger_path(workspace, value):
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ValueError("invalid ledger path")
    return (workspace / value).resolve()


def ledger_findings(workspace, ledger, required, worktrees):
    try:
        files = sorted(ledger.iterdir())
    except (FileNotFoundError, NotADirectoryError):
        return [finding("missing ledger", ledger, "work ledger directory")] if required else []

    findings = []
    named = set()
    for file in files:
        # The work tool also writes close receipts (<id>.close.json) and sweep reports here.
        if (file.suffix != ".json" or file.name.endswith(".close.json")
                or re.fullmatch(r"sweep-\d{8}T\d{12}Z\.json", file.name)):
            continue
        try:
            record = json.loads(file.read_text(encoding="utf-8-sig"))
            if isinstance(record, dict) and record.get("schema") == "work-sweep/1" and "id" not in record:
                continue
            state = record["state"]
            if state not in ("open", "adopted", "closed", "review"):
                raise ValueError("invalid ledger state")
            if not isinstance(record["id"], str) or not record["id"].strip():
                raise ValueError("invalid ledger id")
            tree = ledger_path(workspace, record["path"])
            paths = {tree}
            if record["scratch"] is not None:
                paths.add(ledger_path(workspace, record["scratch"]))
            if not isinstance(record["outputs"], list):
                raise ValueError("invalid ledger outputs")
            paths.update(ledger_path(workspace, output["path"]) for output in record["outputs"])
            if state in ("open", "adopted") and not tree.exists():
                findings.append(finding("record without tree", tree, "existing worktree"))
            named.update(paths)
        except (KeyError, TypeError, ValueError, OSError, RuntimeError):
            findings.append(finding("unreadable ledger record", file, "valid work ledger record"))

    candidates = set(worktrees)
    scratch = workspace / "_scratch"
    if scratch.is_dir():
        candidates.update(path for path in scratch.iterdir() if path.is_dir())
    findings.extend(finding("unrecorded work", path, "path named in work ledger")
                    for path in sorted(candidates) if path.resolve() not in named)
    return findings


def workspace_children(workspace, fs_type, origins=None, registered_roots=None, ledger_trees=None):
    findings = []
    if _is_link(workspace.lstat()):
        return [finding("linked workspace", workspace, "physical workspace")]
    for reserved in RESERVED:
        path = workspace / reserved
        if not path.is_dir():
            findings.append(finding("missing workspace directory", path, path))
    for child in sorted(workspace.iterdir()):
        try:
            info = child.lstat()
            if child.name.casefold() == "_scratch":
                findings.append(finding("unexpected scratch entry", child,
                                        "OS temp or repository .tmp"))
                continue
            if _is_link(info) or not stat.S_ISDIR(info.st_mode):
                findings.append(finding("unexpected workspace child", child,
                                        "canonical clone or reserved directory"))
                continue
            marker = child / ".git"
            if child.name in RESERVED or child.name == ".claude":
                if marker.exists():
                    findings.append(finding("repository occupies reserved directory", child,
                                            workspace / "repository-name"))
                if child.name == "_wt":
                    for entry in sorted(child.iterdir()):
                        prefix, _, slug = entry.name.partition("--")
                        if not prefix or not slug:
                            findings.append(finding("invalid worktree name", entry,
                                                    "<repo-short>--<slug>"))
                continue
            if not marker.is_dir() or _is_link(marker.lstat()):
                findings.append(finding("unexpected workspace child", child,
                                        "canonical clone with local .git", child.name))
                continue
            common = Path(git(child, "rev-parse", "--path-format=absolute",
                              "--git-common-dir").rstrip("\r\n"))
            if common.resolve() != marker.resolve():
                findings.append(finding("unexpected Git common directory", common, marker, child.name))
                continue
            kind = fs_type(child.resolve())
            if not is_local(kind):
                findings.append(finding(f"filesystem {kind}", child,
                                        "local clone filesystem", child.name))
            url = git(child, "remote", "get-url", "origin").strip().rstrip("/")
            name = origin_name(url)
            if origins is not None:
                identity = re.sub(r"^(?:https://|ssh://git@|git@)", "", url).replace(":", "/", 1)
                expected_origin = origins.get(child.name)
                if not expected_origin:
                    findings.append(finding("missing expected origin", child,
                                            "configured repository identity", child.name))
                elif identity.removesuffix(".git") != expected_origin:
                    findings.append(finding("origin identity mismatch", child, expected_origin, child.name))
            if name != child.name:
                findings.append(finding("origin name mismatch", child, workspace / name, child.name))
            records = git(child, "worktree", "list", "--porcelain", "-z")
            paths = [Path(s[9:]) for s in records.split("\0") if s.startswith("worktree ")]
            if not paths or paths[0].resolve() != child.resolve():
                raise OSError("canonical worktree registration missing")
            for registered in paths[1:]:
                physical = registered.resolve()
                expected = workspace / "_wt"
                if expected not in physical.parents:
                    findings.append(finding("worktree outside _wt", registered, expected, child.name))
                elif ledger_trees is not None:
                    ledger_trees.add(registered)
                if not registered.is_dir():
                    findings.append(finding("registered worktree unavailable", registered,
                                            "accessible worktree", child.name))
                    continue
                if registered_roots is not None and expected in physical.parents:
                    registered_roots.add(physical)
                kind = fs_type(physical)
                if not is_local(kind):
                    findings.append(finding(f"filesystem {kind}", registered,
                                            "local worktree filesystem", child.name))
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            findings.append(finding(f"missing evidence ({exc})", child,
                                    "readable clone and worktree metadata", child.name))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=socket.gethostname().split(".")[0].lower())
    parser.add_argument("--repo", type=Path, help="also check this repository's root")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[2]
                        / "config/workstations/work-layout.yaml")
    parser.add_argument("--private-config", type=Path,
                        default=os.environ.get("WORK_LAYOUT_PRIVATE") or None,
                        help="private layout file with client and personal repositories "
                             "(default: $WORK_LAYOUT_PRIVATE)")
    parser.add_argument("--ledger", type=Path, help="work ledger directory (default: <W>/_pm/work)")
    parser.add_argument("--require-ledger", action="store_true", help="report a missing work ledger")
    parser.add_argument("--strict", action="store_true", help="use core repository names")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--json", dest="format", action="store_const", const="json")
    args = parser.parse_args(argv)
    host = args.host.lower()
    findings = []
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        config = {}
        findings.append(finding(f"missing configuration ({exc})", args.config, "readable policy"))
    if args.private_config:
        try:
            merge_private(config, json.loads(Path(args.private_config).read_text(encoding="utf-8")))
        except (ValueError, OSError, AttributeError, TypeError) as exc:
            findings.append(finding(f"missing private layout ({exc.__class__.__name__})",
                                    args.private_config, "readable private layout"))
    try:
        hosts = config["hosts"]
        host_key = next((key for key, value in hosts.items()
                         if host in value.get("hostnames", [])), host)
        policy = hosts[host_key]
        workspace = Path(policy["w"]).expanduser()
        if not workspace.is_absolute():
            raise ValueError("workspace path is not absolute on this machine")
        roots, mounts, unavailable = volume_inventory()
        findings.extend(finding("unreadable volume", path, "readable local filesystem")
                        for path in unavailable)
        if not roots:
            raise OSError("no local filesystem roots enumerated")
        registered_roots = set()
        try:
            kind = filesystem_type(workspace.resolve(strict=True), mounts)
            if not is_local(kind):
                findings.append(finding(f"workspace filesystem {kind}", workspace, "local volume"))
            else:
                ledger_trees = set()
                findings.extend(workspace_children(workspace, lambda p: filesystem_type(p, mounts),
                                                   config.get("origins"), registered_roots, ledger_trees))
                if not _is_link(workspace.lstat()):
                    ledger = args.ledger or workspace / "_pm" / "work"
                    findings.extend(ledger_findings(workspace, ledger, args.require_ledger, ledger_trees))
        except (OSError, RuntimeError) as exc:
            findings.append(finding(f"missing workspace evidence ({exc})", workspace,
                                    "accessible physical workspace"))
        findings.extend(scan_roots(roots, Path.home(), workspace,
                                   [Path(s).expanduser() for s in policy["aliases"]],
                                   [*registered_roots, *(Path(s).expanduser() for s in policy["extra_roots"])],
                                   mounts,
                                   [Path(s).expanduser() for s in policy.get("excluded_parents", [])]))
    except (KeyError, ValueError, OSError, RuntimeError) as exc:
        findings.append(finding(f"missing host evidence ({exc})", host, "configured local host"))
    if args.repo:
        try:
            repo = args.repo.resolve(strict=True)
            name = origin_name(git(repo, "remote", "get-url", "origin").strip().rstrip("/"))
            findings.extend(dict(f, repository=name) for f in
                            repository(repo, config["repositories"][name], args.strict))
        except (KeyError, TypeError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            findings.append(finding(f"missing repository evidence ({exc})", args.repo,
                                    "accessible repository with a configured baseline", args.repo.name))
    for row in findings:
        row["host"] = host
    if args.format == "json":
        print(json.dumps(dict(host=host, findings=findings), indent=2))
    elif findings:
        for row in findings:
            print(f"{host} {row['repository'] or '-'} {row['reason']}: "
                  f"{row['observed']} (expected {row['expected']})")
    else:
        print(f"{host}: complete coverage, no layout drift")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
