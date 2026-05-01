#!/usr/bin/env python3
"""Non-destructive readiness check for workspace-hub#2534 retention cleanup.

Does not delete, move, unmount, or modify /mnt/ace or /mnt/elements data.
It verifies current parent-vs-staging hardlink state and reports cleanup candidates.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import csv, os, subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "retention-cleanup-readiness-2534.tsv"
REPORT = ROOT / "retention-cleanup-readiness-2534.md"
DETAIL = ROOT / "retention-cleanup-readiness-2534-failures.tsv"

RETENTION_NOT_BEFORE = "2026-05-28"

@dataclass(frozen=True)
class Bucket:
    order: int
    bucket: str
    parent: Path
    stage: Path

BUCKETS = [
    Bucket(1, "digitalmodel-suction-pile-sizing", Path("/mnt/ace/digitalmodel/references/suction-pile-sizing"), Path("/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements")),
    Bucket(2, "assethold-casa-grande-77017", Path("/mnt/ace/assethold/casa-grande-77017"), Path("/mnt/ace/assethold/casa-grande-77017/_from_elements")),
    Bucket(3, "digitalmodel-qgis", Path("/mnt/ace/digitalmodel/tools/qgis"), Path("/mnt/ace/digitalmodel/tools/qgis/_from_elements")),
    Bucket(4, "digitalmodel-riser-toolbox", Path("/mnt/ace/digitalmodel/references/riser-toolbox"), Path("/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements")),
    Bucket(5, "doris-62092-sesa", Path("/mnt/ace/doris/62092_sesa"), Path("/mnt/ace/doris/62092_sesa/_from_elements")),
    Bucket(6, "doris-university", Path("/mnt/ace/doris/training"), Path("/mnt/ace/doris/training/_from_elements")),
    Bucket(7, "doris-codes-specs", Path("/mnt/ace/doris/codes"), Path("/mnt/ace/doris/codes/_from_elements/codes-doris")),
    Bucket(8, "acma-projects-31522-woodfibre", Path("/mnt/ace/acma-projects/31522-woodfibre-lng"), Path("/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements")),
]

def iter_files(base: Path):
    if not base.exists():
        return
    for dirpath, _, filenames in os.walk(base):
        for name in filenames:
            p = Path(dirpath) / name
            yield p.relative_to(base).as_posix(), p

def mount_state() -> str:
    try:
        return subprocess.check_output(["findmnt", "/mnt/elements", "-o", "TARGET,SOURCE,FSTYPE,OPTIONS", "-n"], text=True).strip()
    except subprocess.CalledProcessError:
        return "NOT_MOUNTED"

def main() -> int:
    now = datetime.now().astimezone()
    retention_elapsed = now.date().isoformat() >= RETENTION_NOT_BEFORE
    rows=[]
    failures=[]
    for b in BUCKETS:
        count=0; bytes_total=0; missing=0; size_mismatch=0; not_hardlinked=0
        for rel, sp in iter_files(b.stage):
            count += 1
            ss = sp.stat()
            bytes_total += ss.st_size
            pp = b.parent / rel
            if not pp.exists():
                missing += 1
                failures.append([b.order,b.bucket,rel,"missing_in_parent",ss.st_size,"","",""])
                continue
            ps = pp.stat()
            if ss.st_size != ps.st_size:
                size_mismatch += 1
                failures.append([b.order,b.bucket,rel,"size_mismatch",ss.st_size,ps.st_size,ss.st_ino,ps.st_ino])
            if (ss.st_dev, ss.st_ino) != (ps.st_dev, ps.st_ino):
                not_hardlinked += 1
                failures.append([b.order,b.bucket,rel,"not_hardlinked",ss.st_size,ps.st_size,ss.st_ino,ps.st_ino])
        status = "READY_AFTER_RETENTION" if not (missing or size_mismatch or not_hardlinked) else "BLOCKED_VERIFICATION_FAILURE"
        rows.append([b.order,b.bucket,str(b.parent),str(b.stage),count,bytes_total,missing,size_mismatch,not_hardlinked,status])

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w=csv.writer(f, delimiter="\t")
        w.writerow(["order","bucket","parent_target","retained_staging","staging_file_count","staging_bytes","missing_in_parent","size_mismatches","not_hardlinked","readiness_status"])
        w.writerows(rows)
    with DETAIL.open("w", newline="", encoding="utf-8") as f:
        w=csv.writer(f, delimiter="\t")
        w.writerow(["order","bucket","relative_path","failure","stage_size","parent_size","stage_inode","parent_inode"])
        w.writerows(failures)

    md=[]
    md.append("# Retention cleanup readiness check — workspace-hub#2534\n")
    md.append(f"Run time: `{now.isoformat(timespec='seconds')}`\n")
    md.append(f"Retention not-before date: `{RETENTION_NOT_BEFORE}`\n")
    md.append(f"Retention elapsed: **{retention_elapsed}**\n")
    md.append(f"Elements mount state: `{mount_state()}`\n")
    md.append("\nNo files were deleted, moved, unmounted, or modified by this check.\n")
    md.append("\n## Cleanup candidate / verification table\n")
    md.append("| Order | Bucket | Parent target | Retained staging | Files | Bytes | Missing | Size mismatches | Not hardlinked | Status |")
    md.append("|---:|---|---|---|---:|---:|---:|---:|---:|---|")
    for r in rows:
        md.append(f"| {r[0]} | `{r[1]}` | `{r[2]}` | `{r[3]}` | {r[4]:,} | {r[5]:,} | {r[6]} | {r[7]} | {r[8]} | {r[9]} |")
    md.append("\n## Decision\n")
    if retention_elapsed and not failures:
        md.append("Retention window appears elapsed and verification passed. Cleanup could proceed only after explicit final deletion approval and a deletion dry-run.")
    elif not retention_elapsed and not failures:
        md.append("Verification passes, but retention window has **not** elapsed. Cleanup deletion/release remains blocked until 2026-05-28 unless the user explicitly overrides the retention policy.")
    else:
        md.append("Cleanup is blocked by verification failures; inspect the failure TSV before any deletion.")
    md.append("\n## Artifacts\n")
    md.append(f"- Summary TSV: `{OUT}`")
    md.append(f"- Failure TSV: `{DETAIL}`")
    REPORT.write_text("\n".join(md)+"\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {DETAIL}")
    print(f"Wrote {REPORT}")
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
