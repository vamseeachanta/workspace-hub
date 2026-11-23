#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Fix unresolved related_skills references in SKILL.md frontmatter.

Builds an index of all skill names, then removes references to skills
that don't exist. Dry-run by default; pass --apply to write changes.
"""
import sys
import yaml
from pathlib import Path

SKILLS_ROOT = Path(".claude/skills")


def build_skill_index(root: Path) -> dict[str, Path]:
    """Map skill name -> SKILL.md path for all canonical skills."""
    index: dict[str, Path] = {}
    for p in sorted(root.rglob("SKILL.md")):
        if "/_diverged/" in str(p) or "/_archive/" in str(p):
            continue
        content = p.read_text()
        if not content.lstrip().startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            meta = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            continue
        if isinstance(meta, dict) and "name" in meta:
            index[str(meta["name"])] = p
    return index


def find_unresolved_refs(
    root: Path, index: dict[str, Path]
) -> list[dict]:
    """Find skills with related_skills entries not in the index."""
    results = []
    for p in sorted(root.rglob("SKILL.md")):
        if "/_diverged/" in str(p) or "/_archive/" in str(p):
            continue
        content = p.read_text()
        if not content.lstrip().startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            meta = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            continue
        if not isinstance(meta, dict):
            continue
        refs = meta.get("related_skills", [])
        if not isinstance(refs, list):
            continue
        unresolved = [r for r in refs if str(r) not in index]
        if unresolved:
            results.append({
                "skill": meta.get("name", "unknown"),
                "path": str(p),
                "unresolved": unresolved,
                "valid": [r for r in refs if str(r) in index],
            })
    return results


def fix_ref(path: Path, to_remove: list[str], apply: bool) -> dict:
    """Remove unresolved refs from a single SKILL.md."""
    content = path.read_text()
    parts = content.split("---", 2)
    fm_text = parts[1]
    body = parts[2]

    meta = yaml.safe_load(fm_text)
    old_refs = meta.get("related_skills", [])
    new_refs = [r for r in old_refs if str(r) not in to_remove]
    removed = [r for r in old_refs if str(r) in to_remove]

    result = {
        "path": str(path),
        "removed": removed,
        "remaining": new_refs,
    }

    if apply and removed:
        if new_refs:
            meta["related_skills"] = new_refs
        else:
            del meta["related_skills"]
        new_fm = yaml.dump(
            meta, default_flow_style=False, sort_keys=False
        )
        path.write_text(f"---\n{new_fm}---{body}")
        result["applied"] = True

    return result


def main():
    apply = "--apply" in sys.argv
    root = SKILLS_ROOT
    if "--skill-dir" in sys.argv:
        idx = sys.argv.index("--skill-dir")
        root = Path(sys.argv[idx + 1])

    index = build_skill_index(root)
    unresolved = find_unresolved_refs(root, index)

    if not unresolved:
        print("No unresolved related_skills references found.")
        return

    mode = "APPLIED" if apply else "DRY-RUN"
    total_removed = 0
    for entry in unresolved:
        result = fix_ref(
            Path(entry["path"]), entry["unresolved"], apply
        )
        total_removed += len(result["removed"])
        print(
            f"  [{mode}] {entry['skill']:40s} "
            f"remove: {result['removed']}"
        )

    print(
        f"\n[{mode}] {len(unresolved)} skills "
        f"with {total_removed} unresolved refs"
    )


if __name__ == "__main__":
    main()
