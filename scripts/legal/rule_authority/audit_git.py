"""Raw-byte Git tree, index, ref, and history authority audits."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .git_transport import GitRunner, GitTransportError
from .git_transport import require_empty_object_store, validate_private_modes
from .structural import SensitiveArtifacts, contains_sensitive

OID = re.compile(rb"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")


CoverageError = GitTransportError


@dataclass(frozen=True)
class AuditResult:
    verdict: str
    objects_examined: int
    private_findings: tuple[bytes, ...]
    edges: tuple[tuple[bytes, bytes], ...] = ()


HistoryResult = AuditResult


@dataclass(frozen=True)
class Ref:
    oid: bytes
    name: bytes


@dataclass(frozen=True)
class RefSnapshot:
    refs: tuple[Ref, ...]
    identity: str


def _oid(value: bytes | str) -> bytes:
    try:
        raw = value.encode("ascii") if isinstance(value, str) else value
    except UnicodeEncodeError as exc:
        raise CoverageError("full Git OID required") from exc
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


def _parse_index(raw: bytes, max_entries: int) -> list[tuple[bytes, bytes, bytes]]:
    records = raw[:-1].split(b"\0") if raw else []
    if (raw and not raw.endswith(b"\0")) or len(records) > max_entries:
        raise CoverageError("malformed index inventory")
    entries = []
    for record in records:
        try:
            metadata, path = record.split(b"\t", 1)
            mode, oid, stage = metadata.split(b" ")
        except ValueError as exc:
            raise CoverageError("malformed index inventory") from exc
        if OID.fullmatch(oid) is None or stage != b"0":
            raise CoverageError("unsupported index entry")
        entries.append((path, oid, mode))
    return entries


def parse_ls_remote(raw: bytes, *, max_refs: int) -> RefSnapshot:
    """Parse a complete advertised-ref snapshot as raw bytes."""
    if max_refs < 1 or (raw and not raw.endswith(b"\n")):
        raise CoverageError("malformed ref snapshot")
    lines = raw.splitlines()
    if not lines or len(lines) > max_refs:
        raise CoverageError("ref snapshot empty or capped")
    refs = []
    for line in lines:
        try:
            oid, name = line.split(b"\t", 1)
        except ValueError as exc:
            raise CoverageError("malformed ref snapshot") from exc
        if OID.fullmatch(oid) is None or not name or b"\0" in name:
            raise CoverageError("malformed ref snapshot")
        refs.append(Ref(oid, name))
    if len({ref.name for ref in refs}) != len(refs):
        raise CoverageError("duplicate advertised ref")
    canonical = b"".join(ref.oid + b"\t" + ref.name + b"\n" for ref in refs)
    return RefSnapshot(tuple(refs), hashlib.sha256(canonical).hexdigest())


def require_stable_snapshot(before: RefSnapshot, after: RefSnapshot) -> None:
    if before != after:
        raise CoverageError("advertised refs changed")


class ReachabilityGraph:
    def __init__(self, max_edges: int) -> None:
        if max_edges < 1:
            raise CoverageError("invalid edge cap")
        self.max_edges = max_edges
        self.edges: list[tuple[bytes, bytes]] = []

    def add(self, parent: bytes, child: bytes) -> None:
        if len(self.edges) >= self.max_edges:
            raise CoverageError("edge cap exceeded")
        self.edges.append((parent, child))


def _git_path_exists(runner: GitRunner, path: str) -> bool:
    raw = runner.run("rev-parse", "--git-path", path).strip()
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise CoverageError("unsafe Git path") from exc
    if os.path.isabs(value):
        raise CoverageError("unexpected absolute Git path")
    return runner.has_path(value)


def _reject_substitution(runner: GitRunner) -> None:
    if runner.run("for-each-ref", "--format=%(refname)", "refs/replace").strip():
        raise CoverageError("replacement refs are forbidden")
    for path in ("info/grafts", "objects/info/alternates", "objects/info/http-alternates"):
        if _git_path_exists(runner, path):
            raise CoverageError("object substitution is forbidden")
    partial = runner.optional(
        "config", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$"
    )
    if partial is not None:
        raise CoverageError("partial clone is incomplete")


def _header_oid(raw: bytes, name: bytes) -> bytes:
    prefix = name + b" "
    for line in raw.split(b"\n"):
        if line.startswith(prefix):
            return _oid(line[len(prefix):])
        if not line:
            break
    raise CoverageError("malformed Git object")


class _ObjectWalker:
    def __init__(self, runner: GitRunner, sensitive: SensitiveArtifacts, *,
                 max_entries: int, max_blob_bytes: int, max_objects: int,
                 max_edges: int, include_parents: bool) -> None:
        self.runner, self.sensitive = runner, sensitive
        self.max_entries, self.max_blob_bytes = max_entries, max_blob_bytes
        self.max_objects, self.include_parents = max_objects, include_parents
        self.graph, self.seen = ReachabilityGraph(max_edges), set()
        self.findings: list[bytes] = []
        self.entry_count = 0

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
        size = self.runner.run("cat-file", "-s", oid.decode()).strip()
        if not size.isdigit() or int(size) > self.max_blob_bytes:
            raise CoverageError("blob size cap exceeded")
        raw = self.runner.run("cat-file", "blob", oid.decode())
        if len(raw) != int(size):
            raise CoverageError("blob size changed")
        if contains_sensitive(source, raw, self.sensitive):
            self.findings.append(source)

    def _metadata(self, oid: bytes, kind: bytes) -> None:
        raw = self.runner.run("cat-file", kind.decode(), oid.decode())
        label = b"<" + kind + b">"
        if contains_sensitive(label, raw, self.sensitive):
            self.findings.append(label)
        if kind == b"tag":
            self.walk(_header_oid(raw, b"object"), oid)
            return
        self.walk(_header_oid(raw, b"tree"), oid)
        if self.include_parents:
            for line in raw.split(b"\n"):
                if line.startswith(b"parent "):
                    self.walk(_oid(line[7:]), oid)
                elif not line:
                    break

    def _tree(self, oid: bytes) -> None:
        raw = self.runner.run("cat-file", "tree", oid.decode())
        if contains_sensitive(b"<tree>", raw, self.sensitive):
            self.findings.append(b"<tree>")
        entries = parse_ls_tree(
            self.runner.run("ls-tree", "-z", "--full-tree", oid.decode()),
            max_entries=self.max_entries,
        )
        self.entry_count += len(entries)
        if self.entry_count > self.max_entries:
            raise CoverageError("global tree entry cap exceeded")
        for path, child, kind in entries:
            self.graph.add(oid, path)
            self.graph.add(path, child)
            if contains_sensitive(path, b"", self.sensitive):
                self.findings.append(path)
            if kind != b"commit":
                self.walk(child, path)


def _ref_text(required_ref: bytes) -> str:
    if (not required_ref.startswith(b"refs/") or b"\0" in required_ref or
            b"\n" in required_ref):
        raise CoverageError("invalid required ref")
    try:
        return required_ref.decode("ascii")
    except UnicodeDecodeError as exc:
        raise CoverageError("invalid required ref") from exc


def audit_tree(repo: Path, commit_oid: str, required_ref: bytes,
               sensitive: SensitiveArtifacts, *, max_entries: int,
               max_blob_bytes: int) -> AuditResult:
    """Audit the complete raw object tree bound to one required ref."""
    runner = GitRunner(repo)
    try:
        _reject_substitution(runner)
        ref_text, expected = _ref_text(required_ref), _oid(commit_oid)
        ref_oid = _oid(runner.run("show-ref", "--verify", "--hash", ref_text).strip())
        peeled = _oid(runner.run("rev-parse", f"{ref_text}^{{commit}}").strip())
        if peeled != expected:
            raise CoverageError("required ref does not bind commit")
        walker = _ObjectWalker(
            runner, sensitive, max_entries=max_entries, max_blob_bytes=max_blob_bytes,
            max_objects=max_entries * 3 + 3, max_edges=max_entries * 4 + 8,
            include_parents=False,
        )
        if contains_sensitive(required_ref, b"", sensitive):
            walker.findings.append(required_ref)
        walker.walk(ref_oid, required_ref)
        findings = tuple(walker.findings)
        return AuditResult(
            "blocked" if findings else "clean", len(walker.seen), findings,
            tuple(walker.graph.edges),
        )
    except GitTransportError as exc:
        raise CoverageError("Git coverage failed") from exc
    finally:
        runner.close()


def audit_index(repo: Path, sensitive: SensitiveArtifacts, *, max_entries: int,
                max_blob_bytes: int) -> AuditResult:
    runner = GitRunner(repo)
    try:
        _reject_substitution(runner)
        entries = _parse_index(runner.run("ls-files", "-s", "-z"), max_entries)
        walker = _ObjectWalker(
            runner, sensitive, max_entries=max_entries, max_blob_bytes=max_blob_bytes,
            max_objects=max_entries + 1, max_edges=max_entries * 2 + 1,
            include_parents=False,
        )
        for path, oid, mode in entries:
            walker.graph.add(b"<index>", path)
            if contains_sensitive(path, b"", sensitive):
                walker.findings.append(path)
            if mode == b"160000":
                walker.graph.add(path, oid)
            else:
                walker.walk(oid, path)
        findings = tuple(walker.findings)
        return AuditResult(
            "blocked" if findings else "clean", len(walker.seen), findings,
            tuple(walker.graph.edges),
        )
    except GitTransportError as exc:
        raise CoverageError("Git coverage failed") from exc
    finally:
        runner.close()


def _remote(value: str) -> str:
    if not value or any(character in value for character in "\r\n"):
        raise CoverageError("invalid remote")
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.query:
            raise CoverageError("credential-bearing remote forbidden")
    elif not Path(value).is_absolute():
        raise CoverageError("local remote must be absolute")
    return value


def _snapshot(runner: GitRunner, remote: str, max_refs: int) -> RefSnapshot:
    base = runner.run("ls-remote", remote)
    pulls = runner.run("ls-remote", "--refs", remote, "refs/pull/*/head", "refs/pull/*/merge")
    lines = sorted(set((base + pulls).splitlines()))
    raw = b"".join(line + b"\n" for line in lines)
    snapshot = parse_ls_remote(raw, max_refs=max_refs)
    if any(ref.name.startswith(b"refs/replace/") for ref in snapshot.refs):
        raise CoverageError("remote replacement refs forbidden")
    return snapshot


def _fetch_oids(runner: GitRunner, remote: str, refs: tuple[Ref, ...]) -> None:
    for index, oid in enumerate(dict.fromkeys(ref.oid for ref in refs)):
        target = f"refs/audit/{index:08d}"
        runner.run("fetch", "--no-tags", "--no-write-fetch-head", remote,
                   f"+{oid.decode()}:{target}")


def _require_private_mirror(runner: GitRunner) -> None:
    info = runner.info()
    if info.st_uid != os.getuid():
        raise CoverageError("unsafe private mirror")
    if runner.run("rev-parse", "--is-bare-repository").strip() != b"true":
        raise CoverageError("history audit requires a bare mirror")
    if runner.run("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise CoverageError("shallow history is incomplete")
    validate_private_modes(runner)
    require_empty_object_store(runner)
    _reject_substitution(runner)
    if runner.run("for-each-ref", "--format=%(refname)").strip():
        raise CoverageError("history audit requires a fresh mirror")
    if runner.optional("config", "--get-regexp", r"^remote\..*\.(url|pushurl)$") is not None:
        raise CoverageError("persisted remote configuration forbidden")


def audit_history(repo: Path, remote: str, sensitive: SensitiveArtifacts, *,
                  api_discovered_oids: tuple[bytes, ...], max_refs: int,
                  max_entries: int, max_blob_bytes: int, max_objects: int,
                  max_edges: int) -> HistoryResult:
    """Snapshot, exact-fetch, resnapshot, then audit the full remote surface."""
    runner = GitRunner(repo)
    old_umask = os.umask(0o077)
    try:
        _require_private_mirror(runner)
        remote = _remote(remote)
        before = _snapshot(runner, remote, max_refs)
        api_refs = tuple(Ref(_oid(oid), b"api-discovered") for oid in api_discovered_oids)
        _fetch_oids(runner, remote, (*before.refs, *api_refs))
        validate_private_modes(runner)
        after = _snapshot(runner, remote, max_refs)
        require_stable_snapshot(before, after)
        walker = _ObjectWalker(
            runner, sensitive, max_entries=max_entries, max_blob_bytes=max_blob_bytes,
            max_objects=max_objects, max_edges=max_edges, include_parents=True,
        )
        for ref in before.refs:
            if contains_sensitive(ref.name, b"", sensitive):
                walker.findings.append(ref.name)
            walker.walk(ref.oid, ref.name)
        for ref in api_refs:
            walker.walk(ref.oid, ref.name)
        findings = tuple(walker.findings)
        return AuditResult(
            "blocked" if findings else "clean", len(walker.seen), findings,
            tuple(walker.graph.edges),
        )
    except GitTransportError as exc:
        raise CoverageError("Git history coverage failed") from exc
    finally:
        os.umask(old_umask)
        runner.close()
