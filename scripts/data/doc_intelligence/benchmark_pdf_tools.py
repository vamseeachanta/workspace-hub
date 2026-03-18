#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdfium2",
# ]
# ///
"""Benchmark pypdfium2 vs pdftotext for PDF text extraction.

Compares speed, output quality, and readability classification accuracy
on a sample of PDFs from the document corpus.

Usage:
    uv run --no-project python scripts/data/doc_intelligence/benchmark_pdf_tools.py
    uv run --no-project python scripts/data/doc_intelligence/benchmark_pdf_tools.py \
        --sample 100 --output results.json --pdf-dir /mnt/ace/worldenergydata/docs
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def find_pdfs(pdf_dir: str, sample_size: int) -> list[Path]:
    """Recursively find PDFs under pdf_dir, return up to sample_size."""
    pdfs = []
    for root, _, files in os.walk(pdf_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                p = Path(root) / f
                size = p.stat().st_size
                if 1024 < size < 5_000_000:  # 1KB-5MB
                    pdfs.append(p)
                    if len(pdfs) >= sample_size:
                        return pdfs
    return pdfs


def extract_pdftotext(path: Path, first_n_pages: int = 0) -> tuple[str, float]:
    """Extract text via pdftotext subprocess. Returns (text, seconds)."""
    cmd = ["pdftotext", "-q"]
    if first_n_pages > 0:
        cmd.extend(["-f", "1", "-l", str(first_n_pages)])
    cmd.extend([str(path), "-"])

    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        elapsed = time.perf_counter() - t0
        return result.stdout if result.returncode == 0 else "", elapsed
    except (subprocess.TimeoutExpired, Exception):
        return "", time.perf_counter() - t0


def extract_pypdfium2(path: Path, first_n_pages: int = 0) -> tuple[str, float]:
    """Extract text via pypdfium2 in-process. Returns (text, seconds)."""
    import pypdfium2 as pdfium

    t0 = time.perf_counter()
    try:
        doc = pdfium.PdfDocument(str(path))
        n = len(doc)
        if first_n_pages > 0:
            n = min(n, first_n_pages)
        texts = []
        for i in range(n):
            tp = doc[i].get_textpage()
            texts.append(tp.get_text_range())
        doc.close()
        elapsed = time.perf_counter() - t0
        return "\n".join(texts), elapsed
    except Exception:
        return "", time.perf_counter() - t0


def classify_readability_pypdfium2(path: Path, max_pages: int = 5) -> str:
    """Classify PDF readability using pypdfium2 (pdfplumber replacement).

    Returns: "machine" | "ocr-needed" | "mixed" | "empty" | "error"
    """
    import pypdfium2 as pdfium

    try:
        doc = pdfium.PdfDocument(str(path))
        total = len(doc)
        if total == 0:
            doc.close()
            return "empty"

        if total <= max_pages:
            indices = list(range(total))
        else:
            step = total / max_pages
            indices = [int(i * step) for i in range(max_pages)]

        pages_with_text = 0
        for idx in indices:
            tp = doc[idx].get_textpage()
            text = tp.get_text_range().strip()
            if len(text) >= 50:
                pages_with_text += 1

        doc.close()
        ratio = pages_with_text / len(indices)
        if ratio >= 0.8:
            return "machine"
        elif ratio >= 0.2:
            return "mixed"
        else:
            return "ocr-needed"
    except Exception:
        return "error"


def text_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity between two text extractions."""
    if not a or not b:
        return 0.0
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark PDF extraction tools")
    parser.add_argument(
        "--pdf-dir",
        default="/mnt/ace/worldenergydata/docs",
        help="Directory to search for PDFs",
    )
    parser.add_argument(
        "--sample", type=int, default=100,
        help="Number of PDFs to benchmark (default: 100)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Output JSON file path (default: stdout summary)",
    )
    args = parser.parse_args()

    print(f"Finding PDFs in {args.pdf_dir}...", flush=True)
    pdfs = find_pdfs(args.pdf_dir, args.sample)
    if not pdfs:
        print(f"Error: no PDFs found in {args.pdf_dir}", file=sys.stderr)
        return 1

    print(f"Benchmarking {len(pdfs)} PDFs...\n", flush=True)

    results = []
    total_pdftotext = 0.0
    total_pypdfium2 = 0.0
    readability_counts = {}

    for i, pdf in enumerate(pdfs):
        # Full extraction benchmark
        text_pdftotext, t_pdftotext = extract_pdftotext(pdf)
        text_pypdfium2, t_pypdfium2 = extract_pypdfium2(pdf)

        # Readability classification
        readability = classify_readability_pypdfium2(pdf)
        readability_counts[readability] = readability_counts.get(readability, 0) + 1

        # Quality comparison
        similarity = text_similarity(text_pdftotext, text_pypdfium2)

        total_pdftotext += t_pdftotext
        total_pypdfium2 += t_pypdfium2

        result = {
            "file": str(pdf.name),
            "size_bytes": pdf.stat().st_size,
            "pdftotext_seconds": round(t_pdftotext, 6),
            "pypdfium2_seconds": round(t_pypdfium2, 6),
            "speedup": round(t_pdftotext / t_pypdfium2, 2) if t_pypdfium2 > 0 else 0,
            "pdftotext_chars": len(text_pdftotext),
            "pypdfium2_chars": len(text_pypdfium2),
            "word_overlap_similarity": round(similarity, 3),
            "readability_pypdfium2": readability,
        }
        results.append(result)

        if (i + 1) % 20 == 0:
            print(
                f"  [{i+1}/{len(pdfs)}] "
                f"pdftotext: {total_pdftotext:.2f}s "
                f"pypdfium2: {total_pypdfium2:.2f}s "
                f"(speedup: {total_pdftotext/total_pypdfium2:.1f}x)",
                flush=True,
            )

    # Summary
    avg_speedup = (
        total_pdftotext / total_pypdfium2 if total_pypdfium2 > 0 else 0
    )
    similarities = [r["word_overlap_similarity"] for r in results]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0

    summary = {
        "total_files": len(pdfs),
        "total_pdftotext_seconds": round(total_pdftotext, 3),
        "total_pypdfium2_seconds": round(total_pypdfium2, 3),
        "avg_speedup_factor": round(avg_speedup, 2),
        "avg_word_overlap_similarity": round(avg_similarity, 3),
        "readability_distribution": readability_counts,
    }

    output = {"summary": summary, "results": results}

    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS ({len(pdfs)} PDFs)")
    print(f"{'='*60}")
    print(f"Total pdftotext:  {total_pdftotext:.3f}s")
    print(f"Total pypdfium2:  {total_pypdfium2:.3f}s")
    print(f"Average speedup:  {avg_speedup:.1f}x")
    print(f"Avg word overlap: {avg_similarity:.3f}")
    print(f"\nReadability (pypdfium2):")
    for cat, cnt in sorted(readability_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
