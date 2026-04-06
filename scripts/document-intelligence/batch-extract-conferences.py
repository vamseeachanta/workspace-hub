#!/usr/bin/env python3
"""Batch conference document extractor — Phase A catalog to Phase B manifests.

Calls extract_document() directly from the extraction pipeline,
producing manifests with full text, tables, and figure refs.

Usage:
    uv run python scripts/document-intelligence/batch-extract-conferences.py --phase 1
    uv run python scripts/document-intelligence/batch-extract-conferences.py --collection "NACE"

Issue: #1954
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root is on PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.data.doc_intelligence.schema import write_manifest
from scripts.data.doc_intelligence.orchestrator import extract_document as _extract

PHASE1_SMALL = ["Dry Tree Forum", "Euroforum Offshore Risers", "Flow Induced Vibration", "NACE", "Subsea Tieback"]
PHASE2_MEDIUM = ["DOT", "UK Conference Folder", "ISOPE"]
PHASE3_LARGE = ["OMAE", "OTC"]
PHASE4_REMAINING = [
    "Arctic Technology Conference", "Coiled Tubing & Well Intervention Conference 2011",
    "DeepGulf", "EUCI", "IADC International Deepwater Drilling",
    "IMarEST Offshore Oil and Gas Conference", "ISO 9001", "JPT",
    "Offshore West Africa", "Pipeline Pigging & Integrity Management Feb 2009",
    "Rio Oil & Gas", "Robert Restore", "SNAME", "SPE", "SUT",
    "Subsea Houston", "Subsea Survey IMMR", "TO SORT", "TOD",
    "Unlocking Deepwarter Potential- Mumbai"
]

SUPPORTED_EXTS = {".pdf", ".docx", ".xlsx", ".html", ".htm"}
UNSUPPORTED_EXTS = {".ppt", ".pptx", ".xls", ".doc", ".txt"}

CONF_ROOT = Path("/mnt/ace/docs/conferences")
LOG_FILE = REPO_ROOT / "data" / "doc-intelligence" / "manifests" / "conferences" / "extraction-log.jsonl"

stats = {"processed": 0, "errors": 0, "skipped": 0, "secs": 0}


def extract_single(filepath: Path, coll_name: str, batch_size: int = 50, total: int = 0) -> str:
    """Extract document using pipeline directly."""
    start = time.time()

    safe_name = filepath.stem.replace("/", "_").replace("\\", "_").replace(".", "_")
    output_file = REPO_ROOT / "data" / "doc-intelligence" / "manifests" / "conferences" / coll_name / f"{safe_name}.manifest.yaml"

    if output_file.exists() and output_file.stat().st_size > 10:
        stats["skipped"] += 1
        return "skipped"

    try:
        manifest = _extract(str(filepath), domain="conference", output=str(output_file), doc_ref=None)
        elapsed = time.time() - start
        stats["processed"] += 1
        stats["secs"] += elapsed
        return "ok"
    except Exception as e:
        elapsed = time.time() - start
        stats["errors"] += 1
        stats["secs"] += elapsed
        if stats["errors"] <= 10:
            stats.setdefault("error_samples", []).append(f"{filepath.name[:50]}: {e}")
        return "error"


def process_collection(coll_name: str, batch_size: int = 50):
    coll_dir = CONF_ROOT / coll_name
    if not coll_dir.is_dir():
        return {"total": 0, "supported": 0, "unsupported": 0, "ok": 0, "error": 0, "skipped": 0}

    all_files = sorted(f for f in coll_dir.rglob("*") if f.is_file())
    total = len(all_files)

    supported_files = [f for f in all_files if f.suffix.lower() in SUPPORTED_EXTS]
    unsupported_count = len(all_files) - len(supported_files)

    results = {"total": total, "supported": len(supported_files), "unsupported": unsupported_count,
               "ok": 0, "error": 0, "skipped": 0}

    for i, fpath in enumerate(supported_files, 1):
        status = extract_single(fpath, coll_name, batch_size, len(supported_files))
        if status == "ok":
            results["ok"] += 1
        elif status == "skipped":
            results["skipped"] += 1
        else:
            results["error"] += 1

        if i % batch_size == 0 or i == len(supported_files):
            log_entry = {
                "collection": coll_name,
                "progress": f"{i}/{len(supported_files)}",
                "results": dict(results),
                "error_samples": stats.get("error_samples", [])[-5:],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            with open(LOG_FILE, "a") as lf:
                lf.write(json.dumps(log_entry) + "\n")

    return results


def main():
    # Parse args manually to avoid argparse swallowing errors
    args = sys.argv[1:]
    phase = None
    collection = None

    i = 0
    while i < len(args):
        if args[i] == "--phase" and i + 1 < len(args):
            phase = int(args[i + 1])
            i += 2
        elif args[i] == "--collection" and i + 1 < len(args):
            collection = args[i + 1]
            i += 2
        else:
            i += 1

    if collection:
        collections = [collection]
    elif phase:
        phase_map = {1: PHASE1_SMALL, 2: PHASE2_MEDIUM, 3: PHASE3_LARGE, 4: PHASE4_REMAINING}
        collections = phase_map[phase]
    else:
        collections = sorted(d.name for d in CONF_ROOT.iterdir() if d.is_dir())

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    grand = {"ok": 0, "error": 0, "skipped": 0, "unsupported": 0, "total": 0}

    for c in collections:
        results = process_collection(c, batch_size=50)

        # Update grand totals
        grand["total"] += results["total"]
        grand["unsupported"] += results["unsupported"]
        grand["ok"] += results["ok"]
        grand["error"] += results["error"]
        grand["skipped"] += results["skipped"]

        # Log summary line
        summary = f"  {c}: supported={results['supported']}/{results['total']} " \
                  f"ok={results['ok']} err={results['error']} skip={results['skipped']} " \
                  f"unsupported={results['unsupported']}"
        with open(LOG_FILE, "a") as lf:
            lf.write(json.dumps({"summary": summary}) + "\n")

    elapsed = time.time() - t0

    if stats.get("error_samples"):
        with open(LOG_FILE, "a") as lf:
            lf.write(json.dumps({"error_samples": stats["error_samples"][-10:]}) + "\n")

    footer = {
        "event": "complete",
        "elapsed_min": round(elapsed / 60, 1),
        "grand": dict(grand),
        "error_samples": stats.get("error_samples", [])[-10:]
    }
    with open(LOG_FILE, "a") as lf:
        lf.write(json.dumps(footer) + "\n")

    return 0
