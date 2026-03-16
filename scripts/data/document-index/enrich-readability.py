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

    # Full enrichment (writes enriched index)
    uv run --no-project python scripts/data/document-index/enrich-readability.py

    # Resume from a partial run (skips already-classified docs)
    uv run --no-project python scripts/data/document-index/enrich-readability.py --resume
"""

import argparse
import json
import os
import signal
import sys
import time
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
        "--batch-size",
        type=int,
        default=10000,
        help="Write checkpoint every N records",
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

        need_classification = stats["pdf"] - stats["already_classified"]
        print(f"Index: {stats['total']:,} records")
        print(f"  PDFs: {stats['pdf']:,}")
        print(f"  Non-PDF: {stats['non_pdf']:,} (will be 'native')")
        print(f"  Already classified: {stats['already_classified']:,}")
        print(f"  Need classification: {need_classification:,}")
        # Estimate time: ~1s per PDF (conservative)
        est_hours = need_classification / 3600
        print(f"  Estimated time: {est_hours:.1f} hours")
        return 0

    # Enrichment pass
    def _timeout_handler(signum, frame):
        raise TimeoutError()

    t0 = time.time()
    processed = 0
    classified = 0
    skipped = 0
    readability_stats = {}

    with open(index_path) as fin, open(tmp_path, "w") as fout:
        for line in fin:
            rec = json.loads(line.strip())
            processed += 1

            # Skip if already classified and resuming
            if args.resume and "readability" in rec:
                skipped += 1
                fout.write(json.dumps(rec, separators=(",", ":")) + "\n")
                rd = rec["readability"]
                readability_stats[rd] = readability_stats.get(rd, 0) + 1
                continue

            ext = rec.get("ext", "")
            if ext != "pdf":
                rec["readability"] = "native"
            else:
                path = rec["path"]
                size_mb = rec.get("size_mb", 0)

                if size_mb > 50:
                    rec["readability"] = "skipped-large"
                else:
                    # Timeout protection per file
                    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.alarm(15)
                    try:
                        rec["readability"] = classify_pdf_readability(path)
                    except TimeoutError:
                        rec["readability"] = "timeout"
                    finally:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)

                classified += 1

            rd = rec["readability"]
            readability_stats[rd] = readability_stats.get(rd, 0) + 1

            fout.write(json.dumps(rec, separators=(",", ":")) + "\n")

            if processed % 5000 == 0:
                elapsed = time.time() - t0
                rate = processed / elapsed if elapsed > 0 else 0
                print(
                    f"  [{processed:,}] {elapsed:.0f}s ({rate:.0f}/s) "
                    f"classified={classified} skipped={skipped}",
                    flush=True,
                )

    # Replace original with enriched version
    if output_path == index_path:
        backup = index_path.with_suffix(".jsonl.bak")
        os.rename(index_path, backup)
        os.rename(tmp_path, index_path)
        print(f"Backup: {backup}")
    else:
        os.rename(tmp_path, output_path)

    elapsed = time.time() - t0
    print(f"\nEnrichment complete in {elapsed:.0f}s")
    print(f"  Processed: {processed:,}")
    print(f"  Classified: {classified:,}")
    print(f"  Skipped (resume): {skipped:,}")
    print(f"\nReadability breakdown:")
    for rd, cnt in sorted(readability_stats.items(), key=lambda x: -x[1]):
        print(f"  {rd}: {cnt:,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
