#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Fix category_dir_mismatch issues in SKILL.md frontmatter.

Updates the 'category' field to match the directory structure.
Dry-run by default; pass --apply to write changes.
"""
import re, sys, yaml
from pathlib import Path

SKILLS_ROOT = Path(".claude/skills")

def get_category_from_path(path: Path) -> str:
    rel = path.relative_to(SKILLS_ROOT)
    return rel.parts[0] if rel.parts else "unknown"

def fix_file(path: Path, apply: bool) -> dict | None:
    content = path.read_text()
    if not content.lstrip().startswith("---"):
        return None
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    
    fm_text = parts[1]
    body = parts[2]
    
    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None
    
    if not isinstance(meta, dict) or "category" not in meta:
        return None
    
    old_cat = str(meta["category"])
    new_cat = get_category_from_path(path)
    
    # Normalize for comparison
    old_norm = old_cat.lower().replace("-", "").replace("_", "")
    new_norm = new_cat.lower().replace("-", "").replace("_", "")
    
    if old_norm == new_norm or old_norm.startswith(new_norm) or new_norm.startswith(old_norm):
        return None  # Already matches
    
    # Replace category in frontmatter
    new_fm = re.sub(
        r'^(category:\s*).*$',
        f'\\1{new_cat}',
        fm_text,
        flags=re.MULTILINE
    )
    
    if new_fm == fm_text:
        return None
    
    result = {"path": str(path), "old": old_cat, "new": new_cat}
    
    if apply:
        new_content = f"---{new_fm}---{body}"
        path.write_text(new_content)
        result["applied"] = True
    
    return result

def main():
    apply = "--apply" in sys.argv
    skills = sorted(SKILLS_ROOT.rglob("SKILL.md"))
    fixes = []
    for s in skills:
        if "/_diverged/" in str(s) or "/_archive/" in str(s):
            continue
        fix = fix_file(s, apply)
        if fix:
            fixes.append(fix)
    
    mode = "APPLIED" if apply else "DRY-RUN"
    print(f"[{mode}] {len(fixes)} category mismatches found")
    for f in fixes[:20]:
        print(f"  {f['old']:30s} -> {f['new']:20s} | {f['path']}")
    if len(fixes) > 20:
        print(f"  ... and {len(fixes) - 20} more")

if __name__ == "__main__":
    main()
