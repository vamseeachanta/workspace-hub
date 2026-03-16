#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml",
#     "pdfplumber",
#     "python-docx",
#     "openpyxl",
# ]
# ///
"""Assess deep extraction yield across the text-extractable corpus.

Stratified random sample → manifest extraction → yield metrics → YAML report.
Designed for WRK-1246: measures table/chart/equation density by source × extension.

Usage:
    uv run --no-project python scripts/data/document-index/assess-deep-extraction-yield.py \
        --sample-size 100 --output data/doc-intelligence/yield-assessment.yaml

    # Filter to one stratum
    uv run --no-project python scripts/data/document-index/assess-deep-extraction-yield.py \
        --source ace_standards --ext pdf --sample-size 50
"""

import argparse
import json
import os
import random
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.orchestrator import extract_document
from scripts.data.doc_intelligence.schema import manifest_to_dict

# Default strata: source × extension groups
DEFAULT_STRATA = {
    "ace_standards_pdf": {"source": "ace_standards", "exts": ["pdf"]},
    "ace_standards_pdf_gt1mb": {
        "source": "ace_standards",
        "exts": ["pdf"],
        "min_size_mb": 1.0,
    },
    "og_standards_pdf": {"source": "og_standards", "exts": ["pdf"]},
    "ace_project_pdf": {"source": "ace_project", "exts": ["pdf"]},
    "ace_project_xls": {"source": "ace_project", "exts": ["xlsx", "xls"]},
    "dde_project_pdf": {"source": "dde_project", "exts": ["pdf"]},
    "dde_project_doc": {"source": "dde_project", "exts": ["docx", "doc"]},
}

INDEX_PATH = Path("data/document-index/index.jsonl")


def load_stratum_docs(
    index_path: Path,
    source_filter: str | None,
    ext_filter: str | None,
) -> dict[str, list[dict]]:
    """Load docs from index grouped by stratum."""
    if source_filter and ext_filter:
        strata = {
            f"{source_filter}_{ext_filter}": {
                "source": source_filter,
                "exts": [ext_filter],
            }
        }
    elif source_filter:
        strata = {
            k: v for k, v in DEFAULT_STRATA.items() if v["source"] == source_filter
        }
    else:
        strata = DEFAULT_STRATA

    buckets: dict[str, list[dict]] = {k: [] for k in strata}

    with open(index_path) as f:
        for line in f:
            rec = json.loads(line.strip())
            src = rec.get("source", "")
            ext = rec.get("ext", "")
            size_mb = rec.get("size_mb", 0)
            for name, spec in strata.items():
                if src == spec["source"] and ext in spec["exts"]:
                    min_sz = spec.get("min_size_mb", 0)
                    if size_mb >= min_sz:
                        buckets[name].append(rec)

    return buckets


def sample_stratum(docs: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Random sample of n docs from a stratum."""
    rng = random.Random(seed)
    if len(docs) <= n:
        return docs
    return rng.sample(docs, n)


def classify_pdf_readability(path: str) -> dict:
    """Classify a PDF as machine-readable, ocr-needed, or mixed.

    Samples up to 5 pages. A page with >=50 chars of extracted text is
    considered machine-readable; otherwise it's scanned/image-only.

    Returns:
        {readability: "machine"|"ocr-needed"|"mixed"|"empty",
         pages_total, pages_sampled, pages_with_text, chars_per_page_avg}
    """
    import pdfplumber

    try:
        with pdfplumber.open(path) as pdf:
            pages_total = len(pdf.pages)
            if pages_total == 0:
                return {
                    "readability": "empty",
                    "pages_total": 0,
                    "pages_sampled": 0,
                    "pages_with_text": 0,
                    "chars_per_page_avg": 0,
                }

            # Sample up to 5 evenly-spaced pages
            max_sample = min(5, pages_total)
            if pages_total <= 5:
                indices = list(range(pages_total))
            else:
                step = pages_total / max_sample
                indices = [int(i * step) for i in range(max_sample)]

            text_lengths = []
            for idx in indices:
                page = pdf.pages[idx]
                text = (page.extract_text() or "").strip()
                text_lengths.append(len(text))

            pages_with_text = sum(1 for t in text_lengths if t >= 50)
            avg_chars = sum(text_lengths) / len(text_lengths) if text_lengths else 0

            if pages_with_text == len(indices):
                readability = "machine"
            elif pages_with_text == 0:
                readability = "ocr-needed"
            else:
                readability = "mixed"

            return {
                "readability": readability,
                "pages_total": pages_total,
                "pages_sampled": len(indices),
                "pages_with_text": pages_with_text,
                "chars_per_page_avg": round(avg_chars, 0),
            }
    except Exception as e:
        return {
            "readability": "error",
            "pages_total": 0,
            "pages_sampled": 0,
            "pages_with_text": 0,
            "chars_per_page_avg": 0,
            "error": str(e)[:200],
        }


def extract_counts(doc: dict) -> dict:
    """Extract manifest counts and readability from a single document.

    Returns dict with counts, readability classification, or error info.
    """
    path = doc["path"]
    ext = doc.get("ext", "")
    size_mb = doc.get("size_mb", 0)

    result = {
        "path": path,
        "source": doc.get("source", ""),
        "ext": ext,
        "size_mb": size_mb,
        "status": "ok",
        "readability": "n/a",
        "pages_total": 0,
        "pages_with_text": 0,
        "chars_per_page_avg": 0,
        "tables": 0,
        "figure_refs": 0,
        "equations": 0,
        "constants": 0,
        "procedures": 0,
        "sections": 0,
        "worked_examples": 0,
        "definitions": 0,
        "requirements": 0,
        "error": None,
    }

    if not os.path.exists(path):
        result["status"] = "missing"
        result["error"] = "file not found"
        return result

    # Skip large files to avoid memory/time issues
    if size_mb > 20:
        result["status"] = "skipped"
        result["error"] = f"too large: {size_mb:.1f} MB"
        return result

    def _timeout_handler(signum, frame):
        raise TimeoutError("extraction exceeded 30s")

    # Phase 1: Readability classification (PDFs only)
    if ext == "pdf":
        rd = classify_pdf_readability(path)
        result["readability"] = rd["readability"]
        result["pages_total"] = rd["pages_total"]
        result["pages_with_text"] = rd.get("pages_with_text", 0)
        result["chars_per_page_avg"] = rd.get("chars_per_page_avg", 0)
    else:
        # Non-PDF text formats are inherently machine-readable
        result["readability"] = "machine"

    # Phase 2: Manifest extraction (only for machine/mixed — skip pure OCR)
    if result["readability"] == "ocr-needed":
        result["status"] = "ocr-needed"
        return result

    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(30)  # 30s per doc
        manifest = extract_document(path, domain="assessment")
        md = manifest_to_dict(manifest)
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

        # Read counts from manifest stats or count sections directly
        stats = md.get("extraction_stats", {})
        result["tables"] = stats.get("tables", len(md.get("tables", [])))
        result["figure_refs"] = stats.get(
            "figure_refs", len(md.get("figure_refs", []))
        )
        result["sections"] = stats.get("sections", len(md.get("sections", [])))
        result["equations"] = len(md.get("equations", []))
        result["constants"] = len(md.get("constants", []))
        result["procedures"] = len(md.get("procedures", []))
        result["worked_examples"] = len(md.get("worked_examples", []))
        result["definitions"] = len(md.get("definitions", []))
        result["requirements"] = len(md.get("requirements", []))

    except TimeoutError:
        signal.alarm(0)
        result["status"] = "timeout"
        result["error"] = "extraction exceeded 30s"
    except Exception as e:
        signal.alarm(0)
        result["status"] = "error"
        result["error"] = str(e)[:200]

    return result


def compute_yield_metrics(results: list[dict]) -> dict:
    """Compute yield metrics from extraction results."""
    total = len(results)
    ok = [r for r in results if r["status"] == "ok"]
    ok_count = len(ok)

    # Readability breakdown (all docs, not just ok)
    readability_counts = {}
    for r in results:
        rd = r.get("readability", "n/a")
        readability_counts[rd] = readability_counts.get(rd, 0) + 1

    if ok_count == 0:
        return {
            "total_sampled": total,
            "extracted_ok": 0,
            "error_rate": 1.0,
            "readability": readability_counts,
            "yield": {},
        }

    # Yield percentages
    has_tables = sum(1 for r in ok if r["tables"] > 0)
    has_many_tables = sum(1 for r in ok if r["tables"] >= 5)
    has_figures = sum(1 for r in ok if r["figure_refs"] > 0)
    has_equations = sum(1 for r in ok if r["equations"] > 0)
    has_constants = sum(1 for r in ok if r["constants"] > 0)
    has_procedures = sum(1 for r in ok if r["procedures"] > 0)
    has_worked_ex = sum(1 for r in ok if r["worked_examples"] > 0)

    # Totals
    total_tables = sum(r["tables"] for r in ok)
    total_figures = sum(r["figure_refs"] for r in ok)
    total_equations = sum(r["equations"] for r in ok)

    # Size correlation with tables
    sizes = [r["size_mb"] for r in ok]
    tables = [r["tables"] for r in ok]
    corr = _pearson(sizes, tables)

    # Readability breakdown (all results, not just ok)
    readability_counts = {}
    for r in results:
        rd = r.get("readability", "n/a")
        readability_counts[rd] = readability_counts.get(rd, 0) + 1

    return {
        "total_sampled": total,
        "extracted_ok": ok_count,
        "missing": sum(1 for r in results if r["status"] == "missing"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "ocr_needed": sum(1 for r in results if r["status"] == "ocr-needed"),
        "timeouts": sum(1 for r in results if r["status"] == "timeout"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "readability": readability_counts,
        "ocr_needed": sum(1 for r in results if r["status"] == "ocr-needed"),
        "readability": readability_counts,
        "yield": {
            "pct_with_tables": round(has_tables / ok_count * 100, 1),
            "pct_with_5plus_tables": round(has_many_tables / ok_count * 100, 1),
            "pct_with_figures": round(has_figures / ok_count * 100, 1),
            "pct_with_equations": round(has_equations / ok_count * 100, 1),
            "pct_with_constants": round(has_constants / ok_count * 100, 1),
            "pct_with_procedures": round(has_procedures / ok_count * 100, 1),
            "pct_with_worked_examples": round(has_worked_ex / ok_count * 100, 1),
        },
        "totals": {
            "tables": total_tables,
            "figure_refs": total_figures,
            "equations": total_equations,
            "mean_tables_per_doc": round(total_tables / ok_count, 2),
            "mean_figures_per_doc": round(total_figures / ok_count, 2),
            "mean_equations_per_doc": round(total_equations / ok_count, 2),
        },
        "size_table_correlation": round(corr, 3) if corr is not None else None,
    }


def _pearson(x: list[float], y: list[float]) -> float | None:
    """Simple Pearson correlation without numpy."""
    n = len(x)
    if n < 3:
        return None
    mx = sum(x) / n
    my = sum(y) / n
    sx = sum((xi - mx) ** 2 for xi in x)
    sy = sum((yi - my) ** 2 for yi in y)
    if sx == 0 or sy == 0:
        return None
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    return sxy / (sx**0.5 * sy**0.5)


def extrapolate(
    metrics_by_stratum: dict[str, dict],
    population_by_stratum: dict[str, int],
) -> dict:
    """Extrapolate sample yield to full corpus."""
    total_estimated_tables = 0
    total_estimated_figures = 0
    total_estimated_equations = 0
    segments = []

    for name, metrics in metrics_by_stratum.items():
        pop = population_by_stratum.get(name, 0)
        y = metrics.get("yield", {})
        t = metrics.get("totals", {})

        est_tables = int(t.get("mean_tables_per_doc", 0) * pop)
        est_figures = int(t.get("mean_figures_per_doc", 0) * pop)
        est_equations = int(t.get("mean_equations_per_doc", 0) * pop)

        total_estimated_tables += est_tables
        total_estimated_figures += est_figures
        total_estimated_equations += est_equations

        rd = metrics.get("readability", {})
        total_sampled = metrics.get("total_sampled", 1)
        ocr_pct = round(rd.get("ocr-needed", 0) / total_sampled * 100, 1)
        mixed_pct = round(rd.get("mixed", 0) / total_sampled * 100, 1)

        segments.append(
            {
                "stratum": name,
                "population": pop,
                "pct_with_tables": y.get("pct_with_tables", 0),
                "estimated_tables": est_tables,
                "estimated_figures": est_figures,
                "high_yield": y.get("pct_with_tables", 0) > 50,
                "pct_ocr_needed": ocr_pct,
                "pct_mixed": mixed_pct,
                "estimated_ocr_docs": int(pop * ocr_pct / 100),
            }
        )

    # Sort by estimated tables descending
    segments.sort(key=lambda s: s["estimated_tables"], reverse=True)

    total_ocr_docs = sum(s["estimated_ocr_docs"] for s in segments)

    return {
        "total_estimated_tables": total_estimated_tables,
        "total_estimated_figures": total_estimated_figures,
        "total_estimated_equations": total_estimated_equations,
        "high_yield_segments": [s["stratum"] for s in segments if s["high_yield"]],
        "phase2_ocr": {
            "total_ocr_docs": total_ocr_docs,
            "description": "Documents requiring OCR before text extraction — "
            "scanned PDFs with no embedded text layer",
            "recommended_tools": ["tesseract", "doctr", "azure-doc-intelligence"],
        },
        "segments": segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assess deep extraction yield across text-extractable corpus"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Docs per stratum (default: 100)",
    )
    parser.add_argument("--source", help="Filter to one source (e.g., ace_standards)")
    parser.add_argument("--ext", help="Filter to one extension (e.g., pdf)")
    parser.add_argument(
        "--output",
        default="data/doc-intelligence/yield-assessment.yaml",
        help="Output YAML report path",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--index",
        default=str(INDEX_PATH),
        help="Path to document index JSONL",
    )
    args = parser.parse_args()

    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: index not found: {index_path}", file=sys.stderr)
        return 1

    print(f"Loading index from {index_path}...")
    buckets = load_stratum_docs(index_path, args.source, args.ext)

    population = {name: len(docs) for name, docs in buckets.items()}
    print("Population per stratum:")
    for name, count in population.items():
        print(f"  {name}: {count:,}")

    # Sample
    all_results: dict[str, list[dict]] = {}
    metrics_by_stratum: dict[str, dict] = {}
    t0 = time.time()

    for name, docs in buckets.items():
        sample = sample_stratum(docs, args.sample_size, seed=args.seed)
        print(f"\n--- {name}: sampling {len(sample)} of {len(docs):,} ---")

        results = []
        for i, doc in enumerate(sample):
            if args.verbose or (i + 1) % 10 == 0:
                elapsed = time.time() - t0
                print(
                    f"  [{i+1}/{len(sample)}] {elapsed:.0f}s "
                    f"{Path(doc['path']).name[:60]}",
                    flush=True,
                )
            r = extract_counts(doc)
            results.append(r)

        all_results[name] = results
        metrics = compute_yield_metrics(results)
        metrics_by_stratum[name] = metrics

        y = metrics.get("yield", {})
        rd = metrics.get("readability", {})
        ocr_n = metrics.get("ocr_needed", 0)
        print(
            f"  → {metrics['extracted_ok']}/{metrics['total_sampled']} ok | "
            f"ocr-needed: {ocr_n} | "
            f"tables: {y.get('pct_with_tables', 0)}% | "
            f"figures: {y.get('pct_with_figures', 0)}% | "
            f"readability: {rd}",
            flush=True,
        )

    elapsed_total = time.time() - t0

    # Extrapolate
    extrapolation = extrapolate(metrics_by_stratum, population)

    # Build report
    report = {
        "assessment": {
            "title": "Deep Extraction Yield Assessment",
            "wrk_id": "WRK-1246",
            "parent": "WRK-1245",
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sample_size_per_stratum": args.sample_size,
            "seed": args.seed,
            "total_docs_sampled": sum(
                m["total_sampled"] for m in metrics_by_stratum.values()
            ),
            "total_extracted_ok": sum(
                m["extracted_ok"] for m in metrics_by_stratum.values()
            ),
            "elapsed_seconds": round(elapsed_total, 1),
        },
        "population": population,
        "strata": metrics_by_stratum,
        "extrapolation": extrapolation,
    }

    # Write report
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    print(f"\n{'='*60}")
    print(f"Assessment complete in {elapsed_total:.0f}s")
    print(f"Report: {out_path}")
    print(f"\nExtrapolation (full corpus):")
    print(f"  Estimated tables:    {extrapolation['total_estimated_tables']:,}")
    print(f"  Estimated figures:   {extrapolation['total_estimated_figures']:,}")
    print(f"  Estimated equations: {extrapolation['total_estimated_equations']:,}")
    print(f"  High-yield segments: {extrapolation['high_yield_segments']}")

    print(f"\nReadability by stratum:")
    for seg in extrapolation.get("segments", []):
        ocr_pct = seg.get("pct_ocr_needed", 0)
        mixed_pct = seg.get("pct_mixed", 0)
        machine_pct = 100 - ocr_pct - mixed_pct
        print(
            f"  {seg['stratum']}: "
            f"machine={machine_pct:.0f}% ocr={ocr_pct:.0f}% mixed={mixed_pct:.0f}% "
            f"(~{seg['estimated_ocr_docs']:,} OCR docs)"
        )
    ocr = extrapolation.get("phase2_ocr", {})
    print(f"\nPhase 2 — OCR pipeline:")
    print(f"  Estimated OCR docs:  {ocr.get('total_ocr_docs', 0):,}")
    print(f"  These need OCR before text extraction can yield tables/charts")

    return 0


if __name__ == "__main__":
    sys.exit(main())
