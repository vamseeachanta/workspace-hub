#!/usr/bin/env -S uv run --no-project python
"""Bulk-assign category + subcategory fields to WRK items that lack them.

Usage:
    python scripts/work-queue/assign-categories.py          # dry-run (preview table)
    python scripts/work-queue/assign-categories.py --apply  # write changes
    python scripts/work-queue/assign-categories.py --apply --all  # overwrite existing too
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Load infer-category.py (hyphenated name — use importlib)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "infer_category",
    Path(__file__).parent / "infer-category.py",
)
_mod = _ilu.module_from_spec(_spec)  # type: ignore
_spec.loader.exec_module(_mod)  # type: ignore
infer = _mod.infer

QUEUE_ROOT = Path(__file__).resolve().parent.parent.parent / ".claude" / "work-queue"
STATUS_DIRS = ["pending", "working", "blocked"]


def _get_frontmatter_section(text: str) -> str:
    """Return just the YAML frontmatter content (between the two --- delimiters)."""
    first = text.find("---")
    if first == -1:
        return ""
    second = text.find("\n---", first + 3)
    if second == -1:
        return ""
    return text[first + 3:second]


def _get_frontmatter_field(text: str, field: str) -> str:
    fm = _get_frontmatter_section(text)
    m = re.search(rf"^{field}:\s*(.*)$", fm, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip()


def _set_frontmatter_fields(text: str, updates: dict[str, str]) -> str:
    """Set multiple fields strictly inside the YAML frontmatter block.

    Parses the --- delimiters, updates fields in the FM section only,
    and strips any stray occurrences of those fields from the body.
    """
    # Split on first and second '---' delimiters
    first = text.find("---")
    if first == -1:
        return text
    second = text.find("\n---", first + 3)
    if second == -1:
        return text
    fm_start = first + 3       # after opening ---
    fm_end = second            # position of \n---
    fm = text[fm_start:fm_end]
    body = text[fm_end:]       # \n---\n...body...

    # Update or insert each field inside fm
    for field, value in updates.items():
        pattern = rf"^{field}:\s*.*$"
        if re.search(pattern, fm, re.MULTILINE):
            fm = re.sub(pattern, f"{field}: {value}", fm, flags=re.MULTILINE)
        else:
            fm = fm.rstrip("\n") + f"\n{field}: {value}\n"

        # Remove stray occurrences from body (left by earlier buggy writes)
        body = re.sub(rf"^{field}:.*\n?", "", body, flags=re.MULTILINE)

    return f"---{fm}{body}"


def process_file(path: Path, apply: bool, overwrite: bool) -> dict | None:
    text = path.read_text(errors="replace")

    existing_cat = _get_frontmatter_field(text, "category")
    existing_sub = _get_frontmatter_field(text, "subcategory")

    has_cat = bool(existing_cat and existing_cat != "uncategorised")
    has_sub = bool(existing_sub and existing_sub != "uncategorised")

    if has_cat and has_sub and not overwrite:
        return None  # nothing to do

    title = _get_frontmatter_field(text, "title").strip('"')
    # Grab body (everything after closing ---)
    parts = text.split("---", 2)
    body = parts[2] if len(parts) >= 3 else ""

    result = infer(title, body)
    new_cat = result["category"]
    new_sub = result["subcategory"]

    # Only update fields that are missing/uncategorised (unless --all)
    final_cat = new_cat if (not has_cat or overwrite) else existing_cat
    final_sub = new_sub if (not has_sub or overwrite) else existing_sub

    changed = (final_cat != existing_cat) or (final_sub != existing_sub)
    if not changed:
        return None

    if apply:
        new_text = _set_frontmatter_fields(text, {
            "category": final_cat,
            "subcategory": final_sub,
        })
        path.write_text(new_text)

    return {
        "file": path.name,
        "title": title[:55] + ("…" if len(title) > 55 else ""),
        "old_cat": existing_cat or "(none)",
        "old_sub": existing_sub or "(none)",
        "new_cat": final_cat,
        "new_sub": final_sub,
        "written": apply,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default: dry-run)")
    parser.add_argument("--all", dest="overwrite", action="store_true",
                        help="Overwrite existing non-uncategorised values too")
    args = parser.parse_args()

    results = []
    for d in STATUS_DIRS:
        d_path = QUEUE_ROOT / d
        if not d_path.exists():
            continue
        for f in sorted(d_path.glob("WRK-*.md")):
            r = process_file(f, apply=args.apply, overwrite=args.overwrite)
            if r:
                results.append(r)

    if not results:
        print("No changes needed — all items already categorised.")
        return

    # Summary by category
    from collections import Counter
    cat_counts: Counter = Counter(r["new_cat"] for r in results)

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n{'='*70}")
    print(f"  assign-categories.py  [{mode}]  {len(results)} items to update")
    print(f"{'='*70}\n")

    # Category summary
    print("Category distribution of changes:")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat:<20} {count:>3} items")
    print()

    # Per-item table
    col = "{:<12}  {:<20}  {:<18}  {}"
    print(col.format("WRK", "Category→Sub", "Was", "Title"))
    print("-" * 70)
    for r in results:
        wrk = r["file"].replace(".md", "")
        new = f"{r['new_cat']}/{r['new_sub']}"
        was = f"{r['old_cat']}/{r['old_sub']}"
        print(col.format(wrk, new, was, r["title"]))

    print()
    if not args.apply:
        print("  Run with --apply to write changes.")
    else:
        print(f"  {len(results)} items updated.")


if __name__ == "__main__":
    main()
