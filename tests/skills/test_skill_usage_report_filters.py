"""Tests for skill usage report filtering (#1739)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "skills" / "skill-usage-report.py"
SPEC = importlib.util.spec_from_file_location("skill_usage_report", SCRIPT_PATH)
module = importlib.util.module_from_spec(SPEC)
sys.modules["skill_usage_report"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_scan_skills_excludes_internal_and_core_dirs(tmp_path):
    (tmp_path / "_core" / "bash" / "x" ).mkdir(parents=True)
    (tmp_path / "_internal" / "meta" / "y").mkdir(parents=True)
    (tmp_path / "development" / "real-skill").mkdir(parents=True)

    (tmp_path / "_core" / "bash" / "x" / "SKILL.md").write_text("---\nname: x\n---\n")
    (tmp_path / "_internal" / "meta" / "y" / "SKILL.md").write_text("---\nname: y\n---\n")
    (tmp_path / "development" / "real-skill" / "SKILL.md").write_text("---\nname: real-skill\n---\n")

    skills = module.scan_skills(tmp_path)

    assert "development/real-skill" in skills
    assert not any(key.startswith("_core/") for key in skills)
    assert not any(key.startswith("_internal/") for key in skills)
