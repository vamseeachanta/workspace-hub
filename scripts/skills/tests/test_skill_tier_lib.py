#!/usr/bin/env python3
"""TDD tests for skill_tier_lib — quality tier classification."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/skills is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_tier_lib import classify_tier, tier_distribution, classify_skill_file


# ---------------------------------------------------------------------------
# classify_tier — unit tests
# ---------------------------------------------------------------------------

class TestClassifyTier:
    """Test tier classification from parsed frontmatter + body."""

    def test_tier_a_frontmatter_scripts_one_entry(self):
        meta = {"scripts": ["scripts/foo/bar.sh"]}
        assert classify_tier(meta, "some body text") == "A"

    def test_tier_a_frontmatter_scripts_multiple(self):
        meta = {"scripts": ["a.sh", "b.py"]}
        assert classify_tier(meta, "") == "A"

    def test_tier_a_takes_priority_over_exec_pattern(self):
        meta = {"scripts": ["x.sh"]}
        body = "Run: bash scripts/foo.sh"
        assert classify_tier(meta, body) == "A"

    def test_tier_a_empty_scripts_list_is_not_a(self):
        meta = {"scripts": []}
        assert classify_tier(meta, "short body") != "A"

    def test_tier_b_exec_pattern_bash_scripts(self):
        meta = {}
        body = "Execute: bash scripts/skills/audit.sh"
        assert classify_tier(meta, body) == "B"

    def test_tier_b_exec_pattern_uv_run(self):
        meta = None
        body = "Run: uv run --no-project python foo.py"
        assert classify_tier(meta, body) == "B"

    def test_tier_b_exec_pattern_bash_claude_skills(self):
        meta = {}
        body = "bash .claude/skills/dev/run.sh"
        assert classify_tier(meta, body) == "B"

    def test_tier_d_oversized_no_scripts(self):
        meta = {}
        body = "word " * 501  # 501 words, no script refs
        assert classify_tier(meta, body) == "D"

    def test_tier_d_exactly_501_words(self):
        meta = None
        body = "hello " * 501
        assert classify_tier(meta, body) == "D"

    def test_tier_d_500_words_is_not_d(self):
        meta = {}
        body = "word " * 500
        assert classify_tier(meta, body) == "C"

    def test_tier_d_oversized_but_has_exec_pattern_is_b(self):
        """Exec pattern takes priority over oversized prose."""
        meta = {}
        body = ("word " * 501) + " bash scripts/foo.sh"
        assert classify_tier(meta, body) == "B"

    def test_tier_c_default_short_prose(self):
        meta = {}
        body = "A focused guidance skill."
        assert classify_tier(meta, body) == "C"

    def test_tier_c_no_meta(self):
        assert classify_tier(None, "short body") == "C"

    def test_tier_c_meta_without_scripts_key(self):
        meta = {"name": "foo", "description": "bar"}
        body = "Some guidance content here."
        assert classify_tier(meta, body) == "C"

    def test_tier_a_scripts_not_list_is_not_a(self):
        """scripts: must be a list, not a string."""
        meta = {"scripts": "single.sh"}
        body = "short"
        assert classify_tier(meta, body) != "A"


# ---------------------------------------------------------------------------
# tier_distribution — aggregation tests
# ---------------------------------------------------------------------------

class TestTierDistribution:
    """Test tier counting from a list of tier labels."""

    def test_empty_list(self):
        assert tier_distribution([]) == {"A": 0, "B": 0, "C": 0, "D": 0}

    def test_mixed_tiers(self):
        tiers = ["A", "B", "C", "D", "A", "C"]
        result = tier_distribution(tiers)
        assert result == {"A": 2, "B": 1, "C": 2, "D": 1}

    def test_all_same(self):
        tiers = ["B", "B", "B"]
        result = tier_distribution(tiers)
        assert result == {"A": 0, "B": 3, "C": 0, "D": 0}


# ---------------------------------------------------------------------------
# classify_skill_file — integration tests (reads real file content)
# ---------------------------------------------------------------------------

class TestClassifySkillFile:
    """Test end-to-end classification from file content string."""

    def test_file_with_frontmatter_scripts(self):
        content = "---\nname: foo\nscripts:\n  - bar.sh\n---\nBody text."
        assert classify_skill_file(content) == "A"

    def test_file_with_exec_pattern_no_frontmatter(self):
        content = "# My Skill\n\nRun: uv run python script.py\n"
        assert classify_skill_file(content) == "B"

    def test_file_oversized_prose(self):
        content = "---\nname: bloat\n---\n" + ("word " * 510)
        assert classify_skill_file(content) == "D"

    def test_file_focused_prose(self):
        content = "---\nname: focused\ndescription: A small skill\n---\nShort body."
        assert classify_skill_file(content) == "C"

    def test_file_no_frontmatter_short(self):
        content = "# Legacy Skill\n\nJust some guidance."
        assert classify_skill_file(content) == "C"
