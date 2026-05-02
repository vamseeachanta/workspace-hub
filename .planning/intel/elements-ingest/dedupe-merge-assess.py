#!/usr/bin/env python3
"""Non-mutating dedupe/merge assessment for Elements staged buckets.

Scans each approved _from_elements staging folder and its parent target, excluding
staging folders from the parent inventory. Writes TSV details and Markdown summary.
Does not move, copy, delete, or modify any /mnt/ace data.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple
import csv
import os

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "dedupe-merge-assessment"
SUMMARY_TSV = ROOT / "dedupe-merge-assessment-summary.tsv"
REPORT_MD = ROOT / "dedupe-merge-assessment-report.md"

@dataclass(frozen=True)
class Bucket:
    order: int
    bucket: str
    source_label: str
    parent: Path
    stage: Path
    notes: str = ""

BUCKETS = [
    Bucket(1, "digitalmodel-suction-pile-sizing", "Suction Pile Sizing", Path("/mnt/ace/digitalmodel/references/suction-pile-sizing"), Path("/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements"), "smallest / lowest-risk first"),
    Bucket(2, "assethold-casa-grande-77017", "casa_grande_77017", Path("/mnt/ace/assethold/casa-grande-77017"), Path("/mnt/ace/assethold/casa-grande-77017/_from_elements"), "small real-estate/asset bucket"),
    Bucket(3, "digitalmodel-qgis", "qgis", Path("/mnt/ace/digitalmodel/tools/qgis"), Path("/mnt/ace/digitalmodel/tools/qgis/_from_elements"), "reusable workflow/data"),
    Bucket(4, "digitalmodel-riser-toolbox", "Riser Toolbox", Path("/mnt/ace/digitalmodel/references/riser-toolbox"), Path("/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements"), "engineering reference"),
    Bucket(5, "doris-62092-sesa", "62092  SESA FLNG Terminal Project", Path("/mnt/ace/doris/62092_sesa"), Path("/mnt/ace/doris/62092_sesa/_from_elements"), "likely overlap; review carefully"),
    Bucket(6, "doris-university", "Doris University", Path("/mnt/ace/doris/training"), Path("/mnt/ace/doris/training/_from_elements"), "training material"),
    Bucket(7, "doris-codes-specs", "Codes and Specs", Path("/mnt/ace/doris/codes"), Path("/mnt/ace/doris/codes/_from_elements/codes-doris"), "high file-count overlap risk"),
    Bucket(8, "acma-projects-31522-woodfibre", "Woodfibre", Path("/mnt/ace/acma-projects/31522-woodfibre-lng"), Path("/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements"), "very large; treat as separate reviewed merge"),
]


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def iter_files(base: Path, exclude_dirs: Iterable[Path] = ()) -> Iterable[Tuple[str, int]]:
    exclude_resolved = {p.resolve() for p in exclude_dirs if p.exists()}
    if not base.exists():
        return
    for dirpath, dirnames, filenames in os.walk(base):
        current = Path(dirpath).resolve()
        # Prune excluded directories and any generic _from_elements staging subtree.
        kept = []
        for d in dirnames:
            child = (Path(dirpath) / d).resolve()
            if d == "_from_elements" or child in exclude_resolved:
                continue
            kept.append(d)
        dirnames[:] = kept
        for name in filenames:
            p = Path(dirpath) / name
            try:
                yield rel(p, base), p.stat().st_size
            except FileNotFoundError:
                continue


def inventory(base: Path, exclude_dirs: Iterable[Path] = ()) -> Dict[str, int]:
    return dict(iter_files(base, exclude_dirs))


def write_rows(path: Path, header: list[str], rows: Iterable[Iterable[object]]) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(header)
        for row in rows:
            w.writerow(list(row))
            count += 1
    return count


def fmt_int(n: int) -> str:
    return f"{n:,}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    md = []
    md.append("# Elements dedupe-merge assessment report\n")
    md.append("Non-mutating scan only. No files were copied, moved, merged, overwritten, or deleted.\n")
    md.append("\n## Target table\n")
    md.append("| Order | Bucket | Source folder | Parent target | Staging location | Notes |")
    md.append("|---:|---|---|---|---|---|")
    for b in BUCKETS:
        md.append(f"| {b.order} | `{b.bucket}` | `{b.source_label}` | `{b.parent}` | `{b.stage}` | {b.notes} |")

    md.append("\n## Assessment summary\n")
    md.append("| Order | Bucket | Parent files excl. staging | Stage files | Same path + same size | Same path + different size | Stage-only files | Parent-only files | Recommended next action |")
    md.append("|---:|---|---:|---:|---:|---:|---:|---:|---|")

    for b in BUCKETS:
        parent_inv = inventory(b.parent, [b.stage])
        stage_inv = inventory(b.stage)
        parent_keys = set(parent_inv)
        stage_keys = set(stage_inv)
        same_path = parent_keys & stage_keys
        same_size = sorted(k for k in same_path if parent_inv[k] == stage_inv[k])
        diff_size = sorted(k for k in same_path if parent_inv[k] != stage_inv[k])
        stage_only = sorted(stage_keys - parent_keys)
        parent_only = sorted(parent_keys - stage_keys)

        prefix = OUT_DIR / f"{b.order:02d}-{b.bucket}"
        write_rows(prefix.with_suffix(".same-path-same-size.tsv"), ["relative_path", "size"], ((k, stage_inv[k]) for k in same_size))
        write_rows(prefix.with_suffix(".same-path-different-size.tsv"), ["relative_path", "parent_size", "stage_size"], ((k, parent_inv[k], stage_inv[k]) for k in diff_size))
        write_rows(prefix.with_suffix(".stage-only.tsv"), ["relative_path", "stage_size"], ((k, stage_inv[k]) for k in stage_only))
        write_rows(prefix.with_suffix(".parent-only.tsv"), ["relative_path", "parent_size"], ((k, parent_inv[k]) for k in parent_only))

        if diff_size:
            action = "BLOCK automatic merge; review path-size conflicts first."
        elif stage_only and same_size:
            action = "Dry-run rsync --ignore-existing; parent keeps overlaps, stage-only files are candidates."
        elif stage_only:
            action = "Dry-run rsync --ignore-existing; all staged files appear new by relative path."
        elif same_size and not stage_only:
            action = "No merge needed by relative path+size; staging appears duplicate of parent."
        else:
            action = "No staged files found or nothing to merge."

        stage_bytes = sum(stage_inv.values())
        parent_bytes = sum(parent_inv.values())
        summary_rows.append([
            b.order, b.bucket, str(b.parent), str(b.stage), len(parent_inv), parent_bytes, len(stage_inv), stage_bytes,
            len(same_size), len(diff_size), len(stage_only), len(parent_only), action,
        ])
        md.append(
            f"| {b.order} | `{b.bucket}` | {fmt_int(len(parent_inv))} | {fmt_int(len(stage_inv))} | "
            f"{fmt_int(len(same_size))} | {fmt_int(len(diff_size))} | {fmt_int(len(stage_only))} | {fmt_int(len(parent_only))} | {action} |"
        )

    write_rows(SUMMARY_TSV, [
        "order", "bucket", "parent_target", "staging_location", "parent_file_count_excluding_staging", "parent_bytes_excluding_staging",
        "stage_file_count", "stage_bytes", "same_path_same_size_count", "same_path_different_size_count", "stage_only_count", "parent_only_count", "recommended_next_action",
    ], summary_rows)

    md.append("\n## Detail files\n")
    md.append(f"- Summary TSV: `{SUMMARY_TSV}`")
    md.append(f"- Detail directory: `{OUT_DIR}`")
    md.append("- Per bucket files: `*.stage-only.tsv`, `*.same-path-same-size.tsv`, `*.same-path-different-size.tsv`, `*.parent-only.tsv`")
    md.append("\n## Guardrail\n")
    md.append("This report is an assessment artifact only. Do not merge any bucket until the bucket's conflict table is reviewed and an explicit merge command is approved.")
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {SUMMARY_TSV}")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote detail TSVs under {OUT_DIR}")

if __name__ == "__main__":
    main()
