from __future__ import annotations

from pathlib import Path


def test_hermes_template_rejects_nested_repo_skill_paths():
    template = Path("config/agents/hermes/config.yaml.template").read_text()
    bad = [line.strip() for line in template.splitlines() if "__WS_HUB_PATH__/" in line and "/.claude/skills" in line and "__WS_HUB_PATH__/.claude/skills" not in line]
    assert bad == []


def test_hermes_template_accepts_central_workspace_hub_root():
    template = Path("config/agents/hermes/config.yaml.template").read_text()
    assert "__WS_HUB_PATH__/.claude/skills" in template
    assert "__REGISTRY_REPO_SKILL_DIRS__" in template


def test_hermes_template_does_not_hardcode_sibling_repo_skill_dirs():
    template = Path("config/agents/hermes/config.yaml.template").read_text()
    assert "__TIER1_REPO_ROOT__/worldenergydata/.claude/skills" not in template
    assert "__TIER1_REPO_ROOT__/digitalmodel/.claude/skills" not in template
