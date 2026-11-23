"""Contract tests for docs/plans/_template-issue-plan.md (#2778).

The planning template must carry `Client:` (required) and `Project:` (optional)
header fields so downstream agents know which wiki sibling and which project
folder to search/write per .claude/rules/wiki-sibling-routing.md Layer 3.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "docs" / "plans" / "_template-issue-plan.md"


def _template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def test_template_file_exists() -> None:
    """Sanity: the planning template must exist."""
    assert TEMPLATE.is_file(), f"missing template at {TEMPLATE}"


def test_planning_template_carries_client_field() -> None:
    """Client: (required) header marker present per #2778 Layer 3."""
    text = _template_text()
    assert "**Client:**" in text, (
        "planning template must declare Client: header field per "
        ".claude/rules/wiki-sibling-routing.md Layer 3 (#2778)"
    )


def test_planning_template_carries_project_field() -> None:
    """Project: (optional) header marker present per #2778 Layer 3."""
    text = _template_text()
    assert "**Project:**" in text, (
        "planning template must declare Project: header field per "
        ".claude/rules/wiki-sibling-routing.md Layer 3 (#2778)"
    )


def test_planning_template_references_wiki_sibling_routing_rule() -> None:
    """Template must point planners at the routing contract."""
    text = _template_text()
    assert "wiki-sibling-routing" in text, (
        "planning template must reference .claude/rules/wiki-sibling-routing.md "
        "so plan authors know to populate Client:/Project: per #2778"
    )
