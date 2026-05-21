"""Issue #2769 — ACMA pre-move backup disposition reporting (Phase A dry-run).

Composes over scripts/data/preexisting_inventory.py to produce a metadata-only,
public-safe comparison of a single backup root against the corresponding active
root. The output is repo-tracked, redacted, and never emits a destructive
command. All disposition execution is deferred to a separately approved
execution issue per the workspace hard gate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, NamedTuple, Sequence


_PREEXISTING_PATH = Path(__file__).resolve().parent / "preexisting_inventory.py"
_spec = importlib.util.spec_from_file_location("preexisting_inventory", _PREEXISTING_PATH)
assert _spec is not None and _spec.loader is not None
_preexisting = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("preexisting_inventory", _preexisting)
_spec.loader.exec_module(_preexisting)


ELEVATED_THRESHOLD = 0.85
HIGH_THRESHOLD = 0.95
DESTRUCTIVE_KINDS = frozenset({"move", "delete", "archive", "compress", "merge", "tar"})
ALLOWED_KINDS = frozenset({"retain", "report_only"})


class DestructiveActionBlocked(RuntimeError):
    """Raised when a disposition action would mutate source data at Phase A."""


class OutputResidencyBlocked(RuntimeError):
    """Raised when Phase A output would write outside repo-controlled space."""


class DiskUsageTriple(NamedTuple):
    total: int
    used: int
    free: int


@dataclass(frozen=True)
class DiskPressureSnapshot:
    capacity_bytes: int
    used_bytes: int
    free_bytes: int
    used_fraction: float
    severity: str
    threshold_exceeded: bool


@dataclass(frozen=True)
class BackupComparison:
    backup_evidence_id: str
    active_evidence_id: str
    classification: str
    overlap_file_count: int
    unique_file_count: int
    backup_file_count: int
    active_file_count: int
    backup_inaccessible_count: int
    active_inaccessible_count: int
    reason: str


@dataclass(frozen=True)
class BlockedByItem:
    issue_id: str
    status: str


@dataclass(frozen=True)
class BackupDispositionReport:
    comparison: BackupComparison
    disk_pressure: DiskPressureSnapshot
    blocked_by: tuple[BlockedByItem, ...]
    disposition_status: str
    recommended_action: str


@dataclass(frozen=True)
class DispositionExecutionResult:
    kind: str
    backup_source_id: str
    executed: bool


def compare_backup_to_active(backup_root: Path | str, active_root: Path | str) -> BackupComparison:
    backup_path = Path(backup_root)
    active_path = Path(active_root)
    manifest = _preexisting.build_inventory([backup_path, active_path])
    backup = manifest.sources[manifest.source_id(backup_path)]
    active = manifest.sources[manifest.source_id(active_path)]

    if backup.inaccessible_count or active.inaccessible_count:
        return BackupComparison(
            backup_evidence_id=_evidence_id(backup_path),
            active_evidence_id=_evidence_id(active_path),
            classification="incomplete_scan",
            overlap_file_count=0,
            unique_file_count=0,
            backup_file_count=backup.file_count,
            active_file_count=active.file_count,
            backup_inaccessible_count=backup.inaccessible_count,
            active_inaccessible_count=active.inaccessible_count,
            reason="one or more paths could not be inspected; comparison is non-authoritative",
        )

    active_hashes = active.content_hashes
    overlap_file_count = sum(
        1 for record in backup.file_records if record.sha256 in active_hashes
    )
    unique_file_count = backup.file_count - overlap_file_count

    if backup.file_count == 0:
        classification = "entirely_unique"
        reason = "backup contains no files; nothing to compare"
    elif unique_file_count == 0:
        classification = "fully_redundant"
        reason = "every backup file hash appears in the active tree"
    elif overlap_file_count == 0:
        classification = "entirely_unique"
        reason = "no backup file hash appears in the active tree"
    else:
        classification = "partially_unique"
        reason = "some backup file hashes appear in the active tree, others do not"

    return BackupComparison(
        backup_evidence_id=_evidence_id(backup_path),
        active_evidence_id=_evidence_id(active_path),
        classification=classification,
        overlap_file_count=overlap_file_count,
        unique_file_count=unique_file_count,
        backup_file_count=backup.file_count,
        active_file_count=active.file_count,
        backup_inaccessible_count=0,
        active_inaccessible_count=0,
        reason=reason,
    )


def measure_disk_pressure(
    mount_path: Path | str,
    *,
    disk_usage_fn: Callable[[Path | str], DiskUsageTriple] = shutil.disk_usage,
) -> DiskPressureSnapshot:
    triple = disk_usage_fn(mount_path)
    total = int(triple.total)
    used = int(triple.used)
    free = int(triple.free)
    used_fraction = used / total if total > 0 else 0.0
    if used_fraction >= HIGH_THRESHOLD:
        severity = "high"
        threshold_exceeded = True
    elif used_fraction >= ELEVATED_THRESHOLD:
        severity = "elevated"
        threshold_exceeded = True
    else:
        severity = "normal"
        threshold_exceeded = False
    return DiskPressureSnapshot(
        capacity_bytes=total,
        used_bytes=used,
        free_bytes=free,
        used_fraction=used_fraction,
        severity=severity,
        threshold_exceeded=threshold_exceeded,
    )


def build_disposition_report(
    *,
    backup_root: Path | str,
    active_root: Path | str,
    mount_path: Path | str,
    blocked_by: Sequence[BlockedByItem] = (),
    disk_usage_fn: Callable[[Path | str], DiskUsageTriple] = shutil.disk_usage,
) -> BackupDispositionReport:
    comparison = compare_backup_to_active(backup_root, active_root)
    disk_pressure = measure_disk_pressure(mount_path, disk_usage_fn=disk_usage_fn)
    blocked_by_tuple = tuple(blocked_by)

    open_deps = [item for item in blocked_by_tuple if item.status.lower() != "closed"]

    if open_deps:
        disposition_status = "blocked"
        recommended_action = "deferred:dependency_open"
    elif comparison.classification == "incomplete_scan":
        disposition_status = "blocked"
        recommended_action = "deferred:incomplete_scan"
    elif disk_pressure.severity == "high":
        disposition_status = "blocked"
        recommended_action = "deferred:high_disk_pressure_requires_human_review"
    else:
        disposition_status = "ready_for_recommendation"
        recommended_action = "deferred:awaiting_approved_execution_issue"

    return BackupDispositionReport(
        comparison=comparison,
        disk_pressure=disk_pressure,
        blocked_by=blocked_by_tuple,
        disposition_status=disposition_status,
        recommended_action=recommended_action,
    )


def render_public_report(report: BackupDispositionReport) -> list[str]:
    pressure = report.disk_pressure
    comp = report.comparison
    lines = [
        "# ACMA Pre-Move Backup Disposition Report (Phase A, dry-run)",
        "",
        (
            "This report is metadata-only and redacted. It compares one backup "
            "source against the corresponding active source by content hash. "
            "No file contents, raw paths, client names, or filenames are "
            "emitted. Disposition execution (delete/move/archive/compress) is "
            "out of scope for this phase; a separately approved execution "
            "issue is required before any destructive command may run."
        ),
        "",
        "## Comparison",
        f"- backup_evidence: {comp.backup_evidence_id}",
        f"- active_evidence: {comp.active_evidence_id}",
        f"- classification: {comp.classification}",
        f"- backup_file_count: {comp.backup_file_count}",
        f"- active_file_count: {comp.active_file_count}",
        f"- overlap_file_count: {comp.overlap_file_count}",
        f"- unique_file_count: {comp.unique_file_count}",
        f"- backup_inaccessible_count: {comp.backup_inaccessible_count}",
        f"- active_inaccessible_count: {comp.active_inaccessible_count}",
        f"- reason: {comp.reason}",
        "",
        "## Disk pressure",
        f"- capacity_bytes: {pressure.capacity_bytes}",
        f"- used_bytes: {pressure.used_bytes}",
        f"- free_bytes: {pressure.free_bytes}",
        f"- used_fraction: {pressure.used_fraction:.4f}",
        f"- severity: {pressure.severity}",
        f"- threshold_exceeded: {pressure.threshold_exceeded}",
        "",
        "## Gates",
        f"- disposition_status: {report.disposition_status}",
        f"- recommended_action: {report.recommended_action}",
    ]
    if report.blocked_by:
        lines.append("- blocked_by:")
        for item in report.blocked_by:
            lines.append(f"  - {item.issue_id} status={item.status}")
    else:
        lines.append("- blocked_by: (none declared)")
    lines.extend(
        [
            "",
            "## Non-emission contract",
            (
                "- This document intentionally contains no shell commands. "
                "Any future destructive action requires a separate plan and "
                "explicit status:plan-approved on a new execution issue."
            ),
        ]
    )
    return lines


def write_disposition_report(
    *,
    backup_root: Path | str,
    active_root: Path | str,
    mount_path: Path | str,
    blocked_by: Sequence[BlockedByItem] = (),
    output_path: Path | str,
    disk_usage_fn: Callable[[Path | str], DiskUsageTriple] = shutil.disk_usage,
) -> Path:
    report = build_disposition_report(
        backup_root=backup_root,
        active_root=active_root,
        mount_path=mount_path,
        blocked_by=blocked_by,
        disk_usage_fn=disk_usage_fn,
    )
    output = _validated_output_path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(render_public_report(report)) + "\n", encoding="utf-8")
    return output


def _validated_output_path(output_path: Path | str) -> Path:
    output = Path(output_path)
    resolved = output.expanduser().resolve(strict=False)
    mnt_ace = Path("/mnt/ace").resolve(strict=False)
    if resolved == mnt_ace or mnt_ace in resolved.parents:
        raise OutputResidencyBlocked("Phase A reports must not be written to data roots.")
    repo_root = Path.cwd().resolve(strict=False)
    if output.is_absolute() and resolved != repo_root and repo_root not in resolved.parents:
        raise OutputResidencyBlocked(
            "Phase A reports must be written inside the current repo/worktree."
        )
    return output


def execute_disposition_recommendation(
    *,
    action_kind: str,
    backup_source_id: str,
    dry_run: bool = True,
) -> DispositionExecutionResult:
    if action_kind in DESTRUCTIVE_KINDS:
        raise DestructiveActionBlocked(
            f"Phase A blocks destructive disposition kind: {action_kind!r}. "
            "Open a separate execution issue and obtain status:plan-approved."
        )
    if action_kind not in ALLOWED_KINDS:
        raise DestructiveActionBlocked(
            f"Phase A only permits {sorted(ALLOWED_KINDS)}; got {action_kind!r}."
        )
    if not dry_run:
        raise DestructiveActionBlocked(
            "Phase A only supports dry-run; live execution requires a separate "
            "approved issue."
        )
    return DispositionExecutionResult(
        kind=action_kind, backup_source_id=backup_source_id, executed=False
    )


def _evidence_id(value: Path | str) -> str:
    return hashlib.sha256(str(value).encode("utf-8", errors="surrogateescape")).hexdigest()[:16]


def _parse_blocked_by(values: Iterable[str]) -> list[BlockedByItem]:
    parsed: list[BlockedByItem] = []
    for raw in values:
        if not raw:
            continue
        if ":" not in raw:
            raise ValueError("--blocked-by entry must be 'issue_id:status'")
        issue_id, status = raw.split(":", 1)
        issue_id = issue_id.strip()
        status = status.strip().lower()
        if not re.fullmatch(r"#\d+", issue_id):
            raise ValueError(
                "--blocked-by issue_id must be a redacted GitHub issue reference like '#2747'"
            )
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", status):
            raise ValueError("--blocked-by status must be a compact status token")
        parsed.append(BlockedByItem(issue_id=issue_id, status=status))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Issue #2769 Phase A — produce a metadata-only, redacted disposition "
            "report comparing one backup root against the corresponding active root."
        )
    )
    parser.add_argument("--backup-root", required=True)
    parser.add_argument("--active-root", required=True)
    parser.add_argument("--mount-path", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--blocked-by",
        action="append",
        default=[],
        help="Dependency entry of the form 'issue_id:status'. Repeatable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Compatibility flag; Phase A is always dry-run and metadata-only.",
    )
    args = parser.parse_args(argv)
    blocked = _parse_blocked_by(args.blocked_by)
    write_disposition_report(
        backup_root=args.backup_root,
        active_root=args.active_root,
        mount_path=args.mount_path,
        blocked_by=blocked,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
