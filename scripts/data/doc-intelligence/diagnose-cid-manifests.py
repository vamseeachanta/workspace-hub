#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Scan naval-architecture manifests and report CID corruption levels.

Usage:
    uv run --no-project python scripts/data/doc-intelligence/diagnose-cid-manifests.py
    uv run --no-project python scripts/data/doc-intelligence/diagnose-cid-manifests.py --domain naval-architecture
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

CID_PATTERN = re.compile(r"\(cid:\d+\)")


def diagnose_manifest(manifest_path: Path) -> dict:
    """Analyze a manifest for CID corruption."""
    with open(manifest_path) as f:
        data = yaml.safe_load(f)

    sections = data.get("sections") or []
    if not sections:
        return {"status": "empty", "total_chars": 0, "cid_ratio": 0.0}

    total_chars = sum(len(s.get("text", "")) for s in sections)
    if total_chars == 0:
        return {"status": "empty", "total_chars": 0, "cid_ratio": 0.0}

    cid_chars = 0
    for s in sections:
        text = s.get("text", "")
        cid_chars += sum(len(m.group()) for m in CID_PATTERN.finditer(text))

    cid_ratio = cid_chars / total_chars
    if cid_ratio > 0.10:
        status = "CORRUPTED"
    elif cid_ratio > 0.01:
        status = "PARTIAL"
    else:
        status = "CLEAN"

    return {
        "status": status,
        "total_chars": total_chars,
        "cid_ratio": cid_ratio,
        "sections": len(sections),
    }


def main():
    parser = argparse.ArgumentParser(description="Diagnose CID corruption in manifests")
    parser.add_argument(
        "--domain", default="naval-architecture", help="Domain subdirectory"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    manifest_dir = repo_root / "data" / "doc-intelligence" / "manifests" / args.domain

    if not manifest_dir.exists():
        print(f"ERROR: {manifest_dir} not found", file=sys.stderr)
        sys.exit(1)

    manifests = sorted(manifest_dir.glob("*.manifest.yaml"))
    print(f"Scanning {len(manifests)} manifests in {args.domain}/\n")

    results = {"CORRUPTED": [], "PARTIAL": [], "CLEAN": [], "empty": []}
    for mf in manifests:
        info = diagnose_manifest(mf)
        stem = mf.stem.replace(".manifest", "")
        results[info["status"]].append((stem, info))

    for status in ["CORRUPTED", "PARTIAL", "CLEAN", "empty"]:
        items = results[status]
        print(f"── {status} ({len(items)}) ──")
        for stem, info in items:
            if status in ("CORRUPTED", "PARTIAL"):
                print(
                    f"  {stem}  cid_ratio={info['cid_ratio']:.1%}  "
                    f"chars={info['total_chars']}  sections={info.get('sections', 0)}"
                )
            elif status == "CLEAN":
                print(f"  {stem}  chars={info['total_chars']}  sections={info.get('sections', 0)}")
        print()

    corrupted = len(results["CORRUPTED"])
    partial = len(results["PARTIAL"])
    clean = len(results["CLEAN"])
    empty = len(results["empty"])
    print(f"Summary: {corrupted} corrupted, {partial} partial, {clean} clean, {empty} empty")

    if corrupted > 0:
        print(f"\nRe-extraction needed for {corrupted} manifests (pypdfium2 fallback)")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
