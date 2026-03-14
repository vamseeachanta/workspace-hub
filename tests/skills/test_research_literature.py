# ABOUTME: Validates research-literature skill file structure and frontmatter
# ABOUTME: Part of WRK-1181 — research and literature gathering skill

from __future__ import annotations

import os

import yaml


SKILL_PATH = ".claude/skills/data/research-literature/SKILL.md"


def test_skill_file_exists():
    assert os.path.exists(SKILL_PATH), f"Skill file missing: {SKILL_PATH}"


def test_skill_frontmatter():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    assert len(parts) >= 3, "Missing YAML frontmatter delimiters"
    meta = yaml.safe_load(parts[1])
    assert meta["name"] == "research-literature"
    assert "triggers" in meta
    assert len(meta["triggers"]) >= 3


def test_skill_has_required_sections():
    with open(SKILL_PATH) as f:
        content = f.read()
    required = [
        "## Inputs",
        "## 5-Step Workflow",
        "Step 1",
        "Step 2",
        "Step 3",
        "Step 4",
        "Step 5",
        "## Research Brief Template",
        "## AC Checklist",
    ]
    for section in required:
        assert section in content, f"Missing section: {section}"


def test_skill_references_existing_scripts():
    with open(SKILL_PATH) as f:
        content = f.read()
    assert "query-ledger.py" in content
    assert "index.jsonl" in content
    assert "capability-map" in content


def test_skill_version():
    with open(SKILL_PATH) as f:
        content = f.read()
    parts = content.split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert "version" in meta
    assert meta["version"] == "1.0.0"
