#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Detect skill rot: broken references, missing scripts, orphans, stale links.

Scans all SKILL.md files under .claude/skills/ (excluding _archive/) and checks:
  a. related_skills / see_also → target skill name exists in the skill index
  b. scripts: list → each script file exists on disk
  c. File-path references in body text → file exists on disk
  d. Orphan detection: skills with 0 inbound refs from any other skill
  e. Stale section references: body refs to '## Section' in another skill

Auto-fixes safe cases (with --apply):
  - Removes broken related_skills/see_also entries

Reports everything else without modification.

Output: JSON report to stdout + persisted to .claude/state/skill-rot-report/YYYY-MM-DD.json

Exit 0 always (non-blocking for nightly cron).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SKILLS_ROOT = Path(".claude/skills")
REPORT_DIR = Path(".claude/state/skill-rot-report")

# Patterns for file-path references in body text
FILE_PATH_PATTERNS = [
    re.compile(r"(?:^|\s|`)(scripts/[^\s`\"'>\)]+)", re.MULTILINE),
    re.compile(r"(?:^|\s|`)(\.claude/skills/[^\s`\"'>\)]+)", re.MULTILINE),
    re.compile(r"(?:^|\s|`)(\.planning/[^\s`\"'>\)]+)", re.MULTILINE),
    re.compile(r"(?:^|\s|`)(\.claude/state/[^\s`\"'>\)]+)", re.MULTILINE),
]

# Pattern for section references to other skills: e.g. "see skill-name ## Section Name"
SECTION_REF_PATTERN = re.compile(
    r"(?:see|refer\s+to|in)\s+[`\"]?([a-z][a-z0-9_-]+)[`\"]?\s+##\s+([^\n`\"]+)",
    re.IGNORECASE,
)


def should_skip(path: Path) -> bool:
    """Skip _archive and _diverged directories."""
    s = str(path)
    return "/_archive/" in s or "\\_archive\\" in s or "/_diverged/" in s or "\\_diverged\\" in s


def parse_skill(path: Path) -> tuple[dict | None, str, str]:
    """Parse a SKILL.md into (frontmatter_dict, frontmatter_text, body).

    Returns (None, "", "") on parse failure.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, "", ""

    if not content.lstrip().startswith("---"):
        return None, "", ""

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "", ""

    fm_text = parts[1]
    body = parts[2]

    try:
        meta = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, "", ""

    if not isinstance(meta, dict):
        return None, "", ""

    return meta, fm_text, body


def build_skill_index(root: Path) -> dict[str, Path]:
    """Map skill name -> SKILL.md path for all canonical skills."""
    index: dict[str, Path] = {}
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, _ = parse_skill(p)
        if meta and "name" in meta:
            index[str(meta["name"])] = p
    return index


def build_section_index(root: Path) -> dict[str, set[str]]:
    """Map skill name -> set of '## Section Name' headings in its body."""
    sections: dict[str, set[str]] = {}
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, body = parse_skill(p)
        if not meta or "name" not in meta:
            continue
        name = str(meta["name"])
        headings = set()
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("## "):
                headings.add(stripped[3:].strip())
        sections[name] = headings
    return sections


def check_broken_refs(
    root: Path, index: dict[str, Path]
) -> list[dict]:
    """Find skills with related_skills/see_also entries not in the index."""
    results = []
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, _ = parse_skill(p)
        if not meta:
            continue

        skill_name = str(meta.get("name", str(p)))
        broken = []

        for field in ("related_skills", "see_also"):
            refs = meta.get(field, [])
            if not isinstance(refs, list):
                continue
            for r in refs:
                r_str = str(r)
                if r_str and r_str not in index:
                    broken.append({"field": field, "ref": r_str})

        if broken:
            results.append({
                "skill": skill_name,
                "path": str(p),
                "broken": broken,
            })

    return results


def check_broken_scripts(
    root: Path, index: dict[str, Path]
) -> list[dict]:
    """Find skills whose scripts: entries point to non-existent files."""
    results = []
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, _ = parse_skill(p)
        if not meta:
            continue

        scripts = meta.get("scripts", [])
        if not isinstance(scripts, list) or not scripts:
            continue

        skill_name = str(meta.get("name", str(p)))
        missing = []
        for s in scripts:
            s_str = str(s).strip()
            if s_str and not Path(s_str).exists():
                missing.append(s_str)

        if missing:
            results.append({
                "skill": skill_name,
                "path": str(p),
                "missing_scripts": missing,
            })

    return results


def check_broken_file_paths(root: Path) -> list[dict]:
    """Find file-path references in body text that don't exist on disk."""
    results = []
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, body = parse_skill(p)
        if not meta:
            continue

        skill_name = str(meta.get("name", str(p)))
        missing = []
        seen = set()

        for pattern in FILE_PATH_PATTERNS:
            for match in pattern.finditer(body):
                ref = match.group(1).rstrip(".,;:)")
                if ref in seen:
                    continue
                seen.add(ref)
                # Skip URLs and template variables
                if "http" in ref or "{{" in ref or "{%" in ref:
                    continue
                # Skip if it looks like a generic example/placeholder
                if "/path/" in ref or "/example" in ref:
                    continue
                if not Path(ref).exists():
                    missing.append(ref)

        if missing:
            results.append({
                "skill": skill_name,
                "path": str(p),
                "missing_paths": missing,
            })

    return results


def check_orphans(
    root: Path, index: dict[str, Path]
) -> list[dict]:
    """Find skills with zero inbound references from other skills."""
    # Build inbound reference counts
    inbound: dict[str, int] = {name: 0 for name in index}

    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, _ = parse_skill(p)
        if not meta:
            continue

        source = str(meta.get("name", ""))
        for field in ("related_skills", "see_also"):
            refs = meta.get(field, [])
            if not isinstance(refs, list):
                continue
            for r in refs:
                r_str = str(r)
                if r_str in inbound and r_str != source:
                    inbound[r_str] += 1

    orphans = []
    for name, count in sorted(inbound.items()):
        if count == 0:
            orphans.append({
                "skill": name,
                "path": str(index[name]),
                "inbound_refs": 0,
            })

    return orphans


def check_stale_sections(
    root: Path, index: dict[str, Path], sections: dict[str, set[str]]
) -> list[dict]:
    """Find body references to '## Section Name' in another skill where that section doesn't exist."""
    results = []
    for p in sorted(root.rglob("SKILL.md")):
        if should_skip(p):
            continue
        meta, _, body = parse_skill(p)
        if not meta:
            continue

        skill_name = str(meta.get("name", str(p)))
        stale = []

        for match in SECTION_REF_PATTERN.finditer(body):
            target_skill = match.group(1)
            target_section = match.group(2).strip()

            # Only check if the target skill exists in the index
            if target_skill not in index:
                continue
            if target_skill == skill_name:
                continue

            target_sections = sections.get(target_skill, set())
            if target_section not in target_sections:
                stale.append({
                    "target_skill": target_skill,
                    "section": target_section,
                })

        if stale:
            results.append({
                "skill": skill_name,
                "path": str(p),
                "stale_sections": stale,
            })

    return results


def fix_broken_refs(path: Path, broken_entries: list[dict], apply: bool) -> dict:
    """Remove broken related_skills/see_also entries from a single SKILL.md."""
    content = path.read_text(encoding="utf-8", errors="replace")
    parts = content.split("---", 2)
    body = parts[2]

    meta = yaml.safe_load(parts[1])
    removed = []

    # Group broken refs by field
    broken_by_field: dict[str, set[str]] = {}
    for entry in broken_entries:
        broken_by_field.setdefault(entry["field"], set()).add(entry["ref"])

    for field, bad_refs in broken_by_field.items():
        old_refs = meta.get(field, [])
        if not isinstance(old_refs, list):
            continue
        new_refs = [r for r in old_refs if str(r) not in bad_refs]
        removed_from_field = [r for r in old_refs if str(r) in bad_refs]
        removed.extend({"field": field, "ref": str(r)} for r in removed_from_field)

        if new_refs:
            meta[field] = new_refs
        elif field in meta:
            del meta[field]

    result = {
        "path": str(path),
        "removed": removed,
        "applied": False,
    }

    if apply and removed:
        new_fm = yaml.dump(meta, default_flow_style=False, sort_keys=False)
        path.write_text(f"---\n{new_fm}---{body}")
        result["applied"] = True

    return result


def main() -> None:
    try:
        _main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(0)  # Non-blocking


def _main() -> None:
    apply = "--apply" in sys.argv
    root = SKILLS_ROOT

    if "--skill-dir" in sys.argv:
        idx = sys.argv.index("--skill-dir")
        root = Path(sys.argv[idx + 1])

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[skill-rot] Mode: {mode}")
    print(f"[skill-rot] Scanning: {root}")

    # Build indices
    index = build_skill_index(root)
    sections = build_section_index(root)
    print(f"[skill-rot] Indexed {len(index)} skills, {sum(len(v) for v in sections.values())} sections")

    # Run all checks
    broken_refs = check_broken_refs(root, index)
    broken_scripts = check_broken_scripts(root, index)
    broken_file_paths = check_broken_file_paths(root)
    orphans = check_orphans(root, index)
    stale_sections = check_stale_sections(root, index, sections)

    # Auto-fix broken refs
    fixes = []
    if broken_refs:
        for entry in broken_refs:
            result = fix_broken_refs(
                Path(entry["path"]), entry["broken"], apply
            )
            fixes.append(result)
            status = "FIXED" if result["applied"] else "WOULD-FIX"
            print(f"  [{status}] {entry['skill']}: {[b['ref'] for b in entry['broken']]}")

    # Report broken scripts (flag only)
    if broken_scripts:
        print(f"\n[skill-rot] Broken script references ({len(broken_scripts)}):")
        for entry in broken_scripts:
            print(f"  [FLAG] {entry['skill']}: {entry['missing_scripts']}")

    # Report broken file paths (flag only)
    if broken_file_paths:
        print(f"\n[skill-rot] Broken file-path references ({len(broken_file_paths)}):")
        for entry in broken_file_paths:
            print(f"  [FLAG] {entry['skill']}: {entry['missing_paths']}")

    # Report orphans (informational)
    if orphans:
        print(f"\n[skill-rot] Orphan skills with 0 inbound refs ({len(orphans)}):")
        # Only show first 20 to avoid flooding
        for entry in orphans[:20]:
            print(f"  [INFO] {entry['skill']}")
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more")

    # Report stale sections
    if stale_sections:
        print(f"\n[skill-rot] Stale section references ({len(stale_sections)}):")
        for entry in stale_sections:
            for s in entry["stale_sections"]:
                print(f"  [FLAG] {entry['skill']} -> {s['target_skill']} ## {s['section']}")

    # Build report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "skills_indexed": len(index),
        "broken_refs": broken_refs,
        "broken_refs_fixed": len(fixes),
        "broken_scripts": broken_scripts,
        "broken_file_paths": broken_file_paths,
        "orphans": orphans,
        "stale_sections": stale_sections,
        "summary": {
            "broken_refs_count": sum(len(e["broken"]) for e in broken_refs),
            "broken_scripts_count": sum(len(e["missing_scripts"]) for e in broken_scripts),
            "broken_file_paths_count": sum(len(e["missing_paths"]) for e in broken_file_paths),
            "orphan_count": len(orphans),
            "stale_section_count": sum(len(e["stale_sections"]) for e in stale_sections),
        },
    }

    # Summary line
    s = report["summary"]
    print(f"\n[skill-rot] Summary: "
          f"{s['broken_refs_count']} broken refs, "
          f"{s['broken_scripts_count']} broken scripts, "
          f"{s['broken_file_paths_count']} broken file paths, "
          f"{s['orphan_count']} orphans, "
          f"{s['stale_section_count']} stale sections")

    # Write report to disk
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"{date_str}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"[skill-rot] Report written to {report_path}")

    # Also print JSON to stdout for piping
    print("\n" + json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
