#!/usr/bin/env python3
"""Tests for fix-frontmatter-gaps.py."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def skills_dir(tmp_path: Path) -> Path:
    """Create a minimal skills directory with gap scenarios."""
    root = tmp_path / ".claude" / "skills"

    # Skill missing category
    s1 = root / "data" / "energy" / "test-skill" / "SKILL.md"
    s1.parent.mkdir(parents=True)
    s1.write_text(textwrap.dedent("""\
        ---
        name: test-skill
        description: >-
          Analyze energy data from multiple sources
          and generate comprehensive reports for review
        version: 1.0.0
        ---
        # Test Skill
    """))

    # Skill missing version
    s2 = root / "engineering" / "cad" / "mesh-tool" / "SKILL.md"
    s2.parent.mkdir(parents=True)
    s2.write_text(textwrap.dedent("""\
        ---
        name: mesh-tool
        description: >-
          Generate and refine computational meshes
          for finite element analysis workflows
        category: engineering
        ---
        # Mesh Tool
    """))

    # Skill missing both category and version
    s3 = root / "business" / "sales" / "lead-gen" / "SKILL.md"
    s3.parent.mkdir(parents=True)
    s3.write_text(textwrap.dedent("""\
        ---
        name: lead-gen
        description: >-
          Identify and qualify potential leads using
          automated scoring and enrichment pipelines
        ---
        # Lead Gen
    """))

    # Skill with all fields (should be untouched)
    s4 = root / "ai" / "optimizer" / "SKILL.md"
    s4.parent.mkdir(parents=True)
    s4.write_text(textwrap.dedent("""\
        ---
        name: optimizer
        description: >-
          Optimize model parameters and hyperparameters
          using grid search and Bayesian methods
        version: 2.1.0
        category: ai
        ---
        # Optimizer
    """))

    # Skill with short description (report only, don't auto-fix)
    s5 = root / "ops" / "docker-tool" / "SKILL.md"
    s5.parent.mkdir(parents=True)
    s5.write_text(textwrap.dedent("""\
        ---
        name: docker-tool
        description: Docker management skill
        version: 1.0.0
        category: ops
        ---
        # Docker Tool
    """))

    return root


def load_script():
    """Import the fix script as a module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fix_frontmatter_gaps",
        "scripts/skills/fix-frontmatter-gaps.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def mod():
    return load_script()


class TestParseFrontmatter:
    def test_valid_frontmatter(self, mod):
        content = "---\nname: foo\nversion: 1.0.0\n---\n# Body"
        meta, body = mod.parse_frontmatter(content)
        assert meta["name"] == "foo"
        assert "# Body" in body

    def test_no_frontmatter(self, mod):
        content = "# Just a heading"
        meta, body = mod.parse_frontmatter(content)
        assert meta is None


class TestCategoryFromPath:
    def test_extracts_top_level(self, mod):
        root = Path("/skills")
        p = Path("/skills/engineering/cad/mesh/SKILL.md")
        assert mod.category_from_path(p, root) == "engineering"

    def test_single_level(self, mod):
        root = Path("/skills")
        p = Path("/skills/ai/SKILL.md")
        assert mod.category_from_path(p, root) == "ai"


class TestAddMissingField:
    def test_adds_category(self, mod):
        content = "---\nname: foo\nversion: 1.0.0\n---\n# Body"
        result = mod.add_missing_field(content, "category", "data")
        assert "category: data" in result
        assert result.startswith("---\n")

    def test_adds_version(self, mod):
        content = "---\nname: foo\ncategory: ai\n---\n# Body"
        result = mod.add_missing_field(content, "version", "1.0.0")
        assert "version: 1.0.0" in result

    def test_skips_existing_field(self, mod):
        content = "---\nname: foo\nversion: 2.0.0\n---\n# Body"
        result = mod.add_missing_field(content, "version", "1.0.0")
        assert result == content  # unchanged
        assert "version: 2.0.0" in result


class TestScanGaps:
    def test_finds_all_gaps(self, mod, skills_dir):
        gaps = mod.scan_gaps(skills_dir)
        missing_cat = [g for g in gaps if "category" in g["missing"]]
        missing_ver = [g for g in gaps if "version" in g["missing"]]
        short_desc = [g for g in gaps if g.get("short_description")]
        assert len(missing_cat) == 2  # test-skill, lead-gen
        assert len(missing_ver) == 2  # mesh-tool, lead-gen
        assert len(short_desc) == 1   # docker-tool

    def test_complete_skill_not_in_gaps(self, mod, skills_dir):
        gaps = mod.scan_gaps(skills_dir)
        names = [g["name"] for g in gaps]
        assert "optimizer" not in names


class TestApplyFixes:
    def test_fixes_category_and_version(self, mod, skills_dir):
        report = mod.apply_fixes(skills_dir, dry_run=False)
        assert report["category_fixed"] == 2
        assert report["version_fixed"] == 2

        # Verify file contents
        import yaml
        lead_gen = skills_dir / "business" / "sales" / "lead-gen" / "SKILL.md"
        content = lead_gen.read_text()
        meta, _ = mod.parse_frontmatter(content)
        assert meta["category"] == "business"
        assert meta["version"] == "1.0.0"

    def test_dry_run_no_changes(self, mod, skills_dir):
        orig = (skills_dir / "business" / "sales" / "lead-gen" / "SKILL.md").read_text()
        mod.apply_fixes(skills_dir, dry_run=True)
        after = (skills_dir / "business" / "sales" / "lead-gen" / "SKILL.md").read_text()
        assert orig == after

    def test_reports_short_descriptions(self, mod, skills_dir):
        report = mod.apply_fixes(skills_dir, dry_run=False)
        assert len(report["short_descriptions"]) == 1
        assert report["short_descriptions"][0]["name"] == "docker-tool"
