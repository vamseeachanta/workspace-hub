#!/usr/bin/env -S uv run --no-project python
"""Bulk-assign the `computer:` field to WRK items that lack it.

Routing rules are derived from workstations SKILL.md.  The script reads
each item's `target_repos` and `title`, applies the rules, and writes the
`computer:` line into the frontmatter if it is absent or blank.

Usage:
    python scripts/work-queue/assign-workstations.py          # dry-run
    python scripts/work-queue/assign-workstations.py --apply  # write changes
    python scripts/work-queue/assign-workstations.py --apply --all  # also overwrite existing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

QUEUE_ROOT = Path(__file__).resolve().parent.parent.parent / ".claude" / "work-queue"
STATUS_DIRS = ["pending", "working", "blocked"]

# ---------------------------------------------------------------------------
# Routing rules — order matters (first match wins)
# ---------------------------------------------------------------------------

KEYWORD_RULES: list[tuple[list[str], str]] = [
    # License-locked tools — highest priority
    (["orcaflex", "orcawave", "ansys", "aqwa"], "acma-ansys05"),
    # Open-source FEA/CFD/animation — ace-linux-2 speciality
    (["openfoam", "blender", "gmsh", "calculix", "fenics", "fenicsx",
      "freecad", "elmer", "cfd", "fea-hpc", "heavy-compute", "large-sim"],
     "ace-linux-2"),
    # GPU-heavy compute
    (["gali", "gpu-training", "cuda-training"], "gali-linux-compute-1"),
    # Windows-only tools
    (["solidworks", "windows-only", "ms-office", "excel-macro"], "acma-ws014"),
]

REPO_RULES: dict[str, str] = {
    "worldenergydata": "ace-linux-1",
    "aceengineer-website": "ace-linux-1",
    "aceengineer-admin": "ace-linux-1",
    "aceengineer-strategy": "ace-linux-1",
    "workspace-hub": "ace-linux-1",
    "digitalmodel": "ace-linux-1",
    "assetutilities": "ace-linux-1",
    "assethold": "ace-linux-1",
    "achantas-data": "ace-linux-1",
    "hobbies": "ace-linux-1",
    "investments": "ace-linux-1",
    "sabithaandkrishnaestates": "ace-linux-1",
    "saipem": "ace-linux-1",
    "rock-oil-field": "ace-linux-1",
    "OGManufacturing": "ace-linux-1",
    "doris": "ace-linux-1",
    "frontierdeepwater": "ace-linux-1",
    "acma-projects": "ace-linux-1",  # default; keyword rules may override
    "pdf-large-reader": "ace-linux-1",
    "pyproject-starter": "ace-linux-1",
}

DEFAULT_MACHINE = "ace-linux-1"

# Items whose title or tags suggest they are purely machine-agnostic
# (hub-only docs, skill files, queue management with no external tooling)
# We still assign ace-linux-1 rather than leaving blank, per SKILL.md.


def _read_frontmatter(path: Path) -> tuple[str, str, str]:
    """Return (pre_fm, fm_block, post_fm) from a markdown file.

    pre_fm  = '---\\n'
    fm_block = raw YAML lines between the delimiters (no surrounding ---)
    post_fm  = everything after the closing '---'
    """
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^(---\s*\n)(.*?)\n(---)(.*)", text, re.DOTALL)
    if not m:
        return ("", "", text)
    return (m.group(1), m.group(2), m.group(3) + m.group(4))


def _get_field(fm_block: str, field: str) -> str:
    """Extract a scalar frontmatter field value (empty string if absent)."""
    m = re.search(rf"^{field}:\s*(.*)", fm_block, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip().strip('"\'')


def _get_list_field(fm_block: str, field: str) -> list[str]:
    """Extract a YAML list frontmatter field."""
    # Inline list: field: [a, b]
    m = re.search(rf"^{field}:\s*\[([^\]]*)\]", fm_block, re.MULTILINE)
    if m:
        items = [v.strip().strip("'\"") for v in m.group(1).split(",") if v.strip()]
        return items
    # Block list: field:\n  - item
    m = re.search(rf"^{field}:\s*\n((?:\s+-[^\n]*\n?)*)", fm_block, re.MULTILINE)
    if m:
        items = re.findall(r"^\s+-\s+(.+)", m.group(1), re.MULTILINE)
        return [i.strip().strip("'\"") for i in items]
    return []


def determine_machine(title: str, repos: list[str]) -> str:
    """Apply routing rules and return the target machine nickname."""
    title_lower = title.lower()

    # 1. Keyword scan (title) — highest priority
    for keywords, machine in KEYWORD_RULES:
        if any(kw in title_lower for kw in keywords):
            return machine

    # 2. Repo-based routing
    for repo in repos:
        if repo in REPO_RULES:
            return REPO_RULES[repo]

    return DEFAULT_MACHINE


def _insert_computer_field(fm_block: str, machine: str) -> str:
    """Insert or replace the `computer:` line in the frontmatter block.

    Inserts after the `brochure_status:` line if present, otherwise appends.
    """
    # If already has a non-blank value, leave it unless --all was requested
    existing = _get_field(fm_block, "computer")
    if existing:
        return None  # signal: skip

    # Replace blank `computer:` or `computer: ` lines
    if re.search(r"^computer:\s*$", fm_block, re.MULTILINE):
        return re.sub(r"^computer:\s*$", f"computer: {machine}", fm_block,
                      flags=re.MULTILINE, count=1)

    # Insert after brochure_status: if present
    if re.search(r"^brochure_status:", fm_block, re.MULTILINE):
        return re.sub(
            r"(^brochure_status:.*)",
            rf"\1\ncomputer: {machine}",
            fm_block,
            flags=re.MULTILINE,
            count=1,
        )

    # Append at end of frontmatter
    return fm_block.rstrip() + f"\ncomputer: {machine}"


def _overwrite_computer_field(fm_block: str, machine: str) -> str:
    """Set computer: regardless of existing value."""
    if re.search(r"^computer:\s*\S", fm_block, re.MULTILINE):
        return re.sub(r"^computer:\s*\S.*", f"computer: {machine}", fm_block,
                      flags=re.MULTILINE, count=1)
    return _insert_computer_field(fm_block, machine)


def process_file(path: Path, apply: bool, overwrite_existing: bool) -> str | None:
    """Determine machine for a WRK item and optionally write it.

    Returns a human-readable status string, or None if already set and not overwriting.
    """
    pre, fm_block, post = _read_frontmatter(path)
    if not fm_block:
        return f"SKIP (no frontmatter): {path.name}"

    current = _get_field(fm_block, "computer")
    if current and not overwrite_existing:
        return None  # already set, skip silently

    title = _get_field(fm_block, "title") or path.stem
    repos = _get_list_field(fm_block, "target_repos")
    wrk_id = _get_field(fm_block, "id") or path.stem

    machine = determine_machine(title, repos)

    if current == machine:
        return None  # already correct

    action = "OVERWRITE" if current else "ASSIGN"
    label = f"{action}: {wrk_id:12s} → {machine:20s}  [{', '.join(repos) or 'no-repo'}] title={title[:60]}"

    if apply:
        if overwrite_existing:
            new_fm = _overwrite_computer_field(fm_block, machine)
        else:
            new_fm = _insert_computer_field(fm_block, machine)
            if new_fm is None:
                return None

        # Ensure a newline separates the fm block from the closing ---
        if not new_fm.endswith("\n"):
            new_fm += "\n"
        new_text = pre + new_fm + post
        path.write_text(new_text, encoding="utf-8")
        label = label.replace(action, f"{action}✓")

    return label


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default: dry-run only)")
    parser.add_argument("--all", dest="overwrite_all", action="store_true",
                        help="Also overwrite items that already have a computer: value")
    args = parser.parse_args()

    if not args.apply:
        print("DRY-RUN mode — pass --apply to write changes\n")

    changed = 0
    skipped_set = 0
    errors = 0

    for status_dir in STATUS_DIRS:
        dir_path = QUEUE_ROOT / status_dir
        if not dir_path.is_dir():
            continue
        files = sorted(dir_path.glob("WRK-*.md"))
        for f in files:
            try:
                result = process_file(f, apply=args.apply,
                                      overwrite_existing=args.overwrite_all)
                if result:
                    print(result)
                    changed += 1
                else:
                    skipped_set += 1
            except Exception as exc:
                print(f"ERROR: {f.name}: {exc}", file=sys.stderr)
                errors += 1

    verb = "Written" if args.apply else "Would change"
    print(f"\n{verb}: {changed}  |  Already set (skipped): {skipped_set}  |  Errors: {errors}")

    if not args.apply and changed > 0:
        print("\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
