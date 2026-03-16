#!/usr/bin/env python3
"""Tests for coverage checks, YAML output, and CLI in audit-skills.py."""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

SCRIPTS_DIR = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def lib():
    spec = importlib.util.spec_from_file_location(
        "audit_skill_lib", SCRIPTS_DIR / "audit_skill_lib.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def cli_mod():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location(
        "audit_skills", SCRIPTS_DIR / "audit-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def skill_tree(tmp_path):
    d = tmp_path / "skills"
    d.mkdir()
    return d


def _write(skill_dir: Path, name: str, content: str) -> Path:
    d = skill_dir / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(textwrap.dedent(content))
    return d / "SKILL.md"


class TestScriptCoverage:
    def test_flags_no_scripts(self, lib, skill_tree):
        _write(skill_tree, "bare", "---\nname: b\ndescription: t\n---\n# B\nProse.")
        gaps = lib.run_coverage_audit(skill_tree)
        assert any(not g["has_script_ref"] for g in gaps)

    def test_frontmatter_scripts_ok(self, lib, skill_tree):
        _write(skill_tree, "fm", "---\nname: fm\ndescription: t\nscripts:\n  - foo.sh\n---\n# FM")
        assert not any(not g["has_script_ref"] for g in lib.run_coverage_audit(skill_tree))

    def test_body_exec_ok(self, lib, skill_tree):
        _write(skill_tree, "bx", "---\nname: bx\ndescription: t\n---\n# BX\n```\nbash scripts/f\n```")
        assert not any(not g["has_script_ref"] for g in lib.run_coverage_audit(skill_tree))

    def test_exempt_skipped(self, lib, skill_tree):
        _write(skill_tree, "ex", "---\nname: ex\ndescription: t\nscripts_exempt: true\n---\n# EX")
        assert len(lib.run_coverage_audit(skill_tree)) == 0


class TestYamlOutput:
    def test_violations_schema(self, lib, skill_tree):
        _write(skill_tree, "vt", f"---\nname: vt\ndescription: t\n---\n{'word ' * 5001}")
        out = lib.format_violations_yaml(lib.run_violations_audit(skill_tree))
        parsed = yaml.safe_load(out)
        assert "violations" in parsed
        for v in parsed["violations"]:
            assert {"file", "check", "severity"} <= v.keys()

    def test_coverage_schema(self, lib, skill_tree):
        _write(skill_tree, "ct", "---\nname: ct\ndescription: t\n---\n# CT\nProse.")
        out = lib.format_coverage_yaml(lib.run_coverage_audit(skill_tree))
        parsed = yaml.safe_load(out)
        assert "skills" in parsed
        assert "gaps_total" in parsed


class TestCli:
    def test_violations_mode(self, cli_mod, skill_tree):
        _write(skill_tree, "cv", "---\nname: cv\ndescription: t\n---\n# CV")
        _, out = cli_mod.cli_run(["--mode", "violations", "--skill-dir", str(skill_tree)])
        assert "violations" in yaml.safe_load(out)

    def test_coverage_mode(self, cli_mod, skill_tree):
        _write(skill_tree, "cc", "---\nname: cc\ndescription: t\n---\n# CC")
        _, out = cli_mod.cli_run(["--mode", "coverage", "--skill-dir", str(skill_tree)])
        parsed = yaml.safe_load(out)
        assert parsed is None or "skills" in parsed or "gaps_total" in parsed

    def test_all_mode(self, cli_mod, skill_tree):
        _write(skill_tree, "ca", "---\nname: ca\ndescription: t\n---\n# CA")
        _, out = cli_mod.cli_run(["--mode", "all", "--skill-dir", str(skill_tree)])
        parsed = yaml.safe_load(out)
        assert "violations" in parsed
        assert "coverage" in parsed
