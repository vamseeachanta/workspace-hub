"""Bounded, byte-scanning inventory of GitHub-hosted authority surfaces."""

from __future__ import annotations

import io
import re
import stat
import zipfile
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Protocol

from .coverage_contract import GITHUB_SURFACES
from .structural import SensitiveArtifacts, contains_sensitive

REQUIRED_SURFACES = GITHUB_SURFACES
STATES = {"scanned", "queried-no-access", "provider-follow-up", "unknown-residual"}
OID = re.compile(rb"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")


class CoverageError(RuntimeError):
    """GitHub inventory cannot support its claimed coverage."""


@dataclass(frozen=True)
class Download:
    label: bytes
    payload: bytes
    compressed_bytes: int
    expanded_bytes: int


@dataclass(frozen=True)
class ApiPage:
    payload: bytes
    next_cursor: str | None
    etag: str
    edges: int
    state: str = "scanned"
    permission: str = "read"
    discovered_oids: tuple[bytes, ...] = ()
    download_links: int = 0
    downloads: tuple[Download, ...] = ()

    @classmethod
    def no_access(cls, permission: str) -> ApiPage:
        if not permission or not permission.isascii():
            raise CoverageError("invalid permission class")
        return cls(b"", None, permission, 0, "queried-no-access", permission)


@dataclass(frozen=True)
class SurfaceCoverage:
    state: str
    permission: str
    pages: int
    bytes_scanned: int
    edges: int
    downloads: int
    snapshot_identity: str


@dataclass(frozen=True)
class InventoryReport:
    surfaces: dict[str, SurfaceCoverage]
    snapshot_before: str
    snapshot_after: str
    coverage_class: str
    private_findings: tuple[bytes, ...]
    discovered_oids: tuple[bytes, ...]


@dataclass(frozen=True)
class ArchiveResult:
    files: dict[str, bytes]
    private_findings: tuple[bytes, ...]
    compressed_bytes: int
    expanded_bytes: int


class Adapter(Protocol):
    def snapshot(self) -> str: ...
    def page(self, surface: str, cursor: str | None) -> ApiPage: ...


@dataclass
class _Budget:
    limits: tuple[int, int, int, int, int, int]
    counts: list[int] = field(default_factory=lambda: [0] * 6)

    def add(self, *values: int) -> None:
        self.counts = [current + value for current, value in zip(self.counts, values)]
        if any(current > limit for current, limit in zip(self.counts, self.limits)):
            raise CoverageError("inventory cap exceeded")


def _page_evidence(page: ApiPage) -> None:
    if (type(page.payload) is not bytes or type(page.edges) is not int or
            page.state not in STATES or page.edges < 0 or not page.etag or
            not page.permission or not page.permission.isascii()):
        raise CoverageError("invalid surface response")
    if page.download_links < 0 or page.download_links != len(page.downloads):
        raise CoverageError("download evidence incomplete")
    if page.state != "scanned" and (page.payload or page.downloads or page.discovered_oids):
        raise CoverageError("residual surface carried scan evidence")
    if any(OID.fullmatch(oid) is None for oid in page.discovered_oids):
        raise CoverageError("invalid discovered OID")


def _download(surface: str, item: Download, sensitive: SensitiveArtifacts,
              findings: list[bytes]) -> None:
    if (type(item.label) is not bytes or type(item.payload) is not bytes or
            type(item.compressed_bytes) is not int or type(item.expanded_bytes) is not int or
            not item.label or b"\0" in item.label or item.compressed_bytes < 0 or
            item.expanded_bytes != len(item.payload)):
        raise CoverageError("invalid download evidence")
    label = surface.encode() + b":" + item.label
    if contains_sensitive(label, item.payload, sensitive):
        findings.append(label)


def _surface(adapter: Adapter, name: str, sensitive: SensitiveArtifacts,
             budget: _Budget, findings: list[bytes], oids: set[bytes]) -> SurfaceCoverage:
    cursor, seen = None, set()
    pages = byte_count = edges = downloads = 0
    state, permission, identities = "scanned", None, []
    while True:
        if cursor in seen:
            raise CoverageError("pagination cycle")
        seen.add(cursor)
        try:
            page = adapter.page(name, cursor)
        except (KeyError, IndexError) as exc:
            raise CoverageError("surface unavailable") from exc
        _page_evidence(page)
        permission = page.permission if permission is None else permission
        if permission != page.permission:
            raise CoverageError("permission snapshot drift")
        if contains_sensitive(name.encode(), page.payload, sensitive):
            findings.append(name.encode())
        for item in page.downloads:
            _download(name, item, sensitive, findings)
        compressed = sum(item.compressed_bytes for item in page.downloads)
        expanded = sum(item.expanded_bytes for item in page.downloads)
        budget.add(1, len(page.payload), page.edges, len(page.downloads), compressed, expanded)
        pages += 1
        byte_count += len(page.payload)
        edges += page.edges
        downloads += len(page.downloads)
        identities.append(page.etag)
        oids.update(page.discovered_oids)
        state = page.state if page.state != "scanned" else state
        if page.next_cursor is None:
            break
        if not isinstance(page.next_cursor, str) or not page.next_cursor:
            raise CoverageError("invalid pagination cursor")
        cursor = page.next_cursor
    return SurfaceCoverage(state, permission or "none", pages, byte_count, edges,
                           downloads, "|".join(identities))


def inventory(adapter: Adapter, sensitive: SensitiveArtifacts, *, max_pages: int,
              max_bytes: int, max_edges: int, max_downloads: int,
              max_compressed_bytes: int, max_expanded_bytes: int) -> InventoryReport:
    """Scan every required surface with global caps and snapshot stability."""
    limits = (max_pages, max_bytes, max_edges, max_downloads,
              max_compressed_bytes, max_expanded_bytes)
    if min(limits) < 1:
        raise CoverageError("invalid inventory limits")
    before = adapter.snapshot()
    if not isinstance(before, str) or not before:
        raise CoverageError("invalid snapshot")
    budget, findings, oids = _Budget(limits), [], set()
    surfaces = {
        name: _surface(adapter, name, sensitive, budget, findings, oids)
        for name in REQUIRED_SURFACES
    }
    after = adapter.snapshot()
    if before != after:
        raise CoverageError("API snapshot drift")
    complete = all(value.state == "scanned" for value in surfaces.values())
    return InventoryReport(
        surfaces, before, after, "complete" if complete else "partial",
        tuple(findings), tuple(sorted(oids)),
    )


def _archive_name(name: str, max_depth: int) -> str:
    path = PurePosixPath(name)
    if (not name or not name.isascii() or "\\" in name or path.is_absolute() or
            any(part in {"", ".", ".."} for part in path.parts) or
            len(path.parts) > max_depth):
        raise CoverageError("unsafe archive entry")
    return name


def _archive_info(info: zipfile.ZipInfo, *, max_ratio: int, max_depth: int) -> str:
    name = _archive_name(info.filename, max_depth)
    mode, kind = info.external_attr >> 16, stat.S_IFMT(info.external_attr >> 16)
    if info.is_dir() or stat.S_ISLNK(mode) or (kind and not stat.S_ISREG(mode)):
        raise CoverageError("unsupported archive entry")
    if info.flag_bits & 0x1 or info.file_size > max(info.compress_size, 1) * max_ratio:
        raise CoverageError("unsafe archive encoding")
    return name


def scan_zip(raw: bytes, sensitive: SensitiveArtifacts, *, max_entries: int,
             max_compressed_bytes: int, max_expanded_bytes: int,
             max_ratio: int, max_depth: int) -> ArchiveResult:
    """Boundedly extract and scan ZIP bytes without links, devices, or traversal."""
    limits = (max_entries, max_compressed_bytes, max_expanded_bytes, max_ratio, max_depth)
    if min(limits) < 1 or len(raw) > max_compressed_bytes:
        raise CoverageError("invalid archive limits")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            if len(infos) > max_entries:
                raise CoverageError("archive entry cap exceeded")
            names = [_archive_info(info, max_ratio=max_ratio, max_depth=max_depth) for info in infos]
            if len(names) != len(set(names)) or sum(info.file_size for info in infos) > max_expanded_bytes:
                raise CoverageError("archive expansion cap exceeded")
            files = {name: archive.read(info) for name, info in zip(names, infos)}
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise CoverageError("invalid archive") from exc
    findings = tuple(name.encode() for name, payload in files.items()
                     if contains_sensitive(name.encode(), payload, sensitive))
    return ArchiveResult(files, findings, len(raw), sum(map(len, files.values())))
