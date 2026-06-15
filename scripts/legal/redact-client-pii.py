#!/usr/bin/env python3
"""Apply a client->codename redaction map to a set of files.

Part of the workspace-hub public-repo PII remediation (epic #3095, sub-issue #3097).

DESIGN: this script is intentionally **name-agnostic**. It contains no client
identifiers. The real client names and their codenames live ONLY in a private
map file (never committed to a public repo — that would re-introduce the leak,
the same paradox as the legal deny-list). Pass the private map via --map.

Map schema (YAML):
    version: 1
    rules:
      - {pattern: '<python-regex>', replacement: '<codename>', word_bound: false}
      ...
Rules are applied IN ORDER (list each more-specific pattern before a shorter
one it shares a prefix with). All patterns match case-insensitively. When
word_bound is true the pattern is wrapped in \\b...\\b to avoid substring
collisions (e.g. a short client token appearing inside an unrelated word).

Usage:
    uv run python scripts/legal/redact-client-pii.py --map <private.yaml> --files <list.txt>
    uv run python scripts/legal/redact-client-pii.py --map <private.yaml> --dry-run path1 path2 ...
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Rule:
    regex: "re.Pattern[str]"
    replacement: str
    note: str


def load_rules(map_path: Path) -> list[Rule]:
    data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    rules: list[Rule] = []
    for raw in data.get("rules", []):
        pat = raw["pattern"]
        if raw.get("word_bound"):
            # Alpha-boundary: match unless flanked by ASCII letters. This protects
            # a short token from matching inside a larger *word* (e.g. a token inside
            # 'blockMeshDict') while STILL matching when the token abuts digits,
            # underscores, or punctuation (e.g. 'Tokenco7000', 'tokenco_vessels',
            # '_Tokenco[1]') — cases plain \b...\b silently misses because '_' is a
            # regex word char.
            pat = rf"(?<![A-Za-z]){pat}(?![A-Za-z])"
        rules.append(
            Rule(
                regex=re.compile(pat, re.IGNORECASE),
                replacement=raw["replacement"],
                note=raw.get("note", ""),
            )
        )
    if not rules:
        sys.exit(f"error: no rules found in {map_path}")
    return rules


def redact_text(text: str, rules: list[Rule]) -> tuple[str, int]:
    """Apply all rules in order. Returns (new_text, total_replacements)."""
    total = 0
    for rule in rules:
        text, n = rule.regex.subn(rule.replacement, text)
        total += n
    return text, total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map", required=True, type=Path, help="private YAML codename map")
    ap.add_argument("--files", type=Path, help="file containing newline-separated paths to redact")
    ap.add_argument("paths", nargs="*", help="paths to redact (alternative to --files)")
    ap.add_argument("--dry-run", action="store_true", help="report changes, write nothing")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="repo root for relative paths")
    args = ap.parse_args()

    rules = load_rules(args.map)

    targets: list[str] = list(args.paths)
    if args.files:
        targets += [ln.strip() for ln in args.files.read_text().splitlines() if ln.strip()]
    if not targets:
        sys.exit("error: no target files given (use --files or positional paths)")

    # Expand any directory targets into their contained files (recursive).
    expanded: list[str] = []
    for rel in targets:
        fp = args.root / rel
        if fp.is_dir():
            expanded += [str(p.relative_to(args.root)) for p in sorted(fp.rglob("*")) if p.is_file()]
        else:
            expanded.append(rel)

    changed_files = 0
    total_repl = 0
    skipped = 0
    for rel in expanded:
        fp = args.root / rel
        if not fp.is_file():
            continue
        try:
            text = fp.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped += 1
            continue
        new_text, n = redact_text(text, rules)
        if n:
            total_repl += n
            changed_files += 1
            if not args.dry_run:
                fp.write_text(new_text, encoding="utf-8")
            print(f"{'(dry) ' if args.dry_run else ''}{rel}: {n} replacement(s)")

    print(
        f"\n{'DRY-RUN: ' if args.dry_run else ''}files changed: {changed_files}, "
        f"total replacements: {total_repl}, binary/unreadable skipped: {skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
