"""Raw-byte Git tree, index, and ref audit primitives."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .structural import SensitiveArtifacts, contains_sensitive

OID = re.compile(rb"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")


class CoverageError(RuntimeError):
    """Git coverage is malformed, unstable, incomplete, or capped."""


@dataclass(frozen=True)
class AuditResult:
    verdict: str
    objects_examined: int
    private_findings: tuple[bytes, ...]


@dataclass(frozen=True)
class HistoryResult(AuditResult):
    edges: tuple[tuple[bytes, bytes], ...]


@dataclass(frozen=True)
class Ref:
    oid: bytes
    name: bytes


@dataclass(frozen=True)
class RefSnapshot:
    refs: tuple[Ref, ...]
    identity: str


class GitRunner:
    """Invoke Git with argv-only input and a closed noninteractive environment."""

    def __init__(self, repo: Path) -> None:
        self.repo = Path(repo)
        try:
            self._fd = os.open(self.repo, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise CoverageError("Git repository unavailable") from exc
        info = os.fstat(self._fd)
        self.identity = (info.st_dev, info.st_ino)

    def close(self) -> None:
        if getattr(self, "_fd", -1) >= 0:
            os.close(self._fd)
            self._fd = -1

    def __del__(self) -> None:
        self.close()

    def info(self) -> os.stat_result:
        if self._fd < 0:
            raise CoverageError("Git repository handle is closed")
        return os.fstat(self._fd)

    def has_path(self, path: str) -> bool:
        try:
            os.stat(path, dir_fd=self._fd, follow_symlinks=False)
            return True
        except FileNotFoundError:
            return False

    def _execute(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        before = self.info()
        env = {
            "PATH": os.environ.get("PATH", ""), "LANG": "C", "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_LFS_SKIP_SMUDGE": "1",
        }
        command = ["git", "-c", "credential.helper=", "-c", "core.hooksPath=", *args]
        cwd = os.path.join(os.sep, "proc", "self", "fd", str(self._fd))
        result = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, pass_fds=(self._fd,)
        )
        after = self.info()
        if (before.st_dev, before.st_ino) != self.identity or (
                after.st_dev, after.st_ino) != self.identity:
            raise CoverageError("Git repository identity changed")
        return result

    def run(self, *args: str) -> bytes:
        result = self._execute(*args)
        if result.returncode:
            raise CoverageError("Git operation failed")
        return result.stdout

    def optional(self, *args: str) -> bytes | None:
        result = self._execute(*args)
        if result.returncode not in {0, 1}:
            raise CoverageError("Git operation failed")
        return result.stdout if result.returncode == 0 else None


def _oid(value: bytes | str) -> bytes:
    raw = value.encode("ascii") if isinstance(value, str) else value
    if OID.fullmatch(raw) is None:
        raise CoverageError("full Git OID required")
    return raw


def parse_ls_tree(raw: bytes, *, max_entries: int) -> list[tuple[bytes, bytes, bytes]]:
    """Parse NUL-delimited ls-tree output without decoding path bytes."""
    if max_entries < 1 or (raw and not raw.endswith(b"\0")):
        raise CoverageError("malformed tree inventory")
    records = raw[:-1].split(b"\0") if raw else []
    if len(records) > max_entries:
        raise CoverageError("tree entry cap exceeded")
    entries = []
    for record in records:
        try:
            metadata, path = record.split(b"\t", 1)
            mode, kind, oid = metadata.split(b" ")
        except ValueError as exc:
            raise CoverageError("malformed tree inventory") from exc
        if not mode or kind not in {b"blob", b"tree", b"commit"} or OID.fullmatch(oid) is None:
            raise CoverageError("malformed tree inventory")
        entries.append((path, oid, kind))
    return entries


def _parse_index(raw: bytes, max_entries: int) -> list[tuple[bytes, bytes]]:
    records = raw[:-1].split(b"\0") if raw else []
    if (raw and not raw.endswith(b"\0")) or len(records) > max_entries:
        raise CoverageError("malformed index inventory")
    entries = []
    for record in records:
        try:
            metadata, path = record.split(b"\t", 1)
            _mode, oid, stage = metadata.split(b" ")
        except ValueError as exc:
            raise CoverageError("malformed index inventory") from exc
        if OID.fullmatch(oid) is None or stage != b"0":
            raise CoverageError("unsupported index entry")
        entries.append((path, oid))
    return entries


def _scan_objects(runner: GitRunner, entries: list[tuple[bytes, bytes]],
                  sensitive: SensitiveArtifacts, max_blob_bytes: int) -> tuple[bytes, ...]:
    findings = []
    for path, oid in entries:
        size_raw = runner.run("cat-file", "-s", oid.decode("ascii")).strip()
        if not size_raw.isdigit() or int(size_raw) > max_blob_bytes:
            raise CoverageError("blob size cap exceeded")
        payload = runner.run("cat-file", "blob", oid.decode("ascii"))
        if len(payload) != int(size_raw):
            raise CoverageError("blob size changed")
        if contains_sensitive(path, payload, sensitive):
            findings.append(path)
    return tuple(findings)


def audit_tree(repo: Path, commit_oid: str, sensitive: SensitiveArtifacts, *,
               max_entries: int, max_blob_bytes: int) -> AuditResult:
    """Audit an exact commit's raw metadata, paths, and blob bytes without checkout."""
    oid = _oid(commit_oid).decode("ascii")
    runner = GitRunner(repo)
    if runner.run("cat-file", "-t", oid).strip() != b"commit":
        raise CoverageError("named object is not a commit")
    raw_commit = runner.run("cat-file", "commit", oid)
    tree = parse_ls_tree(
        runner.run("ls-tree", "-rz", "--full-tree", oid), max_entries=max_entries
    )
    blobs = [(path, entry_oid) for path, entry_oid, kind in tree if kind == b"blob"]
    findings = list(_scan_objects(runner, blobs, sensitive, max_blob_bytes))
    if contains_sensitive(b"<commit>", raw_commit, sensitive):
        findings.append(b"<commit>")
    return AuditResult("blocked" if findings else "clean", len(blobs) + 1, tuple(findings))


def audit_index(repo: Path, sensitive: SensitiveArtifacts, *, max_entries: int,
                max_blob_bytes: int) -> AuditResult:
    """Audit index authority, never working-tree bytes."""
    runner = GitRunner(repo)
    entries = _parse_index(runner.run("ls-files", "-s", "-z"), max_entries)
    findings = _scan_objects(runner, entries, sensitive, max_blob_bytes)
    return AuditResult("blocked" if findings else "clean", len(entries), findings)


def parse_ls_remote(raw: bytes, *, max_refs: int) -> RefSnapshot:
    """Parse an advertised ref snapshot as raw bytes."""
    if max_refs < 1 or (raw and not raw.endswith(b"\n")):
        raise CoverageError("malformed ref snapshot")
    lines = raw.splitlines()
    if len(lines) > max_refs:
        raise CoverageError("ref cap exceeded")
    refs = []
    for line in lines:
        try:
            oid, name = line.split(b"\t", 1)
        except ValueError as exc:
            raise CoverageError("malformed ref snapshot") from exc
        if OID.fullmatch(oid) is None or not name or b"\0" in name:
            raise CoverageError("malformed ref snapshot")
        refs.append(Ref(oid, name))
    identity = hashlib.sha256(raw).hexdigest()
    return RefSnapshot(tuple(refs), identity)


def require_stable_snapshot(before: RefSnapshot, after: RefSnapshot) -> None:
    if before != after:
        raise CoverageError("advertised refs changed")


class ReachabilityGraph:
    """Bounded reverse-edge retention for private coverage reports."""

    def __init__(self, max_edges: int) -> None:
        if max_edges < 1:
            raise CoverageError("invalid edge cap")
        self.max_edges = max_edges
        self.edges: list[tuple[bytes, bytes]] = []

    def add(self, parent: bytes, child: bytes) -> None:
        if len(self.edges) >= self.max_edges:
            raise CoverageError("edge cap exceeded")
        self.edges.append((parent, child))


def _require_private_mirror(runner: GitRunner) -> None:
    info = runner.info()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
            stat.S_IMODE(info.st_mode) != 0o700):
        raise CoverageError("unsafe private mirror")
    if runner.run("rev-parse", "--is-bare-repository").strip() != b"true":
        raise CoverageError("history audit requires a bare mirror")
    if runner.run("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise CoverageError("shallow history is incomplete")
    if runner.optional("config", "--get-regexp", r"^remote\..*\.promisor$") is not None:
        raise CoverageError("partial clone is incomplete")
    if runner.has_path("objects/info/alternates"):
        raise CoverageError("alternate object store is forbidden")


def _header_oid(raw: bytes, name: bytes) -> bytes:
    prefix = name + b" "
    for line in raw.split(b"\n"):
        if line.startswith(prefix):
            return _oid(line[len(prefix):])
        if not line:
            break
    raise CoverageError("malformed Git object")


class _HistoryWalker:
    def __init__(self, runner: GitRunner, sensitive: SensitiveArtifacts, *,
                 max_entries: int, max_blob_bytes: int, max_objects: int,
                 max_edges: int) -> None:
        self.runner = runner
        self.sensitive = sensitive
        self.max_entries = max_entries
        self.max_blob_bytes = max_blob_bytes
        self.max_objects = max_objects
        self.graph = ReachabilityGraph(max_edges)
        self.seen: set[bytes] = set()
        self.findings: list[bytes] = []

    def walk(self, oid: bytes, source: bytes) -> None:
        self.graph.add(source, oid)
        if oid in self.seen:
            return
        if len(self.seen) >= self.max_objects:
            raise CoverageError("object cap exceeded")
        self.seen.add(oid)
        kind = self.runner.run("cat-file", "-t", oid.decode("ascii")).strip()
        if kind == b"blob":
            self._blob(oid, source)
        elif kind in {b"commit", b"tag"}:
            self._metadata(oid, kind)
        elif kind == b"tree":
            self._tree(oid)
        else:
            raise CoverageError("unsupported Git object")

    def _blob(self, oid: bytes, source: bytes) -> None:
        size = self.runner.run("cat-file", "-s", oid.decode("ascii")).strip()
        if not size.isdigit() or int(size) > self.max_blob_bytes:
            raise CoverageError("blob size cap exceeded")
        raw = self.runner.run("cat-file", "blob", oid.decode("ascii"))
        if len(raw) != int(size):
            raise CoverageError("blob size changed")
        if contains_sensitive(source, raw, self.sensitive):
            self.findings.append(source)

    def _metadata(self, oid: bytes, kind: bytes) -> None:
        raw = self.runner.run("cat-file", kind.decode("ascii"), oid.decode("ascii"))
        if contains_sensitive(b"<" + kind + b">", raw, self.sensitive):
            self.findings.append(b"<" + kind + b">")
        if kind == b"tag":
            self.walk(_header_oid(raw, b"object"), oid)
            return
        self.walk(_header_oid(raw, b"tree"), oid)
        for line in raw.split(b"\n"):
            if line.startswith(b"parent "):
                self.walk(_oid(line[7:]), oid)
            elif not line:
                break

    def _tree(self, oid: bytes) -> None:
        raw = self.runner.run("cat-file", "tree", oid.decode("ascii"))
        if contains_sensitive(b"<tree>", raw, self.sensitive):
            self.findings.append(b"<tree>")
        entries = parse_ls_tree(
            self.runner.run("ls-tree", "-z", "--full-tree", oid.decode("ascii")),
            max_entries=self.max_entries,
        )
        for path, child, kind in entries:
            self.graph.add(oid, path)
            if contains_sensitive(path, b"", self.sensitive):
                self.findings.append(path)
            if kind != b"commit":
                self.walk(child, path)


def audit_history(repo: Path, before: RefSnapshot, after: RefSnapshot,
                  sensitive: SensitiveArtifacts, *, max_entries: int,
                  max_blob_bytes: int, max_objects: int,
                  max_edges: int) -> HistoryResult:
    """Audit all objects reachable from a stable advertised-ref snapshot."""
    require_stable_snapshot(before, after)
    runner = GitRunner(repo)
    _require_private_mirror(runner)
    walker = _HistoryWalker(
        runner, sensitive, max_entries=max_entries, max_blob_bytes=max_blob_bytes,
        max_objects=max_objects, max_edges=max_edges,
    )
    for ref in before.refs:
        if contains_sensitive(ref.name, b"", sensitive):
            walker.findings.append(ref.name)
        walker.walk(ref.oid, ref.name)
    findings = tuple(walker.findings)
    return HistoryResult(
        "blocked" if findings else "clean", len(walker.seen), findings,
        tuple(walker.graph.edges),
    )
