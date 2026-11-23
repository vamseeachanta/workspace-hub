"""Checks for newly added knowledge-pipeline and digitalmodel-code-explorer skills."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def test_knowledge_pipeline_skill_mentions_target_dirs_and_tests():
    text = _read('.claude/skills/data/knowledge-pipeline/SKILL.md')
    assert 'scripts/knowledge/' in text
    assert 'scripts/learning/' in text
    assert 'docs/superpowers/' in text
    assert 'test_review_open_issues.py' in text


def test_digitalmodel_code_explorer_skill_mentions_module_mapping():
    text = _read('.claude/skills/digitalmodel/code-explorer/SKILL.md')
    assert 'digitalmodel/src/digitalmodel/' in text
    assert 'Source -> Test Mapping Pattern' in text
    assert 'fatigue/' in text
