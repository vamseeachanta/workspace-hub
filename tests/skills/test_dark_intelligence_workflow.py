"""Tests for the dark-intelligence-workflow skill definition."""

import os

import yaml


SKILL_PATH = ".claude/skills/data/dark-intelligence-workflow/SKILL.md"


def test_skill_file_exists():
    assert os.path.exists(SKILL_PATH)


def test_skill_frontmatter():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert meta["name"] == "dark-intelligence-workflow"
    assert meta["version"] == "1.0.0"
    assert meta["category"] == "data"
    assert "triggers" in meta
    assert len(meta["triggers"]) >= 3


def test_skill_has_related_skills():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert "related_skills" in meta
    assert "data/research-literature" in meta["related_skills"]
    assert "data/calculation-report" in meta["related_skills"]


def test_skill_has_seven_steps():
    with open(SKILL_PATH) as f:
        content = f.read()
    for step_num in range(1, 8):
        assert f"Step {step_num}" in content, f"Missing Step {step_num}"


def test_skill_has_legal_gate():
    with open(SKILL_PATH) as f:
        content = f.read()
    assert "HARD GATE" in content
    assert "legal-sanity-scan" in content


def test_skill_has_archive_schema():
    with open(SKILL_PATH) as f:
        content = f.read()
    assert "dark-intelligence-" in content
    assert "legal_scan_passed" in content
    assert "equations:" in content
    assert "inputs:" in content
    assert "outputs:" in content
    assert "worked_examples:" in content


def test_skill_has_tdd_template():
    with open(SKILL_PATH) as f:
        content = f.read()
    assert "test_" in content
    assert "from_dark_intelligence" in content
    assert "tolerance" in content


def test_skill_has_integration_points():
    with open(SKILL_PATH) as f:
        content = f.read()
    assert "research-literature" in content
    assert "calculation-report" in content
    assert "legal-sanity-scan" in content
