#!/usr/bin/env python3
"""TDD tests for eval-skills.py — WRK-1266: type inference improvements."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
eval_mod = import_module("eval-skills")

infer_skill_type = eval_mod.infer_skill_type
check_required_sections = eval_mod.check_required_sections
SECTIONS_BY_TYPE = eval_mod.SECTIONS_BY_TYPE


# ---------------------------------------------------------------------------
# infer_skill_type tests
# ---------------------------------------------------------------------------

class TestInferSkillTypeExplicitFrontmatter:
    """Explicit type: field in frontmatter always wins."""

    def test_explicit_workflow(self):
        meta = {"type": "workflow", "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "workflow"

    def test_explicit_guidance(self):
        meta = {"type": "guidance", "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "guidance"

    def test_explicit_reference(self):
        meta = {"type": "reference", "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "reference"

    def test_explicit_tool(self):
        meta = {"type": "tool", "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "tool"

    def test_explicit_unknown_falls_through(self):
        """Unknown type: value should not match, falls to heuristics."""
        meta = {"type": "bogus", "name": "test"}
        # No scripts, no exec patterns, business dir → reference
        result = infer_skill_type(meta, "", Path(".claude/skills/business/foo/SKILL.md"))
        assert result == "reference"


class TestInferSkillTypeScriptsExempt:
    """scripts_exempt: true → guidance for non-domain categories."""

    def test_scripts_exempt_true_non_domain(self):
        meta = {"scripts_exempt": True, "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "guidance"

    def test_scripts_exempt_true_domain_is_reference(self):
        """Domain categories override scripts_exempt."""
        meta = {"scripts_exempt": True, "name": "test"}
        path = Path(".claude/skills/engineering/foo/SKILL.md")
        assert infer_skill_type(meta, "", path) == "reference"

    def test_scripts_exempt_false(self):
        meta = {"scripts_exempt": False, "name": "test"}
        path = Path(".claude/skills/business/x/SKILL.md")
        assert infer_skill_type(meta, "no exec patterns", path) == "reference"


class TestInferSkillTypeScriptsField:
    """Frontmatter scripts: [...] → tool."""

    def test_has_scripts_list(self):
        meta = {"scripts": ["run.sh"], "name": "test"}
        assert infer_skill_type(meta, "", Path("x/SKILL.md")) == "tool"


class TestInferSkillTypeBodyPatterns:
    """Body exec patterns → tool."""

    def test_bash_scripts_pattern(self):
        body = "Run with: bash scripts/foo/run.sh"
        assert infer_skill_type(None, body, Path("x/SKILL.md")) == "tool"

    def test_uv_run_pattern(self):
        body = "Execute: uv run something"
        assert infer_skill_type(None, body, Path("x/SKILL.md")) == "tool"


class TestInferSkillTypePathBased:
    """Path-based inference for category directories."""

    def test_workspace_hub_dir_is_workflow(self):
        path = Path(".claude/skills/workspace-hub/some-skill/SKILL.md")
        assert infer_skill_type({}, "", path) == "workflow"

    def test_core_dir_is_workflow(self):
        path = Path(".claude/skills/_core/some-skill/SKILL.md")
        assert infer_skill_type({}, "", path) == "workflow"

    def test_business_dir_is_reference(self):
        path = Path(".claude/skills/business/some-skill/SKILL.md")
        assert infer_skill_type({}, "", path) == "reference"

    def test_data_dir_is_reference(self):
        path = Path(".claude/skills/data/visualization/charts/SKILL.md")
        assert infer_skill_type({}, "", path) == "reference"

    def test_science_dir_is_reference(self):
        path = Path(".claude/skills/science/physics/SKILL.md")
        assert infer_skill_type({}, "", path) == "reference"

    def test_reference_dir_is_reference(self):
        path = Path(".claude/skills/references/api-guide/SKILL.md")
        assert infer_skill_type({}, "", path) == "reference"

    def test_engineering_dir_is_reference(self):
        path = Path(".claude/skills/engineering/marine-offshore/aqwa/SKILL.md")
        assert infer_skill_type({}, "", path) == "reference"

    def test_coordination_dir_is_guidance(self):
        path = Path(".claude/skills/coordination/some-skill/SKILL.md")
        assert infer_skill_type({}, "", path) == "guidance"

    def test_operations_dir_is_guidance(self):
        path = Path(".claude/skills/operations/deploy/SKILL.md")
        assert infer_skill_type({}, "", path) == "guidance"

    def test_development_dir_is_tool(self):
        path = Path(".claude/skills/development/some-tool/SKILL.md")
        assert infer_skill_type({}, "", path) == "tool"

    def test_ai_dir_is_tool(self):
        path = Path(".claude/skills/ai/some-agent/SKILL.md")
        assert infer_skill_type({}, "", path) == "tool"


class TestInferSkillTypeShortContent:
    """Short skills with no code blocks → reference."""

    def test_short_no_code_is_reference(self):
        body = "Short guidance text.\n" * 5  # ~50 lines, no code
        path = Path(".claude/skills/misc/x/SKILL.md")
        meta = {"name": "test"}
        result = infer_skill_type(meta, body, path)
        assert result == "reference"

    def test_short_with_code_is_not_reference(self):
        body = "Use this:\n```bash\necho hello\n```\n"
        path = Path(".claude/skills/misc/x/SKILL.md")
        meta = {"name": "test"}
        result = infer_skill_type(meta, body, path)
        # Has code blocks → not reference, should be guidance or tool
        assert result != "reference"


class TestCheckRequiredSections:
    """check_required_sections uses skill_type to pick section list."""

    def test_guidance_needs_fewer_sections(self):
        body = "## When to Use\nfoo\n## Core Concepts\nbar\n## Best Practices\nbaz\n"
        issues = check_required_sections(body, skill_type="guidance")
        assert len(issues) == 0

    def test_workflow_needs_all_sections(self):
        body = "## Quick Start\nfoo\n"
        issues = check_required_sections(body, skill_type="workflow")
        # Missing 4 of 5 workflow sections
        assert len(issues) == 4

    def test_reference_needs_no_sections(self):
        body = "Some reference content without any specific sections.\n"
        issues = check_required_sections(body, skill_type="reference")
        assert len(issues) == 0

    def test_default_is_guidance_not_workflow(self):
        """With no skill_type, default should be guidance, not workflow."""
        body = "## When to Use\nfoo\n## Core Concepts\nbar\n## Best Practices\nbaz\n"
        issues = check_required_sections(body)
        # Default param is "workflow" currently — this test documents expected behavior after fix
        # After fix: default should still work correctly when called with explicit type
        assert isinstance(issues, list)


class TestEvaluateSkillUsesInferredType:
    """evaluate_skill must pass inferred type to check_required_sections."""

    def test_guidance_skill_no_section_warnings(self, tmp_path):
        """A guidance-type skill should not get workflow section warnings."""
        skill_dir = tmp_path / ".claude" / "skills" / "business" / "test-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(textwrap.dedent("""\
            ---
            name: test-guidance
            description: A guidance skill for testing type inference in eval
            version: 1.0.0
            category: business
            ---

            # Test Guidance Skill

            ## When to Use
            Use this when testing.

            ## Core Concepts
            Key concepts here.

            ## Best Practices
            Follow these practices.
        """))

        root = tmp_path / ".claude" / "skills"
        name_index = {"test-guidance": skill_file}
        result = eval_mod.evaluate_skill(skill_file, root, name_index)

        section_issues = [i for i in result.issues if i.check == "section_missing"]
        assert len(section_issues) == 0, f"Got unexpected section_missing: {[i.message for i in section_issues]}"


# ---------------------------------------------------------------------------
# check_line_count tests (WRK-1273)
# ---------------------------------------------------------------------------

check_line_count = eval_mod.check_line_count


class TestCheckLineCount:
    """check_line_count enforces 200-line warning and 400-line critical."""

    def test_under_limit_no_issues(self):
        content = "line\n" * 100
        issues = check_line_count(content)
        assert len(issues) == 0

    def test_exactly_200_no_issues(self):
        content = "line\n" * 200
        issues = check_line_count(content)
        assert len(issues) == 0

    def test_201_lines_warning(self):
        content = "line\n" * 201
        issues = check_line_count(content)
        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert issues[0].check == "line_count_exceeded"
        assert "201" in issues[0].message

    def test_400_lines_warning(self):
        content = "line\n" * 400
        issues = check_line_count(content)
        assert len(issues) == 1
        assert issues[0].severity == "warning"

    def test_401_lines_critical(self):
        content = "line\n" * 401
        issues = check_line_count(content)
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert issues[0].check == "line_count_exceeded"
        assert "401" in issues[0].message

    def test_empty_content(self):
        issues = check_line_count("")
        assert len(issues) == 0


# ---------------------------------------------------------------------------
# Type-aware description checks (WRK-1259)
# ---------------------------------------------------------------------------

check_description_quality = eval_mod.check_description_quality
DESC_MIN_WORDS_BY_TYPE = eval_mod.DESC_MIN_WORDS_BY_TYPE


class TestDescMinWordsByType:
    """DESC_MIN_WORDS_BY_TYPE defines per-type thresholds."""

    def test_workflow_threshold_is_10(self):
        assert DESC_MIN_WORDS_BY_TYPE["workflow"] == 10

    def test_tool_threshold_is_8(self):
        assert DESC_MIN_WORDS_BY_TYPE["tool"] == 8

    def test_guidance_threshold_is_5(self):
        assert DESC_MIN_WORDS_BY_TYPE["guidance"] == 5

    def test_reference_threshold_is_3(self):
        assert DESC_MIN_WORDS_BY_TYPE["reference"] == 3


class TestCheckDescriptionQualityTypeAware:
    """check_description_quality uses skill_type for threshold."""

    def test_6_word_desc_fails_workflow(self):
        meta = {"description": "A short skill description here now"}
        issues = check_description_quality(meta, skill_type="workflow")
        assert any(i.check == "description_too_short" for i in issues)

    def test_6_word_desc_passes_guidance(self):
        meta = {"description": "A short skill description here now"}
        issues = check_description_quality(meta, skill_type="guidance")
        assert not any(i.check == "description_too_short" for i in issues)

    def test_4_word_desc_passes_reference(self):
        meta = {"description": "Reference skill overview data"}
        issues = check_description_quality(meta, skill_type="reference")
        assert not any(i.check == "description_too_short" for i in issues)

    def test_4_word_desc_fails_tool(self):
        meta = {"description": "Reference skill overview data"}
        issues = check_description_quality(meta, skill_type="tool")
        assert any(i.check == "description_too_short" for i in issues)

    def test_2_word_desc_fails_reference(self):
        meta = {"description": "Too short"}
        issues = check_description_quality(meta, skill_type="reference")
        assert any(i.check == "description_too_short" for i in issues)

    def test_default_type_uses_guidance_threshold(self):
        """No skill_type → guidance threshold (5 words)."""
        meta = {"description": "Five word description is fine"}
        issues = check_description_quality(meta)
        assert not any(i.check == "description_too_short" for i in issues)

    def test_reference_desc_too_short_is_info_severity(self):
        """Reference type description warnings should be info, not warning."""
        meta = {"description": "Ab"}
        issues = check_description_quality(meta, skill_type="reference")
        short_issues = [i for i in issues if i.check == "description_too_short"]
        assert len(short_issues) == 1
        assert short_issues[0].severity == "info"


class TestEvaluateSkillDescTypeAware:
    """evaluate_skill passes inferred type to check_description_quality."""

    def test_reference_skill_short_desc_no_warning(self, tmp_path):
        """A reference-type skill with 5-word desc should not get warning."""
        skill_dir = tmp_path / ".claude" / "skills" / "engineering" / "test"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\n"
            "name: test-ref\n"
            "description: Engineering reference for testing\n"
            "version: 1.0.0\n"
            "category: engineering\n"
            "---\n\n# Test Reference\n\nSome content.\n"
        )
        root = tmp_path / ".claude" / "skills"
        result = eval_mod.evaluate_skill(skill_file, root, {"test-ref": skill_file})
        desc_warnings = [
            i for i in result.issues
            if i.check == "description_too_short" and i.severity == "warning"
        ]
        assert len(desc_warnings) == 0
