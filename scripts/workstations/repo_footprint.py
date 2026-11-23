"""Metadata-only footprint receipts for an existing registry selection.

No blob/history walks, repository writes, profile changes or user-file reads.
Only bounded Git locator metadata (.git/commondir) is read as text.
Path categories are storage hints, never evidence-retention decisions.
"""
from __future__ import annotations

import os
import socket
import stat
import subprocess
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

DEPENDENCIES = {".venv", "venv", "node_modules", ".tox", ".nox"}
HEAVY_CANDIDATES = {"data", "datasets", "outputs", "results", "corpus", "extracts", "artifacts"}
CATEGORIES = ("checkout", "dependencies", "heavy_data_candidates", "git")
_WINDOWS = os.name == "nt"


def is_redirect(value: os.stat_result) -> bool:
    """Do not follow symlinks or Windows junction/reparse directories."""
    return stat.S_ISLNK(value.st_mode) or bool(getattr(value, "st_file_attributes", 0) & 0x400)


def _has_symlink_component(path: Path) -> bool:
    for part in (path, *path.parents):
        try:
            if is_redirect(os.lstat(part)):
                return True
        except FileNotFoundError:
            continue  # Missing selected paths are reported as unavailable below.
    return False


def _locator(path: Path, prefix: str = "") -> Path:
    if _has_symlink_component(path):
        raise ValueError("symlink Git locator")
    with path.open("rb") as handle:
        raw = handle.read(8193)
    if len(raw) > 8192:
        raise ValueError("oversized Git locator")
    text = os.fsdecode(raw).strip()
    if not text.startswith(prefix) or "\n" in text:
        raise ValueError("invalid Git locator")
    target = Path(text[len(prefix):])
    target = target if target.is_absolute() else path.parent / target
    if _has_symlink_component(target):
        raise ValueError("symlink Git locator target")
    return target


def allocated_bytes(value: os.stat_result) -> int | None:
    """st_blocks is in 512-byte units; unsupported is not zero or logical size."""
    blocks = getattr(value, "st_blocks", None)
    return blocks * 512 if blocks is not None and blocks >= 0 else None


def _stat_signature(value: os.stat_result) -> tuple:
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns, getattr(value, "st_blocks", None),
            getattr(value, "st_file_attributes", None))


@lru_cache(maxsize=1)
def _windows_api():
    # Loaded only on Windows; POSIX continues to use st_blocks.
    import ctypes
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p,
                                  w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.GetFileInformationByHandleEx.argtypes = [w.HANDLE, ctypes.c_int,
                                                   ctypes.c_void_p, w.DWORD]
    kernel.GetFileInformationByHandleEx.restype = w.BOOL

    class Standard(ctypes.Structure):
        _fields_ = [("allocation", ctypes.c_longlong), ("eof", ctypes.c_longlong),
                    ("links", w.DWORD), ("delete", ctypes.c_ubyte),
                    ("directory", ctypes.c_ubyte)]

    class Basic(ctypes.Structure):
        _fields_ = [(name, ctypes.c_longlong) for name in
                    ("created", "accessed", "written", "changed")] + [("attributes", w.DWORD)]

    return ctypes, kernel, Standard, Basic


def _windows_allocation(path: Path, value: os.stat_result) -> int:
    """Metadata-only handle query, rejecting replacement/redirect/change.

    AllocationSize includes ordinary-file cluster rounding, unlike
    GetCompressedFileSizeW. No flush is attempted on user files: observations
    require a quiescent checkout and cannot prove an atomic disk snapshot.
    """
    ctypes, kernel, Standard, Basic = _windows_api()
    handle = kernel.CreateFileW(str(path.absolute()), 0x80, 7, None, 3, 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    def snapshot():
        standard, basic = Standard(), Basic()
        identity = (ctypes.c_ubyte * 24)()
        for kind, output in ((1, standard), (0, basic), (18, identity)):
            if not kernel.GetFileInformationByHandleEx(handle, kind, ctypes.byref(output), ctypes.sizeof(output)):
                raise ctypes.WinError(ctypes.get_last_error())
        file_id = (int.from_bytes(bytes(identity[:8]), "little"),
                   int.from_bytes(bytes(identity[8:]), "little"))
        return (file_id, standard.allocation, standard.eof, standard.links,
                standard.delete, standard.directory, basic.attributes,
                basic.written, basic.changed)
    try:
        first, second = snapshot(), snapshot()
        if (first != second or first[0] != (value.st_dev, value.st_ino)
                or not value.st_ino or first[2] != value.st_size or first[1] < 0
                or first[4] or first[5] or first[6] & 0x410):
            raise OSError("unstable or redirected Windows file metadata")
        return first[1]
    finally:
        kernel.CloseHandle(handle)


def _file_allocation(path: Path, value: os.stat_result) -> int | None:
    return _windows_allocation(path, value) if _WINDOWS else allocated_bytes(value)


def _empty() -> dict[str, Any]:
    return {"logical_bytes": 0, "known_logical_bytes": 0, "allocated_bytes": 0,
            "known_allocated_bytes": 0, "files": 0}


def _merge(target: dict[str, Any], value: dict[str, Any]) -> None:
    for key in ("logical_bytes", "known_logical_bytes", "known_allocated_bytes", "files"):
        target[key] += value[key]
    if target["allocated_bytes"] is None or value["allocated_bytes"] is None:
        target["allocated_bytes"] = None
    else:
        target["allocated_bytes"] += value["allocated_bytes"]


def _git_dirs(repo: Path) -> tuple[Path, Path]:
    # Git canonicalizes locators; validate redirects BEFORE it hides symlinks.
    metadata = repo / ".git"
    private = _locator(metadata, "gitdir: ") if metadata.is_file() else metadata
    if _has_symlink_component(private):
        raise ValueError("symlink Git metadata")
    if os.path.lexists(private / "commondir"):
        _locator(private / "commondir")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), "rev-parse",
         "--path-format=absolute", "--git-dir", "--git-common-dir"],
        capture_output=True, text=True, check=False, env=env, timeout=15,
    )
    paths = result.stdout.strip().splitlines()
    if result.returncode or len(paths) != 2 or any(not Path(p).is_absolute() for p in paths):
        raise ValueError("cannot resolve local Git metadata")
    return Path(paths[0]), Path(paths[1])


def _selection(data: dict, machine_id: str, selection: str) -> tuple[dict, list[str], str]:
    machine = (data.get("machines") or {}).get(machine_id)
    if not isinstance(machine, dict):
        raise ValueError("unknown registry machine")
    if selection == "required":
        names = (machine.get("tier1_baseline") or {}).get("required")
        suffix = "tier1_baseline.required"
    elif selection == "registered":
        names, suffix = machine.get("repos"), "repos"
    else:
        raise ValueError("selection must be required or registered")
    if not isinstance(names, list) or not names:
        raise ValueError(f"machines.{machine_id}.{suffix} must be a nonempty list")
    for name in names:
        if (not isinstance(name, str) or not name or name in {".", "..", ".git"}
                or any(c in name for c in "/\\:") or any(ord(c) < 32 for c in name)):
            raise ValueError("repository names must be single relative path components")
    return machine, list(dict.fromkeys(names)), f"machines.{machine_id}.{suffix}"


class _Scanner:
    def __init__(self) -> None:
        self.seen: set[tuple[int, int]] = set()
        self.signatures: dict[tuple[int, int], tuple] = {}
        self.issues: list[dict[str, str]] = []
        self.hardlink_aliases = 0
        self.git_breakdown = {key: _empty() for key in ("objects", "lfs", "recovery_backups", "other")}

    def issue(self, code: str, path: Path) -> None:
        self.issues.append({"code": code, "path": str(path)})

    def file(self, path: Path, value: os.stat_result, bucket: dict) -> dict | None:
        if _WINDOWS and is_redirect(value):
            return None
        if _has_symlink_component(path.parent):
            self.issue("symlink_ancestor_excluded", path)
            return None
        try:
            size = _file_allocation(path, value)
        except OSError:
            size = None
            self.issue("allocation_unavailable", path)
        after = os.lstat(path)
        if (_has_symlink_component(path.parent)
                or _stat_signature(after) != _stat_signature(value)):
            self.issue("file_changed_during_scan", path)
            return None
        key = (value.st_dev, value.st_ino)
        if value.st_ino and key in self.seen:
            if self.signatures[key] != _stat_signature(value):
                self.issue("hardlink_changed_during_scan", path)
            self.hardlink_aliases += 1
            return None
        if value.st_ino:
            self.seen.add(key)
            self.signatures[key] = _stat_signature(value)
        measured = {"logical_bytes": value.st_size, "known_logical_bytes": value.st_size,
                    "allocated_bytes": size,
                    "known_allocated_bytes": size or 0, "files": 1}
        _merge(bucket, measured)
        return measured

    def scan(self, root: Path, *, git: bool = False, category_override: str | None = None) -> dict[str, dict]:
        buckets = {key: _empty() for key in CATEGORIES}
        pending = [root]
        directories = []
        while pending:
            path = pending.pop()
            try:
                value = os.lstat(path)
                relative = path.relative_to(root)
                parts = relative.parts
                category = category_override or ("git" if git else (
                    "dependencies" if any(p in DEPENDENCIES for p in parts) else
                    "heavy_data_candidates" if parts and parts[0] in HEAVY_CANDIDATES else "checkout"
                ))
                measured = None
                if is_redirect(value):
                    measured = self.file(path, value, buckets[category])
                    self.issue("symlink_target_excluded", path)
                elif stat.S_ISDIR(value.st_mode):
                    if _has_symlink_component(path):
                        self.issue("symlink_ancestor_excluded", path)
                        continue
                    if path != root and not git and os.path.lexists(path / ".git"):
                        self.issue("nested_repository_excluded", path)
                        continue
                    with os.scandir(path) as entries:
                        pending.extend(sorted((Path(e.path) for e in entries if git or e.name != ".git"), reverse=True))
                    directories.append((path, _stat_signature(value)))
                elif stat.S_ISREG(value.st_mode):
                    measured = self.file(path, value, buckets[category])
                    if git and path.name == "alternates" and path.parent.name == "info" and value.st_size:
                        self.issue("external_git_alternates", path)
                else:
                    self.issue("special_file_excluded", path)
                if git and measured is not None:
                    key = {"objects": "objects", "lfs": "lfs", "recovery-backups": "recovery_backups"}.get(parts[0] if parts else "", "other")
                    _merge(self.git_breakdown[key], measured)
            except OSError:
                self.issue("scan_error", path)
        for path, signature in directories:
            try:
                if _has_symlink_component(path) or _stat_signature(os.lstat(path)) != signature:
                    self.issue("directory_changed_during_scan", path)
            except OSError:
                self.issue("scan_error", path)
        return buckets


def measure_machine(
    data: dict[str, Any], machine_id: str, *, repo_root: Path | None = None,
    selection: str = "required", budget_bytes: int | None = None, now: str | None = None,
    environment_paths: list[Path] | tuple[Path, ...] = (),
) -> dict[str, Any]:
    """Measure a registry-selected local working set, not the whole fleet/inventory."""
    if budget_bytes is not None and budget_bytes <= 0:
        raise ValueError("budget-bytes must be positive")
    environments = list(dict.fromkeys(Path(p) for p in environment_paths))
    if any(not p.is_absolute() for p in environments):
        raise ValueError("explicit environment paths must be absolute")
    machine, names, source = _selection(data, machine_id, selection)
    _, registered, _ = _selection(data, machine_id, "registered")
    configured_root = machine.get("tier1_repo_root") or (machine.get("tier1_baseline") or {}).get("repo_root")
    if not configured_root and machine.get("workspace_root"):
        configured_root = str(Path(machine["workspace_root"]).parent)
    root_value = repo_root or configured_root
    if not root_value or not Path(root_value).is_absolute():
        raise ValueError("an absolute local repo root is required; use --repo-root on another platform")
    root = Path(root_value)
    scanner = _Scanner()
    totals = {key: _empty() for key in CATEGORIES}
    inventory: list[str] = []
    try:
        root_blocked = _has_symlink_component(root)
        if root_blocked:
            scanner.issue("symlink_root_excluded", root)
    except OSError:
        root_blocked = True
        scanner.issue("root_unavailable", root)
    if not root_blocked:
        try:
            with os.scandir(root) as entries:
                inventory = sorted(e.name for e in entries if e.is_dir(follow_symlinks=False)
                                   and os.path.lexists(Path(e.path) / ".git"))
        except OSError:
            scanner.issue("inventory_unavailable", root)
    records, unavailable, stores = [], [], {}
    private_dirs: list[Path] = []
    for name in names:
        path = root / name
        try:
            if root_blocked or path.is_symlink() or not path.is_dir() or not os.path.lexists(path / ".git"):
                raise ValueError("repository unavailable")
            if (path / ".git").is_symlink():
                raise ValueError("symlink Git metadata")
            private, common = _git_dirs(path)
            if _has_symlink_component(common) or _has_symlink_component(private):
                raise ValueError("symlink Git metadata")
            if not common.is_dir() or not private.is_dir():
                raise ValueError("Git metadata directory unavailable")
            common, private = common.resolve(), private.resolve()
        except (ValueError, OSError, subprocess.TimeoutExpired):
            unavailable.append(name)
            scanner.issue("repository_unavailable", path)
            continue
        sizes = scanner.scan(path)
        # Linked-worktree .git pointer is local metadata, not checkout content.
        pointer = path / ".git"
        if pointer.is_file():
            pointer_sizes = scanner.scan(pointer, git=True)
            _merge(sizes["git"], pointer_sizes["git"])
        records.append({"repository": name, "path": str(path), "categories": sizes,
                        "common_git_dir": str(common)})
        for key in CATEGORIES:
            _merge(totals[key], sizes[key])
        entry = stores.setdefault(str(common), {"path": str(common), "repositories": []})
        entry["repositories"].append(name)
        if private != common and common not in private.parents:
            private_dirs.append(private)
    # The shared directory includes its linked-worktree administration directories.
    for entry in stores.values():
        sizes = scanner.scan(Path(entry["path"]), git=True)["git"]
        entry["bytes"] = sizes
        _merge(totals["git"], sizes)
    for path in dict.fromkeys(private_dirs):
        _merge(totals["git"], scanner.scan(path, git=True)["git"])
    environment_records = []
    for path in environments:
        try:
            if _has_symlink_component(path) or not path.is_dir():
                raise OSError("unavailable environment")
            sizes = scanner.scan(path, category_override="dependencies")["dependencies"]
            _merge(totals["dependencies"], sizes)
            environment_records.append({"path": str(path), "bytes": sizes})
        except OSError:
            scanner.issue("environment_unavailable", path)
    total = _empty()
    for value in totals.values():
        _merge(total, value)
    complete = not scanner.issues
    if not complete or total["allocated_bytes"] is None:
        budget_status = "indeterminate"
    elif budget_bytes is None:
        budget_status = "not_configured"
    else:
        budget_status = "within_budget" if total["allocated_bytes"] <= budget_bytes else "exceeded"
    if not complete:
        # Preserve observed lower bounds without representing missing coverage as zero.
        measurements = [total, *totals.values(), *scanner.git_breakdown.values()]
        for record in records:
            measurements.extend(record["categories"].values())
        measurements.extend(entry["bytes"] for entry in stores.values())
        measurements.extend(entry["bytes"] for entry in environment_records)
        for measured in measurements:
            measured["logical_bytes"] = None
            measured["allocated_bytes"] = None
    return {
        "schema_version": 1, "mode": "footprint_only", "machine_id": machine_id,
        "configured_hostname": machine.get("hostname"), "observed_hostname": socket.gethostname(),
        "configured_repo_root": configured_root, "repo_root": str(root),
        "repo_root_overridden": repo_root is not None,
        "measured_at_utc": now or datetime.now(UTC).isoformat(), "selection_source": source,
        "selected_repositories": names, "excluded_repositories": sorted(set(inventory) - set(names)),
        "registered_repositories": registered,
        "registered_not_selected": sorted(set(registered) - set(names)),
        "registered_not_observed": sorted(set(registered) - set(inventory)),
        "selected_not_registered": sorted(set(names) - set(registered)),
        "inventory_repositories": inventory, "unavailable_repositories": unavailable,
        "repositories": records, "git_stores": list(stores.values()), "totals": totals, "total": total,
        "git_breakdown": scanner.git_breakdown,
        "environment_accounting": {"inside_selected_roots": "included",
                                   "explicit_paths": [str(p) for p in environments],
                                   "explicit_measurements": environment_records,
                                   "unlisted_external_environments": "excluded"},
        "allocation_method": "windows_file_standard_info" if _WINDOWS else "posix_st_blocks",
        "complete": complete, "issues": scanner.issues, "hardlink_aliases_deduplicated": scanner.hardlink_aliases,
        "core_profile_verified": False, "runtime_readiness": "not_verified",
        "budget": {"limit_bytes": budget_bytes, "status": budget_status,
                   "scope": "all_selected_local_bytes_including_git_and_dependencies"},
        "measurement_notes": [
            "Existing registry selection only; not approved core/heavy membership or whole-inventory size.",
            "Logical and allocated bytes count file/symlink inodes, not directory entries or reclaimable APFS extents.",
            "Incomplete coverage makes full byte totals null; known_logical_bytes and known_allocated_bytes retain observed lower bounds, and files counts observed inodes.",
            "Unsupported allocated size is null; known_allocated_bytes is a lower bound, never a budget substitute.",
            "No symlink/reparse targets, nested repositories or alternate object stores are followed; exclusions make coverage incomplete.",
            "Categories are disjoint path heuristics, not tracked/ignored status or authorization to delete/migrate.",
            "Dependency directory names: " + ", ".join(sorted(DEPENDENCIES)),
            "Heavy-data candidate top-level names: " + ", ".join(sorted(HEAVY_CANDIDATES)),
            "Git includes objects, LFS and recovery sidecars; common stores and hardlinks are counted once.",
            "Hardlink bytes are attributed to the first path in selection order and sorted directory traversal.",
            "Local sequential observation, not an atomic snapshot, runtime validation or fleet attestation.",
            "Files are checked before/after metadata queries; directories and hardlink aliases are checked for observed changes. Quiescent files are required; concurrent changes may evade sequential checks.",
            "Windows uses handle AllocationSize and file identity; no logical-size fallback, content read, user-file flush or filesystem-metadata overhead estimate.",
            "All files inside selected roots and explicit environments are included. Unlisted external environments are excluded: this budget is not the full runtime footprint.",
        ],
    }
