#!/usr/bin/env python3
"""Validate issue #2554 GTM vessel-contractor matrix artifacts.

This script is intentionally narrow: it parses the Markdown scaffold, derives the
semantic live/countable and High-priority counts, checks public-contact patterns,
and optionally rewrites the durable validation artifact used by the #2554 plan.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = ROOT / "docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md"
PLAN = ROOT / "docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md"
SUMMARY = ROOT / "docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md"
SCAN = ROOT / "docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md"
DENY = ROOT / ".legal-deny-list.yaml"

CONTACT_REGEXES = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}(?!\d)"),
    "individual_linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/in/[^\s)]+"),
}


def parse_rows(scaffold: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for match in re.finditer(r"^### Target (\d+) — (.+?)\n(.*?)(?=^### Target |^---\n\n## Summary Counts|\Z)", scaffold, re.M | re.S):
        target = int(match.group(1))
        title = match.group(2).strip()
        body = match.group(3)
        priority_match = re.search(r"outreach_priority\.\*\* \*\*(.*?)\*\*|outreach_priority\.\*\* (.*)", body)
        priority = ((priority_match.group(1) or priority_match.group(2)).strip() if priority_match else "")
        lower = f"{title}\n{body}".lower()
        exclusions: list[str] = []
        if "legacy" in title.lower() or "deprecated" in lower:
            exclusions.append("legacy/deprecated")
        if "outreach_priority.** **defer" in lower or "outreach_priority.** defer" in lower:
            exclusions.append("defer")
        if "partner-shape" in lower or "not a vessel-fleet target" in lower or "non-counted for the vessel-contractor minimum" in lower:
            exclusions.append("explicit non-counted partner-shape")
        if "wind-only; excluded from live_countable until fowt worked example" in lower:
            exclusions.append("wind-only pending FOWT worked example")
        rows.append({"target": target, "title": title, "priority": priority, "status": ", ".join(exclusions) or "counted", "counted": not exclusions})
    return rows


def deny_patterns() -> list[tuple[str, bool]]:
    patterns: list[tuple[str, bool]] = []
    if DENY.exists():
        for match in re.finditer(r'pattern: "(.*?)"\n\s+case_sensitive: (true|false)', DENY.read_text()):
            patterns.append((match.group(1), match.group(2) == "true"))
    return patterns


def scan_contacts(files: list[Path]) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    deny_hits: list[tuple[str, str]] = []
    contact_hits: list[tuple[str, str, str]] = []
    patterns = deny_patterns()
    for path in files:
        text = path.read_text()
        for pattern, case_sensitive in patterns:
            haystack = text if case_sensitive else text.lower()
            needle = pattern if case_sensitive else pattern.lower()
            if needle in haystack:
                deny_hits.append((str(path.relative_to(ROOT)), pattern))
        for name, regex in CONTACT_REGEXES.items():
            for match in regex.finditer(text):
                contact_hits.append((str(path.relative_to(ROOT)), name, match.group(0)[:80]))
    return deny_hits, contact_hits


def render_scan(rows: list[dict[str, object]], deny_hits: list[tuple[str, str]], contact_hits: list[tuple[str, str, str]]) -> str:
    live_count = sum(1 for row in rows if row["counted"])
    high_count = sum(1 for row in rows if row["priority"] == "High")
    table = "\n".join(
        f"| {idx} | {row['target']} | {row['title']} | {row['priority']} | {row['status']} |"
        for idx, row in enumerate(rows, 1)
    )
    deny = "- none" if not deny_hits else "\n".join(f"- `{path}`: `{pattern}`" for path, pattern in deny_hits)
    contacts = "- none" if not contact_hits else "\n".join(f"- `{path}`: {kind} `{value}`" for path, kind, value in contact_hits)
    return f"""# Legal/privacy and semantic-count validation — issue #2554 public matrix

Date: 2026-04-30
Generator: `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`
Scope:
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`

## Why this exists

The r1 post-fill review found that `scripts/legal/legal-sanity-scan.sh --diff-only` can false-pass once the matrix files are already committed. This artifact is generated from the scaffold and targeted committed files so #2554 promotion does not depend on an empty diff or hand-counted rows.

## Results

- Legal deny-list fixed-string hits: {len(deny_hits)}
- Contact-pattern hits (email, phone-like, individual LinkedIn URL): {len(contact_hits)}
- Semantic live/countable vessel/operator target count: {live_count}
- High-priority row count: {high_count}

## Legal deny-list hits

{deny}

## Contact-pattern hits

{contacts}

## Semantic target inventory (visual rows are contiguous; original target heading preserved)

| Row | Target heading | Title | Priority | Count status |
|---:|---:|---|---|---|
{table}

## Promotion note

This scan does not authorize outreach or send. It only supports the #2554 plan-review promotion gate by proving that the public matrix artifacts contain no deny-list/contact-pattern hits and deriving live/countable and High-priority counts from the scaffold parser.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifact", action="store_true")
    args = parser.parse_args()
    scaffold = SCAFFOLD.read_text()
    rows = parse_rows(scaffold)
    deny_hits, contact_hits = scan_contacts([PLAN, SCAFFOLD, SUMMARY])
    output = render_scan(rows, deny_hits, contact_hits)
    if args.write_artifact:
        SCAN.write_text(output)
    live_count = sum(1 for row in rows if row["counted"])
    high_count = sum(1 for row in rows if row["priority"] == "High")
    print(f"live_countable={live_count} high={high_count} deny_hits={len(deny_hits)} contact_hits={len(contact_hits)}")
    if live_count < 20 or high_count != 12 or deny_hits or contact_hits:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
