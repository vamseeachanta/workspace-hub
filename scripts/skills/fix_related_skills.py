#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Fix broken related_skills references in SKILL.md frontmatter.

Builds a name index of all skills, then for each broken reference:
1. Strips path prefixes (e.g. workspace-hub/session-start -> session-start)
2. Removes /SKILL suffix
3. Tries known alias mappings
4. Removes truly dead references

Usage:
    uv run --no-project python scripts/skills/fix_related_skills.py          # dry-run
    uv run --no-project python scripts/skills/fix_related_skills.py --apply  # write changes
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


SKILLS_ROOT = Path(".claude/skills")

# Manual alias map for refs that can't be resolved by suffix stripping
ALIASES: dict[str, str | None] = {
    "session-start-routine": "session-start",
    "knowledge": "knowledge-management",
    "testing": "testing-tdd-london",
    "reflect": "claude-reflect",
    "insights": None,  # no matching skill exists
    "knowledge-base-system": "knowledge-manager",
    "skills-knowledge-graph": "knowledge-manager",
    "repository-health-analyzer": "repo-capability-map",
    "swarm-worker": "git-worktree-workflow",
    # These have no equivalent — remove
    "kubernetes": None,
    "gatsby": None,
    "latex": None,
    "reveal-js": None,
    "azure-functions": None,
    "content-creation": None,
    "webhook-automation": None,
    "roadmap-management": None,
    "parallel-dispatch": None,
    "pillow": None,
    "reportlab": None,
    "markdown-documentation": None,
    "sparc:designer": None,
    "planning": None,
}


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return None, content
    end = content.find("---", 3)
    if end < 0:
        return None, content
    try:
        meta = yaml.safe_load(content[3:end])
        return meta, content[end + 3:]
    except yaml.YAMLError:
        return None, content


def build_name_index_from_skills(skills_root: Path | None = None) -> dict[str, Path]:
    """Build mapping from skill name -> path."""
    root = skills_root or SKILLS_ROOT
    index: dict[str, Path] = {}
    for path in sorted(root.rglob("SKILL.md")):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta, _ = parse_frontmatter(content)
        if meta and "name" in meta:
            index[str(meta["name"])] = path
        else:
            m = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            if m:
                slug = re.sub(r"[^a-z0-9\-]", "", m.group(1).lower().replace(" ", "-"))
                index[slug] = path
    return index


def resolve_reference(ref: str, name_index: dict[str, Path]) -> str | None:
    """Resolve a broken reference to a valid skill name, or None to remove.

    Returns:
        str: valid skill name to replace with
        None: reference should be removed
    """
    ref = ref.strip()

    # Already valid
    if ref in name_index:
        return ref

    # Check manual aliases first
    if ref in ALIASES:
        target = ALIASES[ref]
        if target is None:
            return None
        if target in name_index:
            return target

    # Strip /SKILL suffix
    clean = re.sub(r"/SKILL$", "", ref)
    if clean in name_index:
        return clean

    # Path-style: take last segment
    if "/" in clean:
        last_segment = clean.rsplit("/", 1)[-1]
        if last_segment in name_index:
            return last_segment
        # Check aliases for the stripped segment
        if last_segment in ALIASES:
            target = ALIASES[last_segment]
            if target is None:
                return None
            if target in name_index:
                return target

    # Colon-style (sparc:designer) — not a valid related_skills format
    if ":" in ref:
        return None

    # Prefix match: ref is a prefix of exactly one valid name
    prefix_matches = [name for name in name_index if name.startswith(ref + "-")]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    # No match found — remove
    return None


def compute_fixes(
    refs: list[str], name_index: dict[str, Path]
) -> dict[str, str | None]:
    """Compute fixes for a list of references.

    Returns dict mapping broken_ref -> resolved_name (or None to remove).
    Only includes refs that need changing.
    """
    fixes: dict[str, str | None] = {}
    for ref in refs:
        ref_str = str(ref).strip()
        if ref_str in name_index:
            continue  # already valid
        resolved = resolve_reference(ref_str, name_index)
        fixes[ref_str] = resolved
    return fixes


def apply_fixes_to_file(path: Path, name_index: dict[str, Path], dry_run: bool = True) -> list[str]:
    """Fix related_skills in a single SKILL.md file.

    Returns list of change descriptions.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    meta, body = parse_frontmatter(content)
    if not meta:
        return []

    related = meta.get("related_skills", [])
    if not related or not isinstance(related, list):
        return []

    changes: list[str] = []
    new_related: list[str] = []

    for ref in related:
        ref_str = str(ref).strip()
        if ref_str in name_index:
            new_related.append(ref_str)
            continue

        resolved = resolve_reference(ref_str, name_index)
        if resolved is None:
            changes.append(f"  REMOVE: {ref_str}")
        elif resolved != ref_str:
            changes.append(f"  FIX: {ref_str} -> {resolved}")
            # Avoid duplicates
            if resolved not in new_related:
                new_related.append(resolved)
        else:
            new_related.append(ref_str)

    if not changes:
        return []

    if not dry_run:
        meta["related_skills"] = new_related
        # Rebuild file content
        front = yaml.dump(meta, default_flow_style=False, sort_keys=False, allow_unicode=True)
        new_content = f"---\n{front}---{body}"
        path.write_text(new_content, encoding="utf-8")

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix broken related_skills references")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    parser.add_argument("--skills-root", type=Path, default=SKILLS_ROOT)
    args = parser.parse_args()

    name_index = build_name_index_from_skills(args.skills_root)
    print(f"Name index: {len(name_index)} skills", file=sys.stderr)

    all_skills = sorted(args.skills_root.rglob("SKILL.md"))
    total_fixes = 0
    total_removals = 0

    for path in all_skills:
        changes = apply_fixes_to_file(path, name_index, dry_run=not args.apply)
        if changes:
            print(f"\n{path}:")
            for c in changes:
                print(c)
                if c.startswith("  FIX:"):
                    total_fixes += 1
                elif c.startswith("  REMOVE:"):
                    total_removals += 1

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] {total_fixes} fixed, {total_removals} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
