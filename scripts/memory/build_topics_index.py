#!/usr/bin/env python3
"""build_topics_index.py — generate .claude/memory/topics/INDEX.md (#3189).

Problem-class-grouped index of the topic corpus so agents/humans stop grepping
~180 files to answer "what do we know about X". Stdlib-only (runs under any
provider). DETERMINISTIC: static header (no timestamp), files sorted by name —
two runs over the same corpus produce byte-identical output (no churn commits).
INDEX.md excludes ITSELF.

Class precedence: frontmatter `type:` if present, else filename-slug prefix
(feedback_/project_/reference_), else "other".

Usage:
  python3 build_topics_index.py [--topics-dir .claude/memory/topics] [--out <path>]
  (default --out is <topics-dir>/INDEX.md; use --check to print without writing)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

INDEX_NAME = "INDEX.md"
# Display order + headings for known classes; unknown classes fall to "other".
CLASS_ORDER = [
    ("feedback", "Feedback — execution lessons & hazards"),
    ("project", "Project — ongoing work & state"),
    ("reference", "Reference — external/pointer knowledge"),
    ("user", "User — profile & preferences"),
    ("memory", "Memory — meta"),
    ("other", "Other"),
]
_HEADER = (
    "<!-- MANAGED by scripts/memory/build_topics_index.py — do not hand-edit;\n"
    "     regenerate via bridge-hermes-claude.sh. Deterministic (no timestamp). -->\n\n"
    "# Topics index\n\n"
    "Problem-class grouped index of `.claude/memory/topics/`. Query with "
    "`scripts/memory/recall.py`.\n"
)


def _parse_frontmatter(text: str) -> dict:
    """Extract name/description/type from a leading YAML-ish `---` block.
    Tolerates leading `>` quote lines / blanks before the block; missing block -> {}."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (lines[i].strip() == "" or lines[i].lstrip().startswith(">")):
        i += 1
    if i >= len(lines) or lines[i].strip() != "---":
        return {}
    fm = {}
    for line in lines[i + 1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def _classify(fm: dict, stem: str) -> str:
    t = (fm.get("type") or "").strip().lower()
    if t:
        return t
    for prefix in ("feedback", "project", "reference"):
        if stem.startswith(prefix + "_") or stem.startswith(prefix + "-"):
            return prefix
    return "other"


def build_index(topics_dir) -> str:
    topics_dir = Path(topics_dir)
    groups: dict[str, list[tuple[str, str, str]]] = {}
    for f in sorted(topics_dir.glob("*.md"), key=lambda p: p.name):
        if f.name == INDEX_NAME:
            continue  # never index self
        fm = _parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        cls = _classify(fm, f.stem)
        title = fm.get("name") or f.stem
        desc = fm.get("description") or ""
        groups.setdefault(cls, []).append((f.name, title, desc))

    parts = [_HEADER]
    known = {c for c, _ in CLASS_ORDER}
    ordered = CLASS_ORDER + [(c, c.title()) for c in sorted(groups) if c not in known]
    for cls, heading in ordered:
        rows = groups.get(cls)
        if not rows:
            continue
        parts.append(f"\n## {heading} ({len(rows)})\n\n")
        for name, title, desc in rows:  # already name-sorted
            line = f"- [{title}]({name})"
            if desc:
                line += f" — {desc}"
            parts.append(line + "\n")
    return "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--topics-dir", default=".claude/memory/topics")
    ap.add_argument("--out", default=None, help="default: <topics-dir>/INDEX.md")
    ap.add_argument("--check", action="store_true", help="print to stdout, do not write")
    args = ap.parse_args()
    content = build_index(args.topics_dir)
    if args.check:
        sys.stdout.write(content)
        return 0
    out = Path(args.out) if args.out else Path(args.topics_dir) / INDEX_NAME
    out.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
