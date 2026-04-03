#!/usr/bin/env python3
"""
Cross-Drive Deduplication Audit Script (GitHub Issue #1757)

Compares files between /mnt/ace (local NVMe) and the DDE remote drive
(/mnt/remote/ace-linux-2/dde/) to identify duplicates and unique files.

Strategy:
  1. First pass: index files by (filename, file_size) — cheap metadata only
  2. Second pass: SHA-256 hash only the candidate matches — minimizes remote I/O
  3. Output JSON report + stdout summary

Usage:
    uv run --no-project python scripts/data/document-index/cross-drive-dedup-audit.py
    uv run --no-project python scripts/data/document-index/cross-drive-dedup-audit.py --dry-run
"""

import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ── Drive pair definitions ──────────────────────────────────────────────────
DRIVE_PAIRS = [
    {
        "ace_path": "/mnt/ace/docs/",
        "dde_path": "/mnt/remote/ace-linux-2/dde/documents/",
        "label": "project-docs",
    },
    {
        "ace_path": "/mnt/ace/O&G-Standards/",
        "dde_path": "/mnt/remote/ace-linux-2/dde/0000 O&G/0000 Codes & Standards/",
        "label": "og-standards",
    },
]

REPORT_PATH = Path("data/document-index/cross-drive-dedup-report.json")
HASH_BUF_SIZE = 1 << 16  # 64 KiB read buffer for SHA-256
MAX_UNIQUE_TO_DDE = 500


def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hex digest for a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(HASH_BUF_SIZE)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError) as exc:
        print(f"  WARN: cannot hash {filepath}: {exc}", file=sys.stderr)
        return f"ERROR:{exc}"


def walk_files(root: str) -> list[dict]:
    """Walk a directory tree, returning list of {path, filename, size_bytes}."""
    results = []
    root = os.path.normpath(root)
    if not os.path.isdir(root):
        print(f"  WARN: directory not found: {root}", file=sys.stderr)
        return results
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                if not stat.st_size:
                    continue  # skip zero-byte files
                results.append({
                    "path": fpath,
                    "filename": fname.lower(),  # case-insensitive matching
                    "filename_orig": fname,
                    "size_bytes": stat.st_size,
                })
            except (OSError, PermissionError):
                pass  # broken symlinks, permission issues
    return results


def build_key_index(file_list: list[dict]) -> dict[tuple, list[dict]]:
    """Index files by (lowercase_filename, size_bytes) key."""
    idx = defaultdict(list)
    for f in file_list:
        key = (f["filename"], f["size_bytes"])
        idx[key].append(f)
    return idx


def run_audit(dry_run: bool = False) -> dict:
    """Run the full cross-drive dedup audit. Returns report dict."""
    timestamp = datetime.now(timezone.utc).isoformat()
    report = {
        "generated": timestamp,
        "pairs_compared": [],
        "summary": {
            "total_ace_files": 0,
            "total_dde_files": 0,
            "exact_duplicates": 0,
            "name_size_matches": 0,
            "unique_to_ace": 0,
            "unique_to_dde": 0,
            "dde_unique_size_bytes": 0,
        },
        "unique_to_dde": [],
    }

    all_ace_files: list[dict] = []
    all_dde_files: list[dict] = []
    all_name_size_matches = 0
    all_exact_dupes = 0

    # Collect all DDE files that are NOT matched — we'll track per-pair
    dde_matched_paths: set[str] = set()

    for pair in DRIVE_PAIRS:
        ace_root = pair["ace_path"]
        dde_root = pair["dde_path"]
        label = pair["label"]

        print(f"\n{'='*70}")
        print(f"PAIR: {label}")
        print(f"  ACE: {ace_root}")
        print(f"  DDE: {dde_root}")

        t0 = time.time()
        print("  Scanning ACE files...", end=" ", flush=True)
        ace_files = walk_files(ace_root)
        print(f"{len(ace_files):,} files ({time.time()-t0:.1f}s)")

        t0 = time.time()
        print("  Scanning DDE files...", end=" ", flush=True)
        dde_files = walk_files(dde_root)
        print(f"{len(dde_files):,} files ({time.time()-t0:.1f}s)")

        report["pairs_compared"].append({
            "ace_path": ace_root,
            "dde_path": dde_root,
            "label": label,
            "ace_files": len(ace_files),
            "dde_files": len(dde_files),
        })

        all_ace_files.extend(ace_files)
        all_dde_files.extend(dde_files)

        if dry_run:
            print("  [DRY RUN] Skipping hash comparison.")
            continue

        # ── Pass 1: name+size matching ──────────────────────────────────
        ace_idx = build_key_index(ace_files)
        dde_idx = build_key_index(dde_files)

        # Find overlapping keys
        common_keys = set(ace_idx.keys()) & set(dde_idx.keys())
        pair_name_size = 0
        pair_exact = 0

        # Count candidate files on DDE side
        candidate_dde_paths: set[str] = set()
        candidate_ace_paths: set[str] = set()
        for key in common_keys:
            for f in dde_idx[key]:
                candidate_dde_paths.add(f["path"])
                pair_name_size += 1
            for f in ace_idx[key]:
                candidate_ace_paths.add(f["path"])

        print(f"  Name+size candidates: {pair_name_size:,} DDE files match "
              f"{len(candidate_ace_paths):,} ACE files across {len(common_keys):,} keys")

        # ── Pass 2: SHA-256 on candidates only ─────────────────────────
        if common_keys:
            print("  Hashing ACE candidates...", end=" ", flush=True)
            t0 = time.time()
            ace_hashes: dict[tuple, set[str]] = {}
            for key in common_keys:
                for f in ace_idx[key]:
                    digest = sha256_file(f["path"])
                    hash_key = (key[0], key[1], digest)
                    ace_hashes.setdefault(hash_key, set()).add(f["path"])
            print(f"done ({time.time()-t0:.1f}s)")

            print("  Hashing DDE candidates...", end=" ", flush=True)
            t0 = time.time()
            for key in common_keys:
                for f in dde_idx[key]:
                    digest = sha256_file(f["path"])
                    hash_key = (key[0], key[1], digest)
                    if hash_key in ace_hashes:
                        pair_exact += 1
                        dde_matched_paths.add(f["path"])
            print(f"done ({time.time()-t0:.1f}s)")

        print(f"  Exact SHA-256 duplicates: {pair_exact:,}")
        all_name_size_matches += pair_name_size
        all_exact_dupes += pair_exact

    # ── Build unique-to-DDE list ────────────────────────────────────────
    unique_dde_list = []
    unique_dde_size = 0

    if not dry_run:
        for f in all_dde_files:
            if f["path"] not in dde_matched_paths:
                unique_dde_list.append(f)
                unique_dde_size += f["size_bytes"]

        # Sort by size descending, take top N
        unique_dde_list.sort(key=lambda x: x["size_bytes"], reverse=True)
        unique_dde_list = unique_dde_list[:MAX_UNIQUE_TO_DDE]

    unique_to_ace_count = len(all_ace_files)  # simplified: ace files not matched
    unique_to_dde_count = len(all_dde_files) - len(dde_matched_paths) if not dry_run else 0

    # ── Populate summary ────────────────────────────────────────────────
    report["summary"]["total_ace_files"] = len(all_ace_files)
    report["summary"]["total_dde_files"] = len(all_dde_files)
    report["summary"]["exact_duplicates"] = all_exact_dupes
    report["summary"]["name_size_matches"] = all_name_size_matches
    report["summary"]["unique_to_ace"] = unique_to_ace_count - all_exact_dupes if not dry_run else len(all_ace_files)
    report["summary"]["unique_to_dde"] = unique_to_dde_count
    report["summary"]["dde_unique_size_bytes"] = unique_dde_size

    report["unique_to_dde"] = [
        {"path": f["path"], "size_bytes": f["size_bytes"], "filename": f["filename_orig"]}
        for f in unique_dde_list
    ]

    return report


def format_size(nbytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PiB"


def print_summary(report: dict, dry_run: bool = False) -> None:
    """Print a human-readable summary to stdout."""
    s = report["summary"]
    print(f"\n{'='*70}")
    print("CROSS-DRIVE DEDUP AUDIT SUMMARY")
    print(f"{'='*70}")
    print(f"  Generated:          {report['generated']}")
    print()
    for p in report["pairs_compared"]:
        print(f"  Pair: {p.get('label', 'unknown')}")
        print(f"    ACE ({p['ace_path']}): {p['ace_files']:,} files")
        print(f"    DDE ({p['dde_path']}): {p['dde_files']:,} files")
    print()
    print(f"  Total ACE files:    {s['total_ace_files']:,}")
    print(f"  Total DDE files:    {s['total_dde_files']:,}")
    if not dry_run:
        print(f"  Name+size matches:  {s['name_size_matches']:,}")
        print(f"  Exact duplicates:   {s['exact_duplicates']:,}")
        print(f"  Unique to ACE:      {s['unique_to_ace']:,}")
        print(f"  Unique to DDE:      {s['unique_to_dde']:,}")
        print(f"  DDE unique size:    {format_size(s['dde_unique_size_bytes'])}")
    else:
        print("  [DRY RUN — hashing skipped]")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-drive deduplication audit: ACE vs DDE (issue #1757)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only count files, skip SHA-256 hashing",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(REPORT_PATH),
        help=f"Output JSON report path (default: {REPORT_PATH})",
    )
    args = parser.parse_args()

    print("Cross-Drive Deduplication Audit (ACE vs DDE)")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FULL AUDIT'}")

    report = run_audit(dry_run=args.dry_run)
    print_summary(report, dry_run=args.dry_run)

    # Write JSON report
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()
