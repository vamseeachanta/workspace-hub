#!/usr/bin/env python3
"""audit-prose-operations.py — Scan skills/rules/docs for inline prose operations.

Unlike identify_script_candidates.py (whole-skill classification), this finds
specific operations within step-by-step content that violate the 25% Repetition Rule.

Pattern taxonomy (6 categories):
  count_ops      — count the, tally, how many, number of
  iteration_ops  — for each (file|repo|item|step), iterate over, loop through
  parse_ops      — parse the (yaml|json|md), read and extract, extract the field
  generate_ops   — generate the yaml, build the list, construct the json by hand
  threshold_ops  — check if.*greater, compare.*percent, above.*threshold
  filter_ops     — filter by, select only, narrow to

Output: TSV summary + Markdown report.
"""
import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Pattern taxonomy — (category, compiled_regex)
# ---------------------------------------------------------------------------
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("count_ops",     re.compile(r'\bcount the\b|\btally\b|\bhow many\b|\bnumber of\b', re.IGNORECASE)),
    ("iteration_ops", re.compile(r'\bfor each\s+(file|repo|item|step|directory|entry)\b|\biterate over\b|\bloop through\b', re.IGNORECASE)),
    ("parse_ops",     re.compile(r'\bparse the\s+(yaml|json|md|markdown|config|file)\b|\bread and extract\b|\bextract the field\b', re.IGNORECASE)),
    ("generate_ops",  re.compile(r'\bgenerate the\s+(yaml|json)\b|\bbuild the list\b|\bconstruct the\s+(json|yaml)\b|\bby hand\b', re.IGNORECASE)),
    ("threshold_ops", re.compile(r'\bcheck if\b.{0,30}\bgreater\b|\bcompare\b.{0,30}\bpercent\b|\babove\b.{0,20}\bthreshold\b', re.IGNORECASE)),
    ("filter_ops",    re.compile(r'\bfilter by\b|\bselect only\b|\bnarrow to\b', re.IGNORECASE)),
]

# ---------------------------------------------------------------------------
# Known existing scripts that cover certain operations (for classification)
# ---------------------------------------------------------------------------
KNOWN_SCRIPTS: dict[str, str] = {
    "quota":            "scripts/session/quota-status.sh",
    "snapshot":         "scripts/session/snapshot-age.sh",
    "whats-next":       "scripts/work-queue/whats-next.sh",
    "infer-category":   "scripts/work-queue/infer-category.py",
    "identify-script":  "scripts/skills/identify-script-candidates.sh",
    "legal-scan":       "scripts/legal/legal-sanity-scan.sh",
}


def strip_code_fences(text: str) -> str:
    """Replace content inside ```...``` blocks with blank lines to preserve line numbers."""
    return re.sub(r'```[^\n]*\n.*?```', lambda m: '\n' * m.group(0).count('\n'), text, flags=re.DOTALL)


def classify_operation(line: str, category: str) -> str:
    """Classify an operation as existing-script, new-one-liner, new-utility, or llm-only."""
    line_lower = line.lower()
    for key, path in KNOWN_SCRIPTS.items():
        if key in line_lower and (REPO_ROOT / path).exists():
            return "existing-script"
    if category in ("count_ops", "filter_ops"):
        return "new-one-liner"
    if category in ("iteration_ops", "parse_ops", "generate_ops", "threshold_ops"):
        return "new-utility"
    return "llm-only"


def scan_file(path: Path) -> list[dict]:
    """Scan a single file for prose operation patterns."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    clean = strip_code_fences(text)
    hits = []
    for i, line in enumerate(clean.splitlines(), start=1):
        for category, pattern in PATTERNS:
            m = pattern.search(line)
            if m:
                hits.append({
                    "file": str(path),
                    "line": i,
                    "category": category,
                    "matched_text": m.group(0)[:60],
                    "classification": classify_operation(line, category),
                })
    return hits


def scan_paths(paths: list[Path]) -> list[dict]:
    """Scan all .md files under given paths."""
    all_hits: list[dict] = []
    for root in paths:
        if not root.exists():
            continue
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in ("_archive", "_diverged", "__pycache__")]
            for fname in files:
                if fname.endswith(".md"):
                    all_hits.extend(scan_file(Path(dirpath) / fname))
    return all_hits


def write_markdown(hits: list[dict], output_path: Path) -> None:
    lines = [
        "# Patterns Audit — 25% Repetition Rule",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}  ",
        f"Total flagged operations: {len(hits)}",
        "",
        "## Flagged Items",
        "",
        "| # | File | Line | Category | Matched Text | Classification |",
        "|---|------|------|----------|--------------|----------------|",
    ]
    for i, h in enumerate(hits, start=1):
        rel = Path(h["file"]).relative_to(REPO_ROOT) if h["file"].startswith(str(REPO_ROOT)) else h["file"]
        lines.append(
            f"| {i} | `{rel}` | {h['line']} | `{h['category']}` "
            f"| {h['matched_text']} | {h['classification']} |"
        )

    # Summary by category
    from collections import Counter
    cat_counts = Counter(h["category"] for h in hits)
    cls_counts = Counter(h["classification"] for h in hits)
    lines += [
        "",
        "## Summary by Category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat, cnt in sorted(cat_counts.items()):
        lines.append(f"| `{cat}` | {cnt} |")

    lines += [
        "",
        "## Summary by Classification",
        "",
        "| Classification | Count |",
        "|----------------|-------|",
    ]
    for cls, cnt in sorted(cls_counts.items()):
        lines.append(f"| {cls} | {cnt} |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.rename(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit prose operations in skills/rules/docs.")
    parser.add_argument("--path", action="append", dest="paths",
                        help="Directory to scan (may be given multiple times)")
    parser.add_argument("--output", default=str(REPO_ROOT / "docs" / "patterns-audit-25pct-rule.md"),
                        help="Output Markdown report path")
    args = parser.parse_args()

    if args.paths:
        scan_roots = [Path(p) for p in args.paths]
    else:
        scan_roots = [
            REPO_ROOT / ".claude" / "skills",
            REPO_ROOT / ".claude" / "rules",
            REPO_ROOT / ".claude" / "docs",
        ]

    print(f"Scanning {len(scan_roots)} path(s) for prose operation patterns...")
    hits = scan_paths(scan_roots)
    print(f"  Found {len(hits)} flagged operations")

    from collections import Counter
    for cat, cnt in sorted(Counter(h["category"] for h in hits).items()):
        print(f"  {cat}: {cnt}")

    if args.output and args.output != "/dev/null":
        write_markdown(hits, Path(args.output))
        out_rel = Path(args.output)
        try:
            out_rel = out_rel.relative_to(REPO_ROOT)
        except ValueError:
            pass
        print(f"  Report: {out_rel}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
