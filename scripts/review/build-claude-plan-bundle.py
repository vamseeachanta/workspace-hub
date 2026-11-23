#!/usr/bin/env python3
"""Build a Claude-specific compact review bundle from a markdown plan/spec.

The bundle is intentionally smaller than the source plan. It keeps only the
sections that are most useful for plan critique and trims each section to a
bounded size so the resulting payload stays well below the full document size.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTION_ORDER = [
    "Executive Summary",
    "Review Matrix",
    "Phased Rollout",
    "Testing Strategy",
    "Acceptance Criteria",
]

SECTION_LIMITS = {
    "Executive Summary": 900,
    "Review Matrix": 1100,
    "Phased Rollout": 1200,
    "Testing Strategy": 1100,
    "Acceptance Criteria": 1200,
}

FRONTMATTER_KEYS = [
    "title",
    "description",
    "priority",
    "complexity",
    "status",
    "phase",
    "timeline",
]


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith(("-", "#")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if key in FRONTMATTER_KEYS and value:
            data[key] = value
    return data, body


def parse_sections(body: str) -> tuple[str, dict[str, str]]:
    title = "Untitled Plan"
    title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()

    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(.+)$", body, re.MULTILINE))
    for idx, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        sections[name] = content
    return title, sections


def clean_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned: list[str] = []
    blank_run = 0
    for line in lines:
        if not line.strip():
            blank_run += 1
            if blank_run > 1:
                continue
            cleaned.append("")
            continue
        blank_run = 0
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    snippet = text[:limit].rstrip()
    last_break = max(snippet.rfind("\n- "), snippet.rfind("\n1. "), snippet.rfind("\n### "))
    if last_break > limit * 0.6:
        snippet = snippet[:last_break].rstrip()
    return f"{snippet}\n\n[truncated for Claude compact bundle]"


def build_bundle(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    title, sections = parse_sections(body)

    lines: list[str] = []
    lines.append(f"# Claude Compact Plan Review Bundle")
    lines.append("")
    lines.append(f"Source: `{source}`")
    lines.append(f"Plan Title: {frontmatter.get('title', title)}")
    if frontmatter:
        lines.append("")
        lines.append("## Plan Metadata")
        for key in FRONTMATTER_KEYS:
            if key in frontmatter:
                label = key.replace("_", " ").title()
                lines.append(f"- {label}: {frontmatter[key]}")

    lines.append("")
    lines.append("## Reviewer Instructions")
    lines.append("Focus on completeness, feasibility, dependency clarity, migration risk, testing depth, and machine-enforceable gates.")
    lines.append("Treat this as a compact proxy for the full plan. If a risk appears underspecified due to truncation, call that out explicitly.")

    for name in SECTION_ORDER:
        content = sections.get(name)
        if not content:
            continue
        lines.append("")
        lines.append(f"## {name}")
        lines.append(truncate(clean_text(content), SECTION_LIMITS[name]))

    bundle = "\n".join(lines).strip() + "\n"
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Source markdown plan")
    parser.add_argument("--output", help="Write bundle to this path instead of stdout")
    args = parser.parse_args()

    source = Path(args.input)
    bundle = build_bundle(source)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(bundle, encoding="utf-8")
    else:
        print(bundle, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
