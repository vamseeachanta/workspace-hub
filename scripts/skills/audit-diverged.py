"""audit-diverged.py — Audit and resolve _diverged/ skill directories.

ABOUTME: Compares each _diverged/<repo>/<skill>/SKILL.md against its canonical
counterpart. Classifies as identical/behind/ahead/orphan. Auto-deletes identical
and behind entries. Reports ahead and orphan for manual review.

WRK-639.

Usage:
    uv run --no-project python scripts/skills/audit-diverged.py [--dry-run] [--resolve]
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import os
import shutil
import sys
from pathlib import Path


def hash_file(path: str) -> str:
    """SHA-256 hash of file contents."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return ""


def find_canonical(skill_name: str, skills_root: str, diverged_dir: str) -> str | None:
    """Find canonical SKILL.md for a given skill name outside _diverged/."""
    for skill_md in glob.glob(
        os.path.join(skills_root, "**", skill_name, "SKILL.md"), recursive=True
    ):
        # Skip _diverged, incoming, _archive
        if any(skip in skill_md for skip in ["_diverged", "incoming", "_archive"]):
            continue
        return skill_md
    return None


def classify(diverged_path: str, canonical_path: str | None) -> str:
    """Classify a diverged skill: identical, behind, ahead, or orphan."""
    if canonical_path is None:
        return "orphan"

    div_hash = hash_file(diverged_path)
    can_hash = hash_file(canonical_path)

    if div_hash == can_hash:
        return "identical"

    # Compare by file size as rough heuristic for behind/ahead
    div_size = os.path.getsize(diverged_path)
    can_size = os.path.getsize(canonical_path)

    # If canonical is larger or same, diverged is behind
    if can_size >= div_size:
        return "behind"

    return "ahead"


def main():
    parser = argparse.ArgumentParser(description="Audit _diverged/ skills")
    parser.add_argument("--dry-run", action="store_true", help="Don't delete, just report")
    parser.add_argument("--resolve", action="store_true", help="Auto-delete identical/behind")
    args = parser.parse_args()

    ws_root = os.environ.get(
        "WORKSPACE_ROOT",
        str(Path(__file__).parent.parent.parent),
    )
    skills_root = os.path.join(ws_root, ".claude", "skills")
    diverged_root = os.path.join(skills_root, "_diverged")

    if not os.path.isdir(diverged_root):
        print("No _diverged/ directory found.")
        return

    results = {"identical": [], "behind": [], "ahead": [], "orphan": []}

    for skill_md in sorted(glob.glob(
        os.path.join(diverged_root, "**", "SKILL.md"), recursive=True
    )):
        rel = os.path.relpath(skill_md, diverged_root)
        parts = Path(rel).parts
        if len(parts) < 2:
            continue
        skill_name = parts[-2]  # directory containing SKILL.md

        canonical = find_canonical(skill_name, skills_root, diverged_root)
        cat = classify(skill_md, canonical)
        results[cat].append((rel, skill_md, canonical))

    # Report
    total = sum(len(v) for v in results.values())
    print(f"=== Diverged Skills Audit ({total} total) ===")
    for cat in ["identical", "behind", "ahead", "orphan"]:
        count = len(results[cat])
        print(f"  {cat}: {count}")

    if results["ahead"]:
        print("\n--- AHEAD (manual review needed) ---")
        for rel, div, can in results["ahead"]:
            print(f"  {rel} → canonical: {can}")

    if results["orphan"]:
        print("\n--- ORPHAN (no canonical found) ---")
        for rel, div, can in results["orphan"]:
            print(f"  {rel}")

    # Resolve
    if args.resolve and not args.dry_run:
        deleted = 0
        for cat in ["identical", "behind"]:
            for rel, div, can in results[cat]:
                skill_dir = os.path.dirname(div)
                shutil.rmtree(skill_dir, ignore_errors=True)
                deleted += 1
        print(f"\nResolved: deleted {deleted} identical/behind skill directories")

        # Clean up empty repo directories
        for repo_dir in glob.glob(os.path.join(diverged_root, "*")):
            if os.path.isdir(repo_dir) and not os.listdir(repo_dir):
                os.rmdir(repo_dir)
                print(f"  Removed empty: {os.path.basename(repo_dir)}/")
    elif args.resolve and args.dry_run:
        deletable = len(results["identical"]) + len(results["behind"])
        print(f"\n[DRY RUN] Would delete {deletable} identical/behind directories")

    return results


if __name__ == "__main__":
    main()
