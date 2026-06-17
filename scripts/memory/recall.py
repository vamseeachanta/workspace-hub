#!/usr/bin/env python3
"""recall.py — provider-neutral query over the topic memory corpus (#3189).

Stdlib-only so Claude / Codex / agy all invoke ONE mechanism and get the SAME
result. DETERMINISTIC ordering (score desc, then filename) so the result set is
identical regardless of invoking provider.

Usage:
  python3 recall.py "git worktree race"            # keyword(s)
  python3 recall.py worktree --class feedback --limit 10
  python3 recall.py --kw stash --kw rebase         # repeatable keywords
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_topics_index import _parse_frontmatter, _classify, INDEX_NAME  # noqa: E402


def recall(topics_dir, keywords, cls=None, limit=20):
    topics_dir = Path(topics_dir)
    kws = [k.lower() for k in keywords if k]
    results = []
    for f in topics_dir.glob("*.md"):
        if f.name == INDEX_NAME:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        fm = _parse_frontmatter(text)
        if cls and _classify(fm, f.stem) != cls.lower():
            continue
        hay = (fm.get("name", "") + "\n" + fm.get("description", "") + "\n" + text).lower()
        score = sum(hay.count(k) for k in kws)
        if score:
            results.append((score, f.name, fm.get("name") or f.stem, fm.get("description", "")))
    # deterministic: highest score first, then filename (stable across providers)
    results.sort(key=lambda r: (-r[0], r[1]))
    return results[:limit]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", nargs="*", help="keyword(s)")
    ap.add_argument("--kw", action="append", default=[], help="keyword (repeatable)")
    ap.add_argument("--class", dest="cls", default=None, help="filter by class (feedback/project/...)")
    ap.add_argument("--topics-dir", default=".claude/memory/topics")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    keywords = list(args.query) + list(args.kw)
    if not keywords:
        ap.error("provide at least one keyword (positional or --kw)")
    hits = recall(args.topics_dir, keywords, cls=args.cls, limit=args.limit)
    if not hits:
        print("(no matches)")
        return 0
    for score, name, title, desc in hits:
        print(f"[{score:>3}] {title}  ({name})")
        if desc:
            print(f"      {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
