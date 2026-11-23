from __future__ import annotations

import re

from tests.helpers.stale_reference_docs import (
    CORE_BANNED_STALE_REFERENCE_PATTERNS,
    scan_stale_reference_hits,
)

SCAN_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "docs/README.md",
    "docs/context-pipeline.md",
    "docs/plans/README.md",
    "docs/work-queue-workflow.md",
    "docs/ops/legacy-claude-reference-map.md",
    "docs/governance/TRUST-ARCHITECTURE.md",
    "docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md",
    "docs/modules/workflow/SPEC_LOCALITY_POLICY.md",
]

ALLOWED_LEGACY_REFERENCE_FILES = {
    "docs/ops/legacy-claude-reference-map.md",
    "docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md",
}

EXTRA_BANNED_PATTERNS = [
    (
        "deleted active-stage hook",
        re.compile(r"\.claude/hooks/enforce-active-stage\.sh"),
    ),
    (
        "deleted session-start skill",
        re.compile(r"\.claude/skills/workspace-hub/session-start/SKILL\.md"),
    ),
    (
        "deleted work-queue stage contracts",
        re.compile(r"scripts/work-queue/stages/stage-(?:01-capture|05-user-review-plan-draft|07-user-review-plan-final|10-work-execution)\.yaml"),
    ),
]

BANNED_PATTERNS = [*CORE_BANNED_STALE_REFERENCE_PATTERNS, *EXTRA_BANNED_PATTERNS]


def test_allowlist_is_locked_to_the_two_intentional_legacy_docs() -> None:
    assert ALLOWED_LEGACY_REFERENCE_FILES == {
        "docs/ops/legacy-claude-reference-map.md",
        "docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md",
    }


def test_stale_reference_mentions_are_confined_to_explicit_legacy_docs() -> None:
    unexpected_hits: list[str] = []
    allowed_hits_found = False

    for relative_path in SCAN_FILES:
        hits = scan_stale_reference_hits(relative_path, patterns=BANNED_PATTERNS)
        if not hits:
            continue
        if relative_path in ALLOWED_LEGACY_REFERENCE_FILES:
            allowed_hits_found = True
            continue
        unexpected_hits.extend(hits)

    assert allowed_hits_found, "Expected at least one allowlisted legacy/reference doc to contain documented stale-path redirects"
    assert not unexpected_hits, "Found stale-path mentions outside explicit legacy/reference docs:\n" + "\n".join(unexpected_hits)
