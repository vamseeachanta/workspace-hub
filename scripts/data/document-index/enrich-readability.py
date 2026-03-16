#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pdfplumber",
# ]
# ///
"""Enrich document index with PDF readability classification.

Reads index.jsonl, classifies each PDF as machine-readable / ocr-needed / mixed,
and writes an enriched index with the 'readability' field added.

Non-PDF documents get readability='native' (inherently machine-readable).

Usage:
    # Dry run — report stats without modifying index
    uv run --no-project python scripts/data/document-index/enrich-readability.py --dry-run

    # Full enrichment with 10 parallel workers
    uv run --no-project python scripts/data/document-index/enrich-readability.py --workers 10

    # Resume from a partial run (skips already-classified docs)
    uv run --no-project python scripts/data/document-index/enrich-readability.py --resume --workers 10
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def classify_pdf_readability(path: str, max_pages: int = 5) -> str:
    """Classify PDF readability by sampling page text density.

    Returns: "machine" | "ocr-needed" | "mixed" | "empty" | "error" | "missing"
    """
    if not os.path.exists(path):
        return "missing"

    import pdfplumber

    try:
        with pdfplumber.open(path) as pdf:
            total = len(pdf.pages)
            if total == 0:
                return "empty"

            if total <= max_pages:
                indices = list(range(total))
            else:
                step = total / max_pages
                indices = [int(i * step) for i in range(max_pages)]

            pages_with_text = 0
            for idx in indices:
                text = (pdf.pages[idx].extract_text() or "").strip()
                if len(text) >= 50:
                    pages_with_text += 1

            ratio = pages_with_text / len(indices)
            if ratio >= 0.8:
                return "machine"
            elif ratio >= 0.2:
                return "mixed"
            else:
                return "ocr-needed"

    except Exception:
        return "error"


def _classify_record(rec: dict) -> dict:
    """Worker function: classify one record and return it enriched."""
    ext = rec.get("ext", "")
    if ext != "pdf":
        rec["readability"] = "native"
        return rec

    path = rec["path"]
    size_mb = rec.get("size_mb", 0)

    if size_mb > 50:
        rec["readability"] = "skipped-large"
    else:
        rec["readability"] = classify_pdf_readability(path)

    return rec


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich document index with readability classification"
    )
    parser.add_argument(
        "--index",
        default="data/document-index/index.jsonl",
        help="Path to document index JSONL",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: overwrite input)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report stats only")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip docs that already have readability field",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        help="Records per worker batch (default: 200)",
    )
    args = parser.parse_args()

    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else index_path
    tmp_path = output_path.with_suffix(".jsonl.tmp")

    # Count PDFs first for dry-run
    if args.dry_run:
        stats = {"pdf": 0, "non_pdf": 0, "total": 0, "already_classified": 0}
        with open(index_path) as f:
            for line in f:
                rec = json.loads(line.strip())
                stats["total"] += 1
                if rec.get("ext") == "pdf":
                    stats["pdf"] += 1
                else:
                    stats["non_pdf"] += 1
                if "readability" in rec:
                    stats["already_classified"] += 1

        need = stats["pdf"] - stats["already_classified"]
        print(f"Index: {stats['total']:,} records")
        print(f"  PDFs: {stats['pdf']:,}")
        print(f"  Non-PDF: {stats['non_pdf']:,} (will be 'native')")
        print(f"  Already classified: {stats['already_classified']:,}")
        print(f"  Need classification: {need:,}")
        est_hours = need / (args.workers * 3600)
        print(f"  Estimated time ({args.workers} workers): {est_hours:.1f} hours")
        return 0

    # Phase 1: Read all records, separate into needs-work vs already-done
    print(f"Loading index from {index_path}...", flush=True)
    all_records = []
    need_classify = []  # (index, record) tuples
    skipped = 0

    with open(index_path) as f:
        for i, line in enumerate(f):
            rec = json.loads(line.strip())
            all_records.append(rec)
            if args.resume and "readability" in rec:
                skipped += 1
            else:
                need_classify.append((i, rec))

    total = len(all_records)
    print(
        f"  Total: {total:,} | Need classification: {len(need_classify):,} | "
        f"Already done: {skipped:,}",
        flush=True,
    )

    if not need_classify:
        print("Nothing to classify — all records already have readability field.")
        return 0

    # Phase 2: Parallel classification
    t0 = time.time()
    classified = 0
    readability_stats = {}

    # Count already-classified stats
    for rec in all_records:
        if "readability" in rec:
            rd = rec["readability"]
            readability_stats[rd] = readability_stats.get(rd, 0) + 1

    print(f"Classifying {len(need_classify):,} records with {args.workers} workers...", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        # Submit in chunks to maintain order
        futures = {}
        for idx, rec in need_classify:
            fut = pool.submit(_classify_record, rec)
            futures[fut] = idx

        for fut in as_completed(futures):
            idx = futures[fut]
            try:
                result = fut.result(timeout=30)
                all_records[idx] = result
                rd = result.get("readability", "error")
            except Exception:
                all_records[idx]["readability"] = "error"
                rd = "error"

            readability_stats[rd] = readability_stats.get(rd, 0) + 1
            classified += 1

            if classified % 1000 == 0:
                elapsed = time.time() - t0
                rate = classified / elapsed if elapsed > 0 else 0
                pct = classified / len(need_classify) * 100
                print(
                    f"  [{classified:,}/{len(need_classify):,}] {pct:.1f}% "
                    f"{elapsed:.0f}s ({rate:.0f}/s)",
                    flush=True,
                )

    # Phase 3: Write output
    print("Writing enriched index...", flush=True)
    with open(tmp_path, "w") as fout:
        for rec in all_records:
            fout.write(json.dumps(rec, separators=(",", ":")) + "\n")

    if output_path == index_path:
        backup = index_path.with_suffix(".jsonl.bak")
        if backup.exists():
            backup.unlink()
        os.rename(index_path, backup)
        os.rename(tmp_path, index_path)
        print(f"Backup: {backup}")
    else:
        os.rename(tmp_path, output_path)

    elapsed = time.time() - t0
    print(f"\nEnrichment complete in {elapsed:.0f}s ({elapsed/3600:.1f}h)")
    print(f"  Processed: {total:,}")
    print(f"  Classified: {classified:,}")
    print(f"  Skipped (resume): {skipped:,}")
    print(f"  Workers: {args.workers}")
    print(f"\nReadability breakdown:")
    for rd, cnt in sorted(readability_stats.items(), key=lambda x: -x[1]):
        print(f"  {rd}: {cnt:,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
