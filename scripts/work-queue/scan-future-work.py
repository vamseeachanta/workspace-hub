#!/usr/bin/env python3
"""Scan assets/*/evidence/future-work.yaml for unqueued recommendations.

A recommendation is "unqueued" if:
  - captured: false (or field absent), OR
  - captured: true but no WRK file found with a matching title

Prints results to stdout. Exits 0 always (non-fatal scanner).

Usage:
    uv run --no-project python scripts/work-queue/scan-future-work.py [--days N]
"""
import argparse
import os
import sys
import time
import glob
import warnings

try:
    import yaml
except ImportError:
    print("WARNING: PyYAML not installed — install python3-yaml", file=sys.stderr)
    sys.exit(0)


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(REPO_ROOT, ".claude", "work-queue", "assets")
QUEUE_DIRS = [
    os.path.join(REPO_ROOT, ".claude", "work-queue", "pending"),
    os.path.join(REPO_ROOT, ".claude", "work-queue", "working"),
    os.path.join(REPO_ROOT, ".claude", "work-queue", "archive"),
]


import re as _re

_WRK_ID_RE = _re.compile(r"^WRK-\d+$", _re.IGNORECASE)


def load_wrk_ids() -> set[str]:
    """Return upper-cased WRK IDs of all files in pending/working/archive."""
    ids: set[str] = set()
    for queue_dir in QUEUE_DIRS:
        pattern = os.path.join(queue_dir, "**", "*.md")
        for path in glob.glob(pattern, recursive=True):
            name = os.path.basename(path)
            if name.endswith(".md"):
                wrk_id = name[:-3].upper()
                if _WRK_ID_RE.match(wrk_id):
                    ids.add(wrk_id)
    return ids


def _capture_ref_missing(capture_ref: str, wrk_ids: set[str]) -> bool:
    """Return True if capture_ref looks like a WRK ID that doesn't exist."""
    ref = (capture_ref or "").strip().upper()
    return bool(_WRK_ID_RE.match(ref)) and ref not in wrk_ids


def scan(days: int) -> list[dict]:
    """Return list of unqueued recommendations within the lookback window.

    A recommendation is "unqueued" when:
      - captured: false (or absent), OR
      - captured: true AND capture_ref is a WRK-NNN id that no longer exists
    """
    cutoff = time.time() - days * 86400
    wrk_ids = load_wrk_ids()
    results = []

    pattern = os.path.join(ASSETS_DIR, "*", "evidence", "future-work.yaml")
    for path in sorted(glob.glob(pattern)):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if mtime < cutoff:
            continue

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as exc:
            print(f"WARNING: malformed YAML {path}: {exc}", file=sys.stderr)
            continue

        wrk_id = data.get("wrk_id", os.path.basename(os.path.dirname(os.path.dirname(path))))
        for rec in data.get("recommendations", []):
            title = rec.get("title", "").strip()
            if not title:
                continue
            captured = rec.get("captured", False)
            capture_ref = str(rec.get("capture_ref", "") or "")
            # Skip items that are captured and either have no WRK ref or a valid one
            if captured and not _capture_ref_missing(capture_ref, wrk_ids):
                continue
            results.append({
                "wrk_id": wrk_id,
                "fw_id": rec.get("id", "?"),
                "title": title,
                "captured": captured,
                "capture_ref": capture_ref,
                "severity": rec.get("severity") or rec.get("priority", ""),
                "disposition": rec.get("disposition", ""),
                "source_yaml": path,
            })

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30,
                        help="Lookback window in days (default: 30)")
    parser.add_argument("--candidates-file", default=None,
                        help="If set, append results to this candidates .md file")
    args = parser.parse_args()

    items = scan(args.days)

    if not items:
        print(f"scan-future-work: no unqueued items in last {args.days} days")
        return

    print(f"scan-future-work: {len(items)} unqueued recommendation(s) in last {args.days} days\n")
    print(f"{'WRK-ID':<12} {'FW-ID':<8} {'Captured':<10} {'Severity':<10} Title")
    print("-" * 80)
    for it in items:
        flag = " [ref-missing]" if it["captured"] else ""
        print(f"{it['wrk_id']:<12} {it['fw_id']:<8} {str(it['captured']):<10} "
              f"{str(it['severity']):<10} {it['title'][:44]}{flag}")

    if args.candidates_file:
        _append_candidates(items, args.candidates_file)


def _append_candidates(items: list[dict], dest: str) -> None:
    """Append unqueued future-work items as Phase 7 action candidates."""
    import datetime
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"\n## Future-Work Candidates (scan-future-work {ts})\n"]
    for it in items:
        lines.append(
            f"- Source: {it['wrk_id']}/{it['fw_id']} | "
            f"captured={it['captured']} | "
            f"severity={it['severity']}\n"
            f"  Title: {it['title']}\n"
            f"  YAML: {it['source_yaml']}\n"
        )
    try:
        with open(dest, "a", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"\nAppended {len(items)} candidate(s) to {dest}")
    except OSError as exc:
        print(f"WARNING: could not write candidates file: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
