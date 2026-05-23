"""Contract tests for calc-citation-contract.md sidecar schema (#2778).

The citation sidecar schema documented in .claude/rules/calc-citation-contract.md
must declare `source_sibling:` (required) and `source_project:` (optional) fields
per #2778 Layer 4 (Output layer routing).

The cross-repo digitalmodel/citations/schema.py dataclass update is tracked
separately (#2778 task #21) and lives in the digitalmodel repo; this test
covers only the workspace-hub-side contract.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CITATION_RULE = REPO_ROOT / ".claude" / "rules" / "calc-citation-contract.md"


def _rule_text() -> str:
    return CITATION_RULE.read_text(encoding="utf-8")


def test_citation_rule_file_exists() -> None:
    """Sanity: the citation rule file must exist."""
    assert CITATION_RULE.is_file(), f"missing rule at {CITATION_RULE}"


def test_sidecar_schema_mentions_source_sibling() -> None:
    """Citation rule must declare source_sibling field per #2778 Layer 4."""
    text = _rule_text()
    assert "source_sibling" in text, (
        "calc-citation-contract.md must declare source_sibling: field in the "
        "sidecar schema per .claude/rules/wiki-sibling-routing.md Layer 4 (#2778)"
    )


def test_sidecar_schema_mentions_source_project() -> None:
    """Citation rule must declare source_project field per #2778 Layer 4."""
    text = _rule_text()
    assert "source_project" in text, (
        "calc-citation-contract.md must declare source_project: field "
        "(optional) in the sidecar schema per #2778 Layer 4"
    )


def test_citation_rule_references_wiki_sibling_routing() -> None:
    """Cross-reference: the citation contract should point at the routing rule."""
    text = _rule_text()
    assert "wiki-sibling-routing" in text, (
        "calc-citation-contract.md must cross-reference wiki-sibling-routing.md "
        "so citation authors know which sibling slug to populate"
    )
