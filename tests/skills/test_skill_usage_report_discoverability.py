"""Tests for skill discoverability and retirement gating (#1725, #1726)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
USAGE_PATH = REPO_ROOT / "scripts" / "skills" / "skill-usage-report.py"
RETIRE_PATH = REPO_ROOT / "scripts" / "skills" / "check_retirement_candidates.py"

usage_spec = importlib.util.spec_from_file_location("skill_usage_report_discovery", USAGE_PATH)
usage = importlib.util.module_from_spec(usage_spec)
sys.modules["skill_usage_report_discovery"] = usage
assert usage_spec and usage_spec.loader
usage_spec.loader.exec_module(usage)

retire_spec = importlib.util.spec_from_file_location("retire_candidates_mod", RETIRE_PATH)
retire = importlib.util.module_from_spec(retire_spec)
sys.modules["retire_candidates_mod"] = retire
assert retire_spec and retire_spec.loader
retire_spec.loader.exec_module(retire)


def test_git_log_matching_requires_skill_context():
    log_text = """
    docs: architecture scanners refreshed
    feat(skills): update agenta skill docs
    feat(api): architecture cleanup
    """
    matched = usage.match_skills_in_git_log(log_text, {"architecture", "agenta", "api"})
    assert "agenta" in matched
    assert "architecture" not in matched
    assert "api" not in matched


def test_markdown_skill_links_count_as_references(tmp_path):
    target = tmp_path / "engineering" / "cad" / "blender"
    source = tmp_path / "engineering" / "cad" / "pyvista-3d"
    target.mkdir(parents=True)
    source.mkdir(parents=True)

    (target / "SKILL.md").write_text("---\nname: blender-interface\n---\n# Blender\n")
    (source / "SKILL.md").write_text(
        "---\nname: pyvista-3d\n---\n# PyVista\n\nSee [blender-interface](../blender/SKILL.md).\n"
    )

    skills = usage.scan_skills(tmp_path)
    refs = usage.build_reference_graph(skills)
    assert refs["blender-interface"] >= 1


def test_parent_skill_with_children_is_not_dead(tmp_path):
    parent = tmp_path / "ai" / "prompting" / "ai-prompting"
    child = parent / "sub-skill-a"
    parent.mkdir(parents=True)
    child.mkdir(parents=True)

    (parent / "SKILL.md").write_text("---\nname: ai-prompting\n---\n# Parent\n")
    (child / "SKILL.md").write_text("---\nname: prompt-sub-skill\n---\n# Child\n")

    skills = usage.scan_skills(tmp_path)
    refs = usage.build_reference_graph(skills)
    tiers = usage.classify_tiers(skills, refs, set())

    dead_names = {entry["skill"] for entry in tiers["dead"]}
    cold_names = {entry["skill"] for entry in tiers["cold"]}
    assert "ai-prompting" not in dead_names
    assert "ai-prompting" in cold_names


def test_retirement_checker_respects_non_dead_tier():
    entry = {
        "tier": "hot",
        "baseline_usage_rate": 0.0,
        "calls_in_period": 0,
    }
    assert retire.check_threshold("agenta", entry) == "ok"
