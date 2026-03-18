#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "docling>=2.80",
#     "transformers>=4.51",
#     "huggingface-hub>=0.25,<1",
# ]
# ///
# NOTE: Run with CUDA_VISIBLE_DEVICES="" to force CPU mode on older GPUs.
# NOTE: Do NOT run from workspace-hub root — queue.py shadows stdlib queue.
"""Benchmark Docling for equation/constant/table extraction from engineering PDFs.

Tests Docling's Granite-Docling-258M VLM against pdftotext and pypdfium2 on
content types currently at 0% yield: equations, constants, procedures.

Usage:
    uv run --no-project --with docling python \
        scripts/data/doc_intelligence/benchmark_docling.py \
        --pdf-dir /mnt/ace/O&G-Standards/DNV --sample 10

    uv run --no-project --with docling python \
        scripts/data/doc_intelligence/benchmark_docling.py \
        --pdf /path/to/specific.pdf
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def find_pdfs(pdf_dir: str, sample_size: int) -> list[Path]:
    """Find PDFs, preferring engineering standards with equations."""
    pdfs = []
    for root, _, files in os.walk(pdf_dir):
        for f in sorted(files):
            if f.lower().endswith(".pdf"):
                p = Path(root) / f
                try:
                    size = p.stat().st_size
                except OSError:
                    continue
                if 10_000 < size < 10_000_000:
                    pdfs.append(p)
                    if len(pdfs) >= sample_size:
                        return pdfs
    return pdfs


def extract_docling(path: Path) -> tuple[str, float, dict]:
    """Extract via Docling. Returns (markdown, seconds, metadata)."""
    from docling.document_converter import DocumentConverter

    t0 = time.perf_counter()
    try:
        converter = DocumentConverter()
        result = converter.convert(str(path))
        md = result.document.export_to_markdown()
        elapsed = time.perf_counter() - t0

        metadata = {
            "num_tables": len(result.document.tables) if hasattr(result.document, "tables") else 0,
            "num_pages": result.document.num_pages() if hasattr(result.document, "num_pages") else -1,
        }
        return md, elapsed, metadata
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return "", elapsed, {"error": str(e)}


def extract_pdftotext(path: Path) -> tuple[str, float]:
    """Extract via pdftotext subprocess."""
    t0 = time.perf_counter()
    try:
        result = subprocess.run(
            ["pdftotext", "-q", str(path), "-"],
            capture_output=True, text=True, timeout=30,
        )
        elapsed = time.perf_counter() - t0
        return result.stdout if result.returncode == 0 else "", elapsed
    except Exception:
        return "", time.perf_counter() - t0


def count_equations(text: str) -> int:
    """Count equation-like patterns in text."""
    patterns = [
        r"\$[^$]+\$",           # LaTeX inline math
        r"\$\$[^$]+\$\$",      # LaTeX display math
        r"\\frac\{",            # LaTeX fractions
        r"\\sqrt\{",            # LaTeX sqrt
        r"\\sum|\\int|\\prod",  # LaTeX operators
        r"[α-ωΑ-Ω]",           # Greek letters (common in equations)
        r"[=<>≤≥≈]\s*\d",      # Equations with numbers
        r"\d+\s*[×·]\s*\d",    # Multiplication
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    return count


def count_constants(text: str) -> int:
    """Count engineering constant references."""
    patterns = [
        r"\b\d+\.?\d*\s*(MPa|kPa|GPa|psi|ksi)",   # pressure
        r"\b\d+\.?\d*\s*(kg/m[³3]|lb/ft[³3])",      # density
        r"\b\d+\.?\d*\s*(m/s|ft/s|km/h|mph)",        # velocity
        r"\b\d+\.?\d*\s*(°[CF]|K\b)",                # temperature
        r"\b\d+\.?\d*\s*(N/m|kN|MN|lbf)",            # force
        r"\b\d+\.?\d*\s*(mm|cm|m|in|ft)\b",          # length
        r"\bE\s*=\s*\d",                              # Young's modulus
        r"\bσ|τ|ε|ν\s*=",                             # stress/strain
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def count_tables(text: str) -> int:
    """Count markdown table patterns."""
    return len(re.findall(r"^\|.*\|$", text, re.MULTILINE))


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Docling extraction")
    parser.add_argument("--pdf-dir", default=None, help="Directory to search for PDFs")
    parser.add_argument("--pdf", default=None, help="Single PDF to test")
    parser.add_argument("--sample", type=int, default=10, help="Number of PDFs (default: 10)")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    if args.pdf:
        pdfs = [Path(args.pdf)]
    elif args.pdf_dir:
        pdfs = find_pdfs(args.pdf_dir, args.sample)
    else:
        print("Error: specify --pdf or --pdf-dir", file=sys.stderr)
        return 1

    if not pdfs:
        print("Error: no PDFs found", file=sys.stderr)
        return 1

    print(f"Benchmarking Docling on {len(pdfs)} PDFs...\n", flush=True)

    results = []
    total_docling_time = 0.0
    total_pdftotext_time = 0.0

    for i, pdf in enumerate(pdfs):
        print(f"  [{i+1}/{len(pdfs)}] {pdf.name}...", end=" ", flush=True)

        # Docling extraction
        md_docling, t_docling, meta = extract_docling(pdf)
        total_docling_time += t_docling

        # pdftotext baseline
        text_pdftotext, t_pdftotext = extract_pdftotext(pdf)
        total_pdftotext_time += t_pdftotext

        # Content analysis
        eq_docling = count_equations(md_docling)
        eq_pdftotext = count_equations(text_pdftotext)
        const_docling = count_constants(md_docling)
        const_pdftotext = count_constants(text_pdftotext)
        tables_docling = count_tables(md_docling)

        result = {
            "file": pdf.name,
            "size_bytes": pdf.stat().st_size,
            "docling_seconds": round(t_docling, 2),
            "pdftotext_seconds": round(t_pdftotext, 4),
            "docling_chars": len(md_docling),
            "pdftotext_chars": len(text_pdftotext),
            "equations_docling": eq_docling,
            "equations_pdftotext": eq_pdftotext,
            "constants_docling": const_docling,
            "constants_pdftotext": const_pdftotext,
            "table_rows_docling": tables_docling,
            "docling_metadata": meta,
        }
        results.append(result)

        status = "error" if meta.get("error") else "ok"
        print(
            f"{status} | docling: {t_docling:.1f}s "
            f"eq:{eq_docling} const:{const_docling} tbl:{tables_docling} | "
            f"pdftotext: {t_pdftotext:.2f}s eq:{eq_pdftotext} const:{const_pdftotext}",
            flush=True,
        )

    # Summary
    total_eq_docling = sum(r["equations_docling"] for r in results)
    total_eq_pdftotext = sum(r["equations_pdftotext"] for r in results)
    total_const_docling = sum(r["constants_docling"] for r in results)
    total_const_pdftotext = sum(r["constants_pdftotext"] for r in results)
    total_tbl_docling = sum(r["table_rows_docling"] for r in results)
    errors = sum(1 for r in results if r["docling_metadata"].get("error"))

    summary = {
        "total_files": len(pdfs),
        "errors": errors,
        "total_docling_seconds": round(total_docling_time, 1),
        "total_pdftotext_seconds": round(total_pdftotext_time, 2),
        "avg_docling_seconds": round(total_docling_time / len(pdfs), 2),
        "equations_docling": total_eq_docling,
        "equations_pdftotext": total_eq_pdftotext,
        "equation_yield_improvement": (
            f"{total_eq_docling / total_eq_pdftotext:.1f}x"
            if total_eq_pdftotext > 0 else
            f"{total_eq_docling} vs 0"
        ),
        "constants_docling": total_const_docling,
        "constants_pdftotext": total_const_pdftotext,
        "table_rows_docling": total_tbl_docling,
    }

    print(f"\n{'='*60}")
    print(f"DOCLING BENCHMARK RESULTS ({len(pdfs)} PDFs)")
    print(f"{'='*60}")
    print(f"Total time:  Docling {total_docling_time:.1f}s  |  pdftotext {total_pdftotext_time:.2f}s")
    print(f"Avg/doc:     Docling {total_docling_time/len(pdfs):.1f}s  |  pdftotext {total_pdftotext_time/len(pdfs):.2f}s")
    print(f"Errors:      {errors}/{len(pdfs)}")
    print(f"\nContent Extraction Comparison:")
    print(f"  Equations:  Docling {total_eq_docling}  vs  pdftotext {total_eq_pdftotext}")
    print(f"  Constants:  Docling {total_const_docling}  vs  pdftotext {total_const_pdftotext}")
    print(f"  Table rows: Docling {total_tbl_docling}  (markdown)")

    output = {"summary": summary, "results": results}
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
