"""Hermetic, bounded inventory of GitHub-hosted legal-audit surfaces."""

from __future__ import annotations

import io
import stat
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Protocol

REQUIRED_SURFACES = (
    "actions", "artifacts", "caches", "comments", "commit-comments", "commits",
    "discussions", "forks", "git-trees", "issues", "lfs", "packages", "pages",
    "pulls", "release-assets", "releases", "review-comments", "reviews", "rulesets",
    "run-logs", "timeline", "wiki",
)
STATES = {"scanned", "queried-no-access", "provider-follow-up", "unknown-residual"}


class CoverageError(RuntimeError):
    """GitHub inventory cannot support a complete verdict."""


@dataclass(frozen=True)
class ApiPage:
    payload: bytes
    next_cursor: str | None
    etag: str
    edges: int
    state: str = "scanned"

    @classmethod
    def no_access(cls, permission: str) -> ApiPage:
        if not permission or not permission.isascii():
            raise CoverageError("invalid permission class")
        return cls(b"", None, permission, 0, "queried-no-access")


@dataclass(frozen=True)
class SurfaceCoverage:
    state: str
    pages: int
    bytes_scanned: int
    edges: int
    snapshot_identity: str


@dataclass(frozen=True)
class InventoryReport:
    surfaces: dict[str, SurfaceCoverage]
    snapshot_before: str
    snapshot_after: str
    coverage_class: str


class Adapter(Protocol):
    def snapshot(self) -> str: ...
    def page(self, surface: str, cursor: str | None) -> ApiPage: ...


def _surface(adapter: Adapter, name: str, budget: list[int]) -> SurfaceCoverage:
    cursor = None
    seen: set[str | None] = set()
    pages = byte_count = edges = 0
    state = "scanned"
    identities = []
    while True:
        if cursor in seen:
            raise CoverageError("pagination cycle")
        seen.add(cursor)
        try:
            page = adapter.page(name, cursor)
        except (KeyError, IndexError) as exc:
            raise CoverageError("surface unavailable") from exc
        if page.state not in STATES or page.edges < 0 or not page.etag:
            raise CoverageError("invalid surface response")
        pages += 1
        budget[0] += 1
        byte_count += len(page.payload)
        budget[1] += len(page.payload)
        edges += page.edges
        identities.append(page.etag)
        state = page.state if page.state != "scanned" else state
        if budget[0] > budget[2] or budget[1] > budget[3]:
            raise CoverageError("inventory cap exceeded")
        if page.next_cursor is None:
            break
        if not isinstance(page.next_cursor, str) or not page.next_cursor:
            raise CoverageError("invalid pagination cursor")
        cursor = page.next_cursor
    return SurfaceCoverage(state, pages, byte_count, edges, "|".join(identities))


def inventory(adapter: Adapter, *, max_pages: int, max_bytes: int) -> InventoryReport:
    """Inventory every required surface with before/after snapshot stability."""
    if max_pages < 1 or max_bytes < 1:
        raise CoverageError("invalid inventory limits")
    before = adapter.snapshot()
    if not isinstance(before, str) or not before:
        raise CoverageError("invalid snapshot")
    budget = [0, 0, max_pages, max_bytes]
    surfaces = {name: _surface(adapter, name, budget) for name in REQUIRED_SURFACES}
    after = adapter.snapshot()
    if before != after:
        raise CoverageError("API snapshot drift")
    complete = all(value.state == "scanned" for value in surfaces.values())
    return InventoryReport(surfaces, before, after, "complete" if complete else "partial")


def _archive_name(name: str, max_depth: int) -> str:
    path = PurePosixPath(name)
    if (not name or not name.isascii() or path.is_absolute() or
            any(part in {"", ".", ".."} for part in path.parts) or
            len(path.parts) > max_depth):
        raise CoverageError("unsafe archive entry")
    return name


def _archive_info(info: zipfile.ZipInfo, *, max_ratio: int, max_depth: int) -> str:
    name = _archive_name(info.filename, max_depth)
    mode = info.external_attr >> 16
    kind = stat.S_IFMT(mode)
    if info.is_dir() or stat.S_ISLNK(mode) or (kind and not stat.S_ISREG(mode)):
        raise CoverageError("unsupported archive entry")
    if info.flag_bits & 0x1:
        raise CoverageError("encrypted archive entry")
    compressed = max(info.compress_size, 1)
    if info.file_size > compressed * max_ratio:
        raise CoverageError("archive expansion ratio exceeded")
    return name


def scan_zip(raw: bytes, *, max_entries: int, max_expanded_bytes: int,
             max_ratio: int, max_depth: int) -> dict[str, bytes]:
    """Boundedly extract a ZIP fixture without links, devices, or traversal."""
    if min(max_entries, max_expanded_bytes, max_ratio, max_depth) < 1:
        raise CoverageError("invalid archive limits")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            if len(infos) > max_entries:
                raise CoverageError("archive entry cap exceeded")
            names = [_archive_info(info, max_ratio=max_ratio, max_depth=max_depth)
                     for info in infos]
            if len(names) != len(set(names)):
                raise CoverageError("duplicate archive entry")
            if sum(info.file_size for info in infos) > max_expanded_bytes:
                raise CoverageError("archive expanded-byte cap exceeded")
            result = {name: archive.read(info) for name, info in zip(names, infos)}
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise CoverageError("invalid archive") from exc
    if sum(map(len, result.values())) > max_expanded_bytes:
        raise CoverageError("archive expanded-byte cap exceeded")
    return result
