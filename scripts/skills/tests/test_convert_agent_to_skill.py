"""Tests for convert-agent-to-skill.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent dir to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import as module (hyphenated filename)
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "convert_agent_to_skill",
    Path(__file__).parent.parent / "convert-agent-to-skill.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

parse_frontmatter = _mod.parse_frontmatter
infer_category = _mod.infer_category
extract_description = _mod.extract_description
derive_skill_name = _mod.derive_skill_name
build_skill_content = _mod.build_skill_content
convert_single_file = _mod.convert_single_file
convert_directory = _mod.convert_directory
convert_agent = _mod.convert_agent
batch_convert = _mod.batch_convert
SKIP_FILES = _mod.SKIP_FILES
SKIP_DIRS = _mod.SKIP_DIRS


# ─── Frontmatter parsing ─────────────────────────────────────────────


class TestParseFrontmatter:
    def test_with_frontmatter(self):
        content = """---
name: test-agent
description: A test agent
model: sonnet
---
# Agent content
Body text here.
"""
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "test-agent"
        assert meta["description"] == "A test agent"
        assert meta["model"] == "sonnet"
        assert "# Agent content" in body
        assert "Body text here." in body

    def test_without_frontmatter(self):
        content = """# Just markdown
No frontmatter here.
"""
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert content == body

    def test_empty_content(self):
        meta, body = parse_frontmatter("")
        assert meta == {}
        assert body == ""

    def test_frontmatter_with_quoted_values(self):
        content = """---
name: "quoted-name"
description: 'single-quoted'
---
Body"""
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "quoted-name"
        assert meta["description"] == "single-quoted"

    def test_frontmatter_missing_closing(self):
        content = """---
name: broken
No closing marker.
"""
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content


# ─── Category inference ───────────────────────────────────────────────


class TestInferCategory:
    @pytest.mark.parametrize(
        "path,expected",
        [
            ("agents/orcaflex/README.md", "engineering"),
            ("agents/orcawave/damping.md", "engineering"),
            ("agents/aqwa/README.md", "engineering"),
            ("agents/freecad/README.md", "engineering"),
            ("agents/cad-engineering/README.md", "engineering"),
            ("agents/gmsh/README.md", "engineering"),
            ("agents/cathodic-protection.md", "engineering"),
            ("agents/github/pr-workflow.md", "development"),
            ("agents/testing/unit/runner.md", "development"),
            ("agents/sparc/design.md", "development"),
            ("agents/data/ml/model.md", "data"),
            ("agents/documentation/api.md", "documentation"),
            ("agents/unknown/thing.md", "general"),
        ],
    )
    def test_category_inference(self, path: str, expected: str):
        assert infer_category(path) == expected


# ─── Description extraction ──────────────────────────────────────────


class TestExtractDescription:
    def test_from_metadata(self):
        meta = {"description": "Agent for CP systems"}
        body = "Some body text"
        assert extract_description(meta, body) == "Agent for CP systems"

    def test_from_body_first_paragraph(self):
        meta = {}
        body = """# Title

You are an expert in engineering.
More details here."""
        assert extract_description(meta, body) == "You are an expert in engineering."

    def test_long_description_truncated(self):
        meta = {"description": "x" * 250}
        body = ""
        desc = extract_description(meta, body)
        assert len(desc) <= 200
        assert desc.endswith("...")

    def test_fallback_default(self):
        meta = {}
        body = "# Only headings\n```code```"
        desc = extract_description(meta, body)
        assert desc == "Converted from Claude agent file"


# ─── Skill name derivation ───────────────────────────────────────────


class TestDeriveSkillName:
    def test_from_metadata(self):
        meta = {"name": "my-agent"}
        assert derive_skill_name(Path("foo.md"), meta) == "my-agent"

    def test_from_file_path(self):
        meta = {}
        assert derive_skill_name(Path("agents/cool-agent.md"), meta) == "cool-agent"

    def test_from_directory_path(self, tmp_path):
        d = tmp_path / "orcaflex"
        d.mkdir()
        meta = {}
        assert derive_skill_name(d, meta) == "orcaflex"


# ─── Build skill content ─────────────────────────────────────────────


class TestBuildSkillContent:
    def test_basic_build(self):
        content = build_skill_content(
            "test-agent", "engineering", "A test skill", "Body here."
        )
        assert "name: test-agent" in content
        assert "category: engineering" in content
        assert "description: A test skill" in content
        assert "type: reference" in content
        assert "scripts_exempt: true" in content
        assert "# Test Agent" in content
        assert "Body here." in content

    def test_with_tags(self):
        content = build_skill_content(
            "tagged", "data", "Tagged skill", "Body.", tags=["tag1", "tag2"]
        )
        assert "tags: [tag1, tag2]" in content


# ─── Single file conversion ──────────────────────────────────────────


class TestConvertSingleFile:
    def test_converts_agent_file(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("""---
name: test-agent
description: Test agent description
---
# Test Agent

You are a test agent.""")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir)

        assert result is not None
        assert result.exists()
        content = result.read_text()
        assert "name: test-agent" in content
        assert "You are a test agent." in content

    def test_dry_run_creates_no_files(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("# Simple agent\nBody text.")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir, dry_run=True)

        assert result is not None  # Returns path
        assert not result.exists()  # But doesn't create it

    def test_skip_existing(self, tmp_path):
        agent = tmp_path / "test-agent.md"
        agent.write_text("# Agent\nBody.")

        output_dir = tmp_path / "skills"
        skill_dir = output_dir / "test-agent"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("existing content")

        result = convert_single_file(agent, output_dir)
        assert result is None
        assert skill_file.read_text() == "existing content"

    def test_skip_excluded_files(self, tmp_path):
        agent = tmp_path / "todo.md"
        agent.write_text("# Todo\nSome tasks.")

        output_dir = tmp_path / "skills"
        result = convert_single_file(agent, output_dir)
        assert result is None


# ─── Directory conversion ────────────────────────────────────────────


class TestConvertDirectory:
    def test_concatenates_md_files(self, tmp_path):
        agent_dir = tmp_path / "orcaflex-agent"
        agent_dir.mkdir()
        (agent_dir / "README.md").write_text("""---
name: orcaflex-agent
description: OrcaFlex agent
---
# OrcaFlex Agent

Main content here.""")
        (agent_dir / "BATCH_PROCESSING.md").write_text("""# Batch Processing

Batch notes here.""")

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)

        assert len(results) == 1
        content = results[0].read_text()
        assert "name: orcaflex-agent" in content
        assert "Main content here." in content
        assert "Batch notes here." in content

    def test_empty_directory(self, tmp_path):
        agent_dir = tmp_path / "empty-agent"
        agent_dir.mkdir()

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)
        assert results == []

    def test_skips_todo_files(self, tmp_path):
        agent_dir = tmp_path / "agent"
        agent_dir.mkdir()
        (agent_dir / "README.md").write_text("# Agent\nMain.")
        (agent_dir / "todo.md").write_text("# Todo\nSkip this.")

        output_dir = tmp_path / "skills"
        results = convert_directory(agent_dir, output_dir)

        assert len(results) == 1
        content = results[0].read_text()
        assert "Skip this." not in content


# ─── Batch conversion ────────────────────────────────────────────────


class TestBatchConvert:
    def test_batch_with_include_filter(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        # Create dirs
        for name in ["orcaflex", "testing", "swarm"]:
            d = agents_dir / name
            d.mkdir()
            (d / "README.md").write_text(f"# {name}\nContent for {name}.")

        output_dir = tmp_path / "skills"
        include = {"orcaflex", "testing"}
        results = batch_convert(agents_dir, output_dir, include=include)

        assert len(results) == 2
        names = {r.parent.name for r in results}
        assert "orcaflex" in names
        assert "testing" in names
        assert "swarm" not in names

    def test_batch_skips_excluded_dirs(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        for name in ["core", "swarm", "hive-mind", "github"]:
            d = agents_dir / name
            d.mkdir()
            (d / "README.md").write_text(f"# {name}\nContent.")

        output_dir = tmp_path / "skills"
        results = batch_convert(agents_dir, output_dir)

        names = {r.parent.name for r in results}
        assert "core" in names
        assert "github" in names
        assert "swarm" not in names
        assert "hive-mind" not in names

    def test_batch_handles_top_level_md_files(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        (agents_dir / "cathodic-protection.md").write_text("""---
name: cathodic-protection
description: CP expert
---
# CP Agent
Body.""")

        output_dir = tmp_path / "skills"
        results = batch_convert(agents_dir, output_dir)

        assert len(results) == 1
        assert results[0].parent.name == "cathodic-protection"

    def test_batch_nonexistent_dir(self, tmp_path):
        results = batch_convert(tmp_path / "nope", tmp_path / "out")
        assert results == []
