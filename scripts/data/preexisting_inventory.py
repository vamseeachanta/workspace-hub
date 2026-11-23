from __future__ import annotations

import argparse
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Protocol


DESTRUCTIVE_KINDS = frozenset({"move", "delete", "archive", "compress", "merge"})


class DestructiveActionBlocked(RuntimeError):
    """Raised when a disposition action would mutate source data."""


class FilesystemMutationOps(Protocol):
    def move(self, *args, **kwargs): ...
    def delete(self, *args, **kwargs): ...
    def archive(self, *args, **kwargs): ...
    def compress(self, *args, **kwargs): ...


@dataclass(frozen=True)
class FileRecord:
    source_id: str
    relative_evidence_id: str
    layout_evidence_id: str
    size: int
    mtime_ns: int
    sha256: str
    inode: int | None = None
    device: int | None = None
    hardlink_count: int = 1


@dataclass(frozen=True)
class SymlinkRecord:
    source_id: str
    relative_evidence_id: str
    target_evidence_id: str


@dataclass(frozen=True)
class InventoryError:
    source_id: str
    evidence_id: str
    reason: str


@dataclass
class SourceInventory:
    source_id: str
    source_evidence_id: str
    file_records: list[FileRecord] = field(default_factory=list)
    symlinks: list[SymlinkRecord] = field(default_factory=list)
    errors: list[InventoryError] = field(default_factory=list)
    empty_dir_count: int = 0

    @property
    def file_count(self) -> int:
        return len(self.file_records)

    @property
    def symlink_count(self) -> int:
        return len(self.symlinks)

    @property
    def inaccessible_count(self) -> int:
        return len(self.errors)

    @property
    def hardlink_count(self) -> int:
        return sum(1 for record in self.file_records if record.hardlink_count > 1)

    @property
    def content_fingerprint(self) -> tuple[str, ...]:
        return tuple(sorted(record.sha256 for record in self.file_records))

    @property
    def tree_fingerprint(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                (record.layout_evidence_id, record.sha256)
                for record in self.file_records
            )
        )

    @property
    def content_hashes(self) -> set[str]:
        return {record.sha256 for record in self.file_records}


@dataclass
class InventoryManifest:
    sources: dict[str, SourceInventory]
    _path_to_source_id: dict[Path, str]

    def source_id(self, path: Path) -> str:
        return self._path_to_source_id[path.resolve()]


@dataclass(frozen=True)
class DispositionRecommendation:
    source_id: str
    classification: str
    reason: str
    related_source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecommendationSet:
    by_source: dict[str, DispositionRecommendation]


@dataclass(frozen=True)
class DispositionAction:
    kind: str
    source_id: str
    target_id: str | None = None


def build_inventory(roots: Iterable[Path | str]) -> InventoryManifest:
    resolved_roots = sorted({Path(root).resolve() for root in roots}, key=lambda path: str(path))
    path_to_source_id = {root: f"source:{index:04d}" for index, root in enumerate(resolved_roots, start=1)}
    sources: dict[str, SourceInventory] = {}

    for root in resolved_roots:
        source_id = path_to_source_id[root]
        source = SourceInventory(source_id=source_id, source_evidence_id=_evidence_id(root))
        if _root_is_scannable(root, source):
            _walk_source(root, root, source)
        sources[source_id] = source

    return InventoryManifest(sources=sources, _path_to_source_id=path_to_source_id)


def recommend_disposition(manifest: InventoryManifest) -> RecommendationSet:
    exact_groups: dict[tuple[tuple[str, str], ...], list[str]] = defaultdict(list)
    hash_to_sources: dict[str, set[str]] = defaultdict(set)

    for source_id, source in manifest.sources.items():
        if source.tree_fingerprint and not source.inaccessible_count:
            exact_groups[source.tree_fingerprint].append(source_id)
        for content_hash in source.content_hashes:
            hash_to_sources[content_hash].add(source_id)

    recommendations: dict[str, DispositionRecommendation] = {}
    for source_id, source in manifest.sources.items():
        exact_peers = tuple(sorted(peer for peer in exact_groups[source.tree_fingerprint] if peer != source_id))
        overlapping = tuple(
            sorted(
                {
                    peer
                    for content_hash in source.content_hashes
                    for peer in hash_to_sources[content_hash]
                    if peer != source_id
                }
            )
        )

        if source.inaccessible_count:
            recommendations[source_id] = DispositionRecommendation(
                source_id=source_id,
                classification="incomplete_scan",
                reason="one or more paths could not be inspected; disposition must remain conservative",
                related_source_ids=overlapping,
            )
        elif exact_peers:
            recommendations[source_id] = DispositionRecommendation(
                source_id=source_id,
                classification="exact_duplicate_tree",
                reason="all file content hashes match at least one other source",
                related_source_ids=exact_peers,
            )
        elif overlapping:
            recommendations[source_id] = DispositionRecommendation(
                source_id=source_id,
                classification="partial_overlap",
                reason="one or more content hashes appear in another source",
                related_source_ids=overlapping,
            )
        elif source.file_count == 0:
            recommendations[source_id] = DispositionRecommendation(
                source_id=source_id,
                classification="empty_only",
                reason="source contains no regular files to deduplicate or move",
            )
        else:
            recommendations[source_id] = DispositionRecommendation(
                source_id=source_id,
                classification="unique_only",
                reason="no content hashes overlap another source",
            )

    return RecommendationSet(by_source=recommendations)


def public_summary(manifest: InventoryManifest, recommendations: RecommendationSet) -> list[str]:
    lines = [
        "# Preexisting Data Inventory Summary",
        "",
        "This repo-tracked summary is metadata-only and redacted; "
        "the private scan computes content digests for deduplication but emits "
        "no file contents, raw paths, or client filenames.",
    ]
    for source_id in sorted(manifest.sources):
        source = manifest.sources[source_id]
        recommendation = recommendations.by_source[source_id]
        lines.append(
            " | ".join(
                [
                    f"source: {source_id}",
                    "evidence: redacted",
                    f"classification: {recommendation.classification}",
                    f"files: {source.file_count}",
                    f"empty_dirs: {source.empty_dir_count}",
                    f"symlinks: {source.symlink_count}",
                    f"hardlinks: {source.hardlink_count}",
                    f"inaccessible: {source.inaccessible_count}",
                ]
            )
        )
    return lines


def write_public_summary(roots: Iterable[Path | str], output_path: Path | str) -> Path:
    """Build a metadata-only inventory and write the redacted public summary."""
    manifest = build_inventory(roots)
    recommendations = recommend_disposition(manifest)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(public_summary(manifest, recommendations)) + "\n", encoding="utf-8")
    return output


def execute_disposition_actions(
    actions: Iterable[DispositionAction],
    *,
    fs_ops: FilesystemMutationOps,
    dry_run: bool = True,
) -> None:
    action_list = list(actions)
    blocked = [action.kind for action in action_list if action.kind in DESTRUCTIVE_KINDS]
    if blocked:
        raise DestructiveActionBlocked(
            "Phase A is metadata-only; destructive disposition actions are blocked: "
            + ", ".join(sorted(set(blocked)))
        )
    if not dry_run:
        raise DestructiveActionBlocked("Phase A only supports dry-run metadata generation.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a metadata-only, redacted inventory for preexisting data folders."
    )
    parser.add_argument("roots", nargs="+", help="Preexisting data roots to inventory")
    parser.add_argument(
        "--summary-out",
        required=True,
        help="Output Markdown path for the redacted public summary",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Compatibility flag; Phase A is always dry-run and metadata-only.",
    )
    args = parser.parse_args(argv)
    write_public_summary(args.roots, args.summary_out)
    return 0


def _walk_source(root: Path, current: Path, source: SourceInventory) -> None:
    try:
        children = list(current.iterdir())
    except PermissionError:
        source.errors.append(
            InventoryError(
                source_id=source.source_id,
                evidence_id=_relative_evidence_id(root, current, source.source_id),
                reason="permission_denied",
            )
        )
        return
    except OSError as exc:
        source.errors.append(
            InventoryError(
                source_id=source.source_id,
                evidence_id=_relative_evidence_id(root, current, source.source_id),
                reason=type(exc).__name__.lower(),
            )
        )
        return

    if not children:
        source.empty_dir_count += 1
        return

    for child in children:
        try:
            if child.is_symlink():
                source.symlinks.append(
                    SymlinkRecord(
                        source_id=source.source_id,
                        relative_evidence_id=_relative_evidence_id(
                            root, child, source.source_id
                        ),
                        target_evidence_id=_evidence_id(Path("symlink-target") / _safe_readlink(child)),
                    )
                )
                continue
            if child.is_dir():
                _walk_source(root, child, source)
                continue
            if child.is_file():
                source.file_records.append(_file_record(root, child, source.source_id))
        except OSError as exc:
            source.errors.append(
                InventoryError(
                    source_id=source.source_id,
                    evidence_id=_relative_evidence_id(root, child, source.source_id),
                    reason=type(exc).__name__.lower(),
                )
            )


def _root_is_scannable(root: Path, source: SourceInventory) -> bool:
    try:
        if not root.exists():
            source.errors.append(InventoryError(source.source_id, _evidence_id(root), "missing_root"))
            return False
        if not root.is_dir():
            source.errors.append(InventoryError(source.source_id, _evidence_id(root), "not_directory"))
            return False
    except OSError as exc:
        source.errors.append(InventoryError(source.source_id, _evidence_id(root), type(exc).__name__.lower()))
        return False
    return True


def _file_record(root: Path, path: Path, source_id: str) -> FileRecord:
    stat = path.stat()
    return FileRecord(
        source_id=source_id,
        relative_evidence_id=_relative_evidence_id(root, path, source_id),
        layout_evidence_id=_layout_evidence_id(root, path),
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        sha256=_hash_file(path),
        inode=stat.st_ino,
        device=stat.st_dev,
        hardlink_count=stat.st_nlink,
    )


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_evidence_id(root: Path, path: Path, source_id: str) -> str:
    return _evidence_id(f"{source_id}:{_relative_path_token(root, path)}")


def _layout_evidence_id(root: Path, path: Path) -> str:
    return _evidence_id(_relative_path_token(root, path))


def _relative_path_token(root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = Path(path.name)
    return relative.as_posix()


def _evidence_id(value: Path | str) -> str:
    return hashlib.sha256(str(value).encode("utf-8", errors="surrogateescape")).hexdigest()[:16]


def _safe_readlink(path: Path) -> str:
    try:
        return os.readlink(path)
    except OSError:
        return "unreadable"


if __name__ == "__main__":
    raise SystemExit(main())
