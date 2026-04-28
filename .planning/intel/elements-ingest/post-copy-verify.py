#!/usr/bin/env python3
"""Post-copy verification for Elements staged ingest (workspace-hub#2526).

Reads source and destination trees, compares relative file paths and sizes for each
approved staged bucket, and writes TSV/Markdown verification artifacts. Does not
modify source or destination data.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import os

BASE = Path('/mnt/local-analysis/workspace-hub/.planning/intel/elements-ingest')
SRC = Path('/mnt/elements')

@dataclass(frozen=True)
class Bucket:
    tag: str
    source_rel: str
    dest: Path

BUCKETS = [
    Bucket('doris-62092-sesa', '62092  SESA FLNG Terminal Project', Path('/mnt/ace/doris/62092_sesa/_from_elements')),
    Bucket('assethold-casa-grande-77017', 'casa_grande_77017', Path('/mnt/ace/assethold/casa-grande-77017/_from_elements')),
    Bucket('doris-codes-specs', 'Codes and Specs', Path('/mnt/ace/doris/codes/_from_elements/codes-doris')),
    Bucket('doris-university', 'Doris University', Path('/mnt/ace/doris/training/_from_elements')),
    Bucket('digitalmodel-qgis', 'qgis', Path('/mnt/ace/digitalmodel/tools/qgis/_from_elements')),
    Bucket('digitalmodel-riser-toolbox', 'Riser Toolbox', Path('/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements')),
    Bucket('digitalmodel-suction-pile-sizing', 'Suction Pile Sizing', Path('/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements')),
    Bucket('acma-projects-31522-woodfibre', 'Woodfibre', Path('/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements')),
]


def scan(root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    if not root.exists():
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        base = Path(dirpath)
        for name in filenames:
            p = base / name
            try:
                rel = p.relative_to(root).as_posix()
                out[rel] = p.stat().st_size
            except OSError:
                out[p.relative_to(root).as_posix()] = -1
    return out


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    details_dir = BASE / 'post-copy-verification'
    details_dir.mkdir(exist_ok=True)

    for b in BUCKETS:
        sroot = SRC / b.source_rel
        droot = b.dest
        src = scan(sroot)
        dst = scan(droot)
        missing = sorted(set(src) - set(dst))
        extra = sorted(set(dst) - set(src))
        size_mismatch = sorted(p for p in set(src) & set(dst) if src[p] != dst[p])
        src_bytes = sum(v for v in src.values() if v >= 0)
        dst_bytes = sum(v for v in dst.values() if v >= 0)
        status = 'PASS' if not missing and not size_mismatch else 'FAIL'
        if not sroot.exists():
            status = 'SOURCE_MISSING'
        elif not droot.exists():
            status = 'DEST_MISSING'
        summary_rows.append((b.tag, b.source_rel, str(droot), status, len(src), src_bytes, len(dst), dst_bytes, len(missing), len(size_mismatch), len(extra)))
        detail = details_dir / f'{b.tag}.tsv'
        with detail.open('w', encoding='utf-8') as f:
            f.write('kind\trelpath\tsource_size\tdest_size\n')
            for p in missing:
                f.write(f'MISSING\t{p}\t{src[p]}\t\n')
            for p in size_mismatch:
                f.write(f'SIZE_MISMATCH\t{p}\t{src[p]}\t{dst[p]}\n')
            for p in extra:
                f.write(f'EXTRA\t{p}\t\t{dst[p]}\n')

    summary_tsv = BASE / 'post-copy-verification-summary.tsv'
    with summary_tsv.open('w', encoding='utf-8') as f:
        f.write('tag\tsource\tdestination\tstatus\tsource_files\tsource_bytes\tdest_files\tdest_bytes\tmissing_files\tsize_mismatches\textra_files\n')
        for row in summary_rows:
            f.write('\t'.join(map(str, row)) + '\n')

    report = BASE / 'post-copy-verification-report.md'
    with report.open('w', encoding='utf-8') as f:
        f.write('# Elements post-copy verification report\n\n')
        f.write(f'- Generated: {datetime.now().isoformat()}\n')
        f.write('- Scope: staged `_from_elements/` copies only; no merge verification.\n')
        f.write('- Source deletion/mutation: not performed by this verifier.\n\n')
        f.write('| Bucket | Status | Source files | Destination files | Missing | Size mismatch | Extra |\n')
        f.write('|---|---:|---:|---:|---:|---:|---:|\n')
        for tag, _src, _dest, status, sf, _sb, df, _db, miss, mm, extra in summary_rows:
            f.write(f'| `{tag}` | {status} | {sf} | {df} | {miss} | {mm} | {extra} |\n')
        f.write('\nDetails are in `post-copy-verification/*.tsv`.\n')

    print(f'Wrote {summary_tsv}')
    print(f'Wrote {report}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
