#!/usr/bin/env python3
"""Marine standards batch processor.

Reads the standards-transfer-ledger YAML, filters for a given domain
(default: marine) with status != "done", validates file existence,
extracts basic metadata, and updates status to "done".

Usage:
    uv run python scripts/document-intelligence/batch-process-standards.py
    uv run python scripts/document-intelligence/batch-process-standards.py --dry-run
    uv run python scripts/document-intelligence/batch-process-standards.py --domain marine --limit 5

Issue: #1621
"""

import argparse
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_LEDGER = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "document-index"
    / "standards-transfer-ledger.yaml"
)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def load_ledger(path: str) -> dict:
    """Load a standards-transfer-ledger YAML file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Ledger not found: {path}")
    with open(p, "r") as f:
        return yaml.safe_load(f)


def save_ledger(data: dict, path: str) -> None:
    """Write the ledger dict back to YAML."""
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def filter_standards(
    standards: List[Dict], domain: str = "marine"
) -> List[Dict]:
    """Return standards matching *domain* whose status is not 'done'."""
    return [
        s
        for s in standards
        if s.get("domain") == domain and s.get("status") != "done"
    ]


def apply_status_transition(entry: dict) -> None:
    """Transition an entry to 'done' (idempotent if already done)."""
    if entry.get("status") == "done":
        return
    entry["status"] = "done"
    entry["implemented_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def extract_metadata(file_path: str) -> dict:
    """Extract basic metadata from a file on disk.

    Returns a dict with keys: exists, file_size_bytes, title_from_name.
    """
    p = Path(file_path)
    if p.exists():
        stat = p.stat()
        return {
            "exists": True,
            "file_size_bytes": stat.st_size,
            "title_from_name": p.stem,
        }
    return {
        "exists": False,
        "file_size_bytes": 0,
        "title_from_name": Path(file_path).stem if file_path else "",
    }


# ---------------------------------------------------------------------------
# Progress tracker
# ---------------------------------------------------------------------------


@dataclass
class BatchProgress:
    """Tracks batch processing progress."""

    total: int
    _processed: List[str] = field(default_factory=list)

    @property
    def processed(self) -> int:
        return len(self._processed)

    @property
    def remaining(self) -> int:
        return self.total - self.processed

    def mark_processed(self, standard_id: str) -> None:
        self._processed.append(standard_id)

    def summary(self) -> str:
        return f"Processed {self.processed}/{self.total} standards"


# ---------------------------------------------------------------------------
# Core batch runner
# ---------------------------------------------------------------------------


def run_batch(
    ledger_path: str,
    domain: str = "marine",
    dry_run: bool = False,
    limit: Optional[int] = None,
) -> Dict:
    """Run the batch processor.

    Returns a dict with keys: processed_count, skipped_done, results.
    """
    data = load_ledger(ledger_path)
    candidates = filter_standards(data["standards"], domain=domain)

    if limit is not None:
        candidates = candidates[:limit]

    progress = BatchProgress(total=len(candidates))
    results: list[dict] = []

    for entry in candidates:
        # Validate file existence + extract metadata
        doc_path = entry.get("doc_path", "")
        meta = extract_metadata(doc_path) if doc_path else extract_metadata("")

        if not dry_run:
            apply_status_transition(entry)

        progress.mark_processed(entry["id"])
        results.append(
            {
                "id": entry["id"],
                "title": entry.get("title", ""),
                "file_exists": meta["exists"],
                "file_size_bytes": meta["file_size_bytes"],
            }
        )

    if not dry_run:
        # Recount summary
        from collections import Counter

        status_counts = Counter(s.get("status") for s in data["standards"])
        data["summary"] = dict(status_counts)
        save_ledger(data, ledger_path)

    print(progress.summary())

    return {
        "processed_count": progress.processed,
        "total_candidates": progress.total,
        "results": results,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-process standards in the transfer ledger")
    parser.add_argument(
        "--ledger",
        default=str(DEFAULT_LEDGER),
        help="Path to the standards-transfer-ledger YAML",
    )
    parser.add_argument(
        "--domain",
        default="marine",
        help="Domain to filter (default: marine)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max standards to process",
    )

    args = parser.parse_args()
    result = run_batch(
        ledger_path=args.ledger,
        domain=args.domain,
        dry_run=args.dry_run,
        limit=args.limit,
    )

    # Print summary
    mode = "DRY RUN" if result["dry_run"] else "LIVE"
    print(f"\n[{mode}] {result['processed_count']} of {result['total_candidates']} "
          f"{args.domain} standards processed")

    if result["results"]:
        found = sum(1 for r in result["results"] if r["file_exists"])
        missing = len(result["results"]) - found
        print(f"  Files found: {found}  |  Missing: {missing}")

    for r in result["results"]:
        status_icon = "✓" if r["file_exists"] else "✗"
        size_str = f"{r['file_size_bytes']:,} bytes" if r["file_exists"] else "N/A"
        print(f"  {status_icon} {r['id']}: {r['title'][:60]}  ({size_str})")


if __name__ == "__main__":
    main()
