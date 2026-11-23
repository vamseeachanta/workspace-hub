#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""generate_skills_index.py — (re)build .claude/skills-index.yaml from the skills tree.

The index is the CURATED first-class-skill catalog consumed by humans and by
`scripts/curation/audit_skill_currency.py` (which grades `index_stale` when any index
`path:` no longer exists in the committed tree). It had rotted: 202 of 224 entries pointed
at an old tree layout (last auto-gen 2026-01-21), so this regenerates it cleanly.

Inclusion rule (a path is a "first-class skill" iff ALL hold):
  1. Tracked in the COMMITTED tree (`git ls-tree -r HEAD .claude/skills`). This is the exact
     basis the audit compares against, so the emitted paths are a guaranteed subset → no
     dangling entries. (Working-tree-only / untracked SKILL.md are intentionally excluded.)
  2. Canonical skill location — exactly one category dir + one skill dir
     (`.claude/skills/<category>/<skill>/SKILL.md`) OR a top-level skill that is its own
     category (`.claude/skills/<skill>/SKILL.md`). Deeper SKILL.md files are bundled
     sub-skills / resources of a parent skill, not first-class entries.
  3. YAML frontmatter declares BOTH `name:` and `description:` (a real, addressable skill).
  4. Not under the `_archive/` retired-skills namespace.

Grouping is by the TOP-LEVEL category dir under `.claude/skills/`. Categories and the skills
within each are sorted alphabetically. Output format matches the legacy index exactly:

    # Skills Index for workspace-hub
    # Auto-generated from .claude/skills/
    # Last updated: <YYYY-MM-DD>

    categories:
    - name: <category>
      count: <n>
      skills:
      - name: <skill>
        description: <desc>
        path: .claude/skills/<...>/SKILL.md
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SKILLS_PREFIX = ".claude/skills"
SKILLS_INDEX = REPO / ".claude" / "skills-index.yaml"
ARCHIVE_NS = "_archive"


def committed_skill_md(repo: Path) -> list[str]:
    """SKILL.md paths tracked in HEAD under .claude/skills (repo-root-relative, POSIX)."""
    r = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD", SKILLS_PREFIX],
        capture_output=True, text=True, timeout=60, check=True,
    )
    return [ln for ln in r.stdout.splitlines() if ln.endswith("/SKILL.md")]


def is_first_class(rel_path: str) -> bool:
    """True for `.claude/skills/<cat>/<skill>/SKILL.md` or `.claude/skills/<skill>/SKILL.md`."""
    parts = rel_path.split("/")
    # parts[:2] == ['.claude', 'skills']; trailing is 'SKILL.md'
    inner = parts[2:-1]  # components between the prefix and SKILL.md
    if not (1 <= len(inner) <= 2):
        return False
    return inner[0] != ARCHIVE_NS


def parse_frontmatter(text: str) -> dict:
    """Return the leading `--- ... ---` YAML block as a dict (empty dict if absent/invalid)."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def build_categories(repo: Path) -> list[dict]:
    cats: dict[str, list[dict]] = {}
    for rel in committed_skill_md(repo):
        if not is_first_class(rel):
            continue
        fm = parse_frontmatter((repo / rel).read_text(encoding="utf-8", errors="replace"))
        name = str(fm.get("name", "")).strip()
        desc = str(fm.get("description", "")).strip()
        if not name or not desc:
            continue
        category = rel.split("/")[2]  # top-level dir under .claude/skills/
        cats.setdefault(category, []).append({"name": name, "description": desc, "path": rel})
    out = []
    for category in sorted(cats):
        skills = sorted(cats[category], key=lambda s: s["name"])
        out.append({"name": category, "count": len(skills), "skills": skills})
    return out


def render(categories: list[dict]) -> str:
    header = (
        "# Skills Index for workspace-hub\n"
        "# Auto-generated from .claude/skills/\n"
        f"# Last updated: {date.today().isoformat()}\n\n"
    )
    body = yaml.safe_dump(
        {"categories": categories},
        sort_keys=False, default_flow_style=False, allow_unicode=True, width=80,
    )
    return header + body


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate .claude/skills-index.yaml")
    ap.add_argument("--stdout", action="store_true", help="print to stdout, do not write")
    ap.add_argument("--repo", default=str(REPO), help="repo root (default: inferred)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    categories = build_categories(repo)
    text = render(categories)
    total = sum(c["count"] for c in categories)
    if a.stdout:
        sys.stdout.write(text)
    else:
        (repo / ".claude" / "skills-index.yaml").write_text(text, encoding="utf-8")
        print(f"wrote {repo / '.claude' / 'skills-index.yaml'}: "
              f"{len(categories)} categories, {total} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
