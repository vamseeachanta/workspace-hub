#!/usr/bin/env python3
"""Pure library for skill quality tier classification (A/B/C/D).

Tier priority (first match wins):
  A — frontmatter scripts: list with >=1 entry
  B — body matches EXEC_PATTERN (bash scripts/, uv run, bash .claude/skills/)
  D — body word count > 500 AND no script refs (decomposition candidate)
  C — everything else (focused prose)
"""

from __future__ import annotations

from audit_skill_lib import EXEC_PATTERN, parse_frontmatter

VALID_TIERS = ("A", "B", "C", "D")


def classify_tier(meta: dict | None, body: str) -> str:
    """Classify a skill into quality tier A/B/C/D.

    Args:
        meta: Parsed YAML frontmatter dict (or None).
        body: Skill body text (after frontmatter).

    Returns:
        Single-character tier label.
    """
    # Tier A: frontmatter scripts list with >=1 entry
    if (meta
            and isinstance(meta.get("scripts"), list)
            and len(meta["scripts"]) > 0):
        return "A"

    # Tier B: body contains executable command patterns
    if EXEC_PATTERN.search(body):
        return "B"

    # Tier D: oversized prose (>500 words) with no script refs
    word_count = len(body.split())
    if word_count > 500:
        return "D"

    # Tier C: everything else
    return "C"


def tier_distribution(tiers: list[str]) -> dict[str, int]:
    """Count occurrences of each tier in a list of tier labels.

    Returns:
        Dict with keys A, B, C, D and integer counts.
    """
    counts = {t: 0 for t in VALID_TIERS}
    for t in tiers:
        if t in counts:
            counts[t] += 1
    return counts


def classify_skill_file(content: str) -> str:
    """Classify a skill from its full file content string.

    Parses frontmatter, then delegates to classify_tier().
    """
    meta, body = parse_frontmatter(content)
    return classify_tier(meta, body)
