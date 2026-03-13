#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Batch document extraction runner with queue management.

Usage:
    python batch-extract.py --queue <queue.yaml> [--batch-size N]
        [--rate-limit S] [--resume] [--dry-run] [--verbose]
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parents[3])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.queue import (
    get_pending,
    get_stats,
    load_queue,
    mark_completed,
    mark_failed,
    save_queue,
)

EXTRACT_SCRIPT = str(
    Path(__file__).resolve().parent / "extract-document.py"
)


def _extract_one(doc: dict, output_dir: str, verbose: bool) -> tuple[bool, str]:
    """Run extract-document.py for a single doc. Returns (success, detail)."""
    input_path = doc["path"]
    domain = doc.get("domain", "general")
    doc_ref = doc.get("doc_ref")

    out_dir = Path(output_dir) / domain
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{Path(input_path).stem}.manifest.yaml"

    cmd = [
        sys.executable, EXTRACT_SCRIPT,
        "--input", input_path,
        "--output", str(manifest_path),
        "--domain", domain,
    ]
    if doc_ref:
        cmd.extend(["--doc-ref", doc_ref])
    if verbose:
        cmd.append("--verbose")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True, str(manifest_path)
    error = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
    return False, error


def _emit_cost_record(stats: dict, duration_s: float, wrk: str) -> None:
    """Append a cost-tracking JSONL record for the batch run."""
    cost_dir = Path(_repo_root) / ".claude" / "state" / "session-signals"
    cost_dir.mkdir(parents=True, exist_ok=True)
    cost_file = cost_dir / "cost-tracking.jsonl"
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "provider": "script",
        "model": "batch-extract",
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "wrk": wrk,
        "estimated": False,
        "batch_stats": {
            "processed": stats.get("completed", 0),
            "failed": stats.get("failed", 0),
            "duration_s": round(duration_s, 2),
        },
    }
    with open(cost_file, "a") as f:
        f.write(json.dumps(record) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch document extraction")
    parser.add_argument("--queue", required=True, help="Path to queue YAML")
    parser.add_argument("--batch-size", type=int, default=50, help="Docs per checkpoint")
    parser.add_argument("--rate-limit", type=float, default=2.0, help="Seconds between extractions")
    parser.add_argument("--resume", action="store_true", help="Skip completed/failed docs")
    parser.add_argument("--dry-run", action="store_true", help="Preview without processing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--wrk", default="WRK-5042", help="WRK ID for cost tracking")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    try:
        queue = load_queue(queue_path)
    except FileNotFoundError:
        print(f"Error: queue file not found: {args.queue}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    settings = queue.get("settings", {})
    output_dir = settings.get("output_dir", "data/doc-intelligence/manifests")
    rate_limit = args.rate_limit
    batch_size = args.batch_size

    pending = get_pending(queue)
    if not pending:
        stats = get_stats(queue)
        print(f"No pending documents. Stats: {stats}")
        return 3

    if args.dry_run:
        stats = get_stats(queue)
        print(f"Dry run — {len(pending)} pending documents would be processed.")
        print(f"Queue stats: {stats}")
        return 0

    start_time = time.monotonic()
    processed_count = 0
    failed_count = 0

    for i, doc in enumerate(pending):
        doc["status"] = "processing"

        success, detail = _extract_one(doc, output_dir, args.verbose)
        if success:
            mark_completed(doc, detail)
            processed_count += 1
            if args.verbose:
                print(f"  OK: {doc['path']} -> {detail}")
        else:
            mark_failed(doc, detail)
            failed_count += 1
            if args.verbose:
                print(f"  FAIL: {doc['path']}: {detail}")

        # Rate limit between docs (not after the last one)
        if i < len(pending) - 1 and rate_limit > 0:
            time.sleep(rate_limit)

        # Checkpoint every batch_size docs
        if (i + 1) % batch_size == 0:
            save_queue(queue, queue_path)
            if args.verbose:
                print(f"  Checkpoint at {i + 1}/{len(pending)}")

    # Final save
    save_queue(queue, queue_path)

    duration = time.monotonic() - start_time
    stats = get_stats(queue)
    print(f"Batch complete: {processed_count} processed, {failed_count} failed, "
          f"{stats['pending']} remaining. Duration: {duration:.1f}s")

    _emit_cost_record(
        {"completed": processed_count, "failed": failed_count},
        duration, args.wrk,
    )

    if failed_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
