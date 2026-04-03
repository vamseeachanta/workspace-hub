"""Regression checks for repo-side Hermes skill parity merges (#1741)."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _text(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def test_writing_plans_template_is_no_longer_truncated():
    text = _text('.claude/skills/development/planning/writing-plans/SKILL.md')
    assert '*See sub-skills for full details.*' not in text
    assert '## Writing Process' in text
    assert '## Task Template' in text


def test_github_code_review_contains_operational_workflow():
    text = _text('.claude/skills/development/github/code-review/SKILL.md')
    assert 'gh pr review' in text
    assert '## Review Checklist' in text
    assert 'Verdict: APPROVE | MINOR | MAJOR | REJECT' in text


def test_obsidian_contains_vault_operations():
    text = _text('.claude/skills/business/productivity/obsidian/SKILL.md')
    assert 'OBSIDIAN_VAULT_PATH' in text
    assert 'Always quote vault paths' in text


def test_dspy_contains_core_concepts_and_examples():
    text = _text('.claude/skills/ai/prompting/dspy/SKILL.md')
    assert '## Core Concepts' in text
    assert 'ChainOfThought' in text
    assert '## Practical Workflow' in text


def test_systematic_debugging_contains_root_cause_rule():
    text = _text('.claude/skills/development/systematic-debugging/SKILL.md')
    assert 'Do not fix symptoms until you understand the root cause' in text
    assert '## Hard Stop Rule' in text
