#!/usr/bin/env python3
"""Verify Option D hardlink-preserving merge.

For each bucket, confirms every staged file has a corresponding parent file with
same relative path, size, and inode/device (hardlink). Does not delete or modify
source/staging data.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv, os

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "option-d-merge-verification-summary.tsv"
REPORT = ROOT / "option-d-merge-verification-report.md"
DETAIL_DIR = ROOT / "dedupe-merge-assessment"

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

def iter_stage_files(stage: Path):
    for dirpath, _dirnames, filenames in os.walk(stage):
        for name in filenames:
            p = Path(dirpath) / name
            yield p.relative_to(stage).as_posix(), p

def main() -> None:
    rows=[]
    md=[]
    md.append("# Option D merge verification report\n")
    md.append("Every staged file was checked for a corresponding parent file with same relative path, same size, and same device+inode hardlink identity.\n")
    md.append("\n| Order | Bucket | Stage files | Missing in parent | Size mismatches | Not hardlinked | Status |")
    md.append("|---:|---|---:|---:|---:|---:|---|")
    any_bad=False
    for b in BUCKETS:
        missing=[]; size_bad=[]; inode_bad=[]; count=0; bytes_total=0
        detail_path = DETAIL_DIR / f"{b.order:02d}-{b.bucket}.option-d-verify-failures.tsv"
        with detail_path.open('w', newline='', encoding='utf-8') as f:
            w=csv.writer(f, delimiter='\t')
            w.writerow(['relative_path','failure','stage_size','parent_size','stage_dev','parent_dev','stage_inode','parent_inode'])
            for rel, sp in iter_stage_files(b.stage):
                count += 1
                ss = sp.stat()
                bytes_total += ss.st_size
                pp = b.parent / rel
                if not pp.exists():
                    missing.append(rel)
                    w.writerow([rel,'missing',ss.st_size,'',ss.st_dev,'',ss.st_ino,''])
                    continue
                ps = pp.stat()
                if ss.st_size != ps.st_size:
                    size_bad.append(rel)
                    w.writerow([rel,'size_mismatch',ss.st_size,ps.st_size,ss.st_dev,ps.st_dev,ss.st_ino,ps.st_ino])
                if (ss.st_dev, ss.st_ino) != (ps.st_dev, ps.st_ino):
                    inode_bad.append(rel)
                    w.writerow([rel,'not_hardlinked',ss.st_size,ps.st_size,ss.st_dev,ps.st_dev,ss.st_ino,ps.st_ino])
        status='PASS' if not missing and not size_bad and not inode_bad else 'FAIL'
        any_bad = any_bad or status == 'FAIL'
        rows.append([b.order,b.bucket,str(b.parent),str(b.stage),count,bytes_total,len(missing),len(size_bad),len(inode_bad),status,str(detail_path)])
        md.append(f"| {b.order} | `{b.bucket}` | {count:,} | {len(missing):,} | {len(size_bad):,} | {len(inode_bad):,} | {status} |")
    with OUT.open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f, delimiter='\t')
        w.writerow(['order','bucket','parent','stage','stage_file_count','stage_bytes','missing_in_parent','size_mismatches','not_hardlinked','status','detail_failures_tsv'])
        w.writerows(rows)
    md.append("\n## Artifacts\n")
    md.append(f"- Summary TSV: `{OUT}`")
    md.append(f"- Failure detail TSVs: `{DETAIL_DIR}`")
    md.append("\n## Retention guardrail\n")
    md.append("No `_from_elements/` staging folders or `/mnt/elements` source data were deleted by this verification.")
    REPORT.write_text('\n'.join(md)+'\n', encoding='utf-8')
    print(f"Wrote {OUT}")
    print(f"Wrote {REPORT}")
    if any_bad:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
