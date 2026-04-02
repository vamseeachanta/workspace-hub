"""Tests for review-routing-gate.py — AI review routing policy enforcement.

Encodes the routing rules from docs/standards/AI_REVIEW_ROUTING_POLICY.md:
- Two-provider review by default (Claude + Codex)
- Three-provider review when Gemini triggers fire
- Five Gemini triggers: architecture-heavy, research-heavy, ambiguous-requirements,
  high-stakes, context-saturation
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from review_routing_gate import (
    GEMINI_TRIGGERS,
    RoutingRecommendation,
    analyze_diff_for_triggers,
    build_recommendation,
    classify_change_scope,
    get_pr_diff,
    main,
)


# ---------------------------------------------------------------------------
# Unit tests: trigger detection from diffs
# ---------------------------------------------------------------------------
class TestAnalyzeDiffForTriggers:
    """Test that diffs are analyzed for Gemini trigger conditions."""

    def test_routine_change_no_triggers(self):
        """Simple single-file edit should trigger nothing."""
        diff = """\
diff --git a/scripts/ai/session-params.py b/scripts/ai/session-params.py
--- a/scripts/ai/session-params.py
+++ b/scripts/ai/session-params.py
@@ -10,3 +10,4 @@ def get_params():
     return params
+    # added a comment
"""
        triggers = analyze_diff_for_triggers(diff)
        assert triggers == []

    def test_architecture_heavy_cross_module(self):
        """Changes spanning 4+ directories signal architecture-heavy."""
        diff = """\
diff --git a/scripts/ai/foo.py b/scripts/ai/foo.py
--- a/scripts/ai/foo.py
+++ b/scripts/ai/foo.py
@@ -1 +1 @@
-old
+new
diff --git a/coordination/bar.py b/coordination/bar.py
--- a/coordination/bar.py
+++ b/coordination/bar.py
@@ -1 +1 @@
-old
+new
diff --git a/docs/standards/baz.md b/docs/standards/baz.md
--- a/docs/standards/baz.md
+++ b/docs/standards/baz.md
@@ -1 +1 @@
-old
+new
diff --git a/.claude/rules/qux.md b/.claude/rules/qux.md
--- a/.claude/rules/qux.md
+++ b/.claude/rules/qux.md
@@ -1 +1 @@
-old
+new
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "architecture-heavy" in triggers

    def test_architecture_heavy_config_files(self):
        """Changes to core config files signal architecture-heavy."""
        diff = """\
diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1,3 +1,3 @@
 [project]
-name = "old"
+name = "new"
diff --git a/.claude/rules/patterns.md b/.claude/rules/patterns.md
--- a/.claude/rules/patterns.md
+++ b/.claude/rules/patterns.md
@@ -1 +1 @@
-old
+new
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "architecture-heavy" in triggers

    def test_research_heavy_external_references(self):
        """Diffs mentioning many URLs or citations signal research-heavy."""
        diff = """\
diff --git a/docs/research/analysis.md b/docs/research/analysis.md
--- a/docs/research/analysis.md
+++ b/docs/research/analysis.md
@@ -1,2 +1,10 @@
 # Analysis
+See https://arxiv.org/abs/2401.001 for background.
+Reference: https://openai.com/research/paper1
+Also: https://anthropic.com/research/paper2
+Standard: https://www.iso.org/standard/12345.html
+Spec: https://www.w3.org/TR/spec1
+Data: https://huggingface.co/datasets/test
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "research-heavy" in triggers

    def test_high_stakes_security_changes(self):
        """Changes to security-related files signal high-stakes."""
        diff = """\
diff --git a/scripts/auth/validate-tokens.py b/scripts/auth/validate-tokens.py
--- a/scripts/auth/validate-tokens.py
+++ b/scripts/auth/validate-tokens.py
@@ -1,3 +1,5 @@
 import os
+API_KEY = os.environ["SECRET_KEY"]
+ENCRYPTION_SALT = os.environ["SALT"]
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "high-stakes" in triggers

    def test_high_stakes_production_changes(self):
        """Changes mentioning production/deploy signal high-stakes."""
        diff = """\
diff --git a/scripts/deploy/production-deploy.sh b/scripts/deploy/production-deploy.sh
--- a/scripts/deploy/production-deploy.sh
+++ b/scripts/deploy/production-deploy.sh
@@ -1,2 +1,4 @@
 #!/bin/bash
+# Deploy to production cluster
+kubectl apply -f production.yaml
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "high-stakes" in triggers

    def test_context_saturation_large_diff(self):
        """Very large diffs (>500 lines changed) signal context-saturation."""
        lines = []
        lines.append("diff --git a/big.py b/big.py")
        lines.append("--- a/big.py")
        lines.append("+++ b/big.py")
        lines.append("@@ -1,1 +1,600 @@")
        for i in range(600):
            lines.append(f"+line_{i} = {i}")
        diff = "\n".join(lines)
        triggers = analyze_diff_for_triggers(diff)
        assert "context-saturation" in triggers

    def test_ambiguous_requirements_todo_fixme(self):
        """Diffs with many TODO/FIXME/TBD markers signal ambiguous-requirements."""
        diff = """\
diff --git a/docs/spec.md b/docs/spec.md
--- a/docs/spec.md
+++ b/docs/spec.md
@@ -1,2 +1,10 @@
 # Spec
+TODO: clarify the interface contract
+FIXME: this conflicts with the other spec
+TBD: decide on data format
+TODO: confirm with stakeholders
+FIXME: ambiguous requirement here
"""
        triggers = analyze_diff_for_triggers(diff)
        assert "ambiguous-requirements" in triggers

    def test_multiple_triggers(self):
        """A diff can match multiple triggers simultaneously."""
        lines = []
        # Architecture-heavy: many directories
        for d in ["scripts/ai", "coordination", "docs/standards", ".claude/rules"]:
            lines.append(f"diff --git a/{d}/f.py b/{d}/f.py")
            lines.append(f"--- a/{d}/f.py")
            lines.append(f"+++ b/{d}/f.py")
            lines.append("@@ -1 +1 @@")
            lines.append("-old")
            lines.append("+new")
        # Research-heavy: URLs
        lines.append("diff --git a/docs/r.md b/docs/r.md")
        lines.append("--- a/docs/r.md")
        lines.append("+++ b/docs/r.md")
        lines.append("@@ -1 +1,6 @@")
        for i in range(5):
            lines.append(f"+https://example.com/paper{i}")
        diff = "\n".join(lines)
        triggers = analyze_diff_for_triggers(diff)
        assert "architecture-heavy" in triggers
        assert "research-heavy" in triggers


# ---------------------------------------------------------------------------
# Unit tests: change scope classification
# ---------------------------------------------------------------------------
class TestClassifyChangeScope:
    """Test classification of change scope for priority assignment."""

    def test_docs_only(self):
        diff = "diff --git a/docs/foo.md b/docs/foo.md\n"
        assert classify_change_scope(diff) == "docs-only"

    def test_tests_only(self):
        diff = "diff --git a/tests/test_foo.py b/tests/test_foo.py\n"
        assert classify_change_scope(diff) == "tests-only"

    def test_mixed(self):
        diff = (
            "diff --git a/scripts/ai/foo.py b/scripts/ai/foo.py\n"
            "diff --git a/docs/bar.md b/docs/bar.md\n"
        )
        assert classify_change_scope(diff) == "mixed"

    def test_code_only(self):
        diff = "diff --git a/scripts/ai/foo.py b/scripts/ai/foo.py\n"
        assert classify_change_scope(diff) == "code"


# ---------------------------------------------------------------------------
# Unit tests: recommendation building
# ---------------------------------------------------------------------------
class TestBuildRecommendation:
    """Test the final recommendation JSON structure."""

    def test_no_triggers_two_provider(self):
        rec = build_recommendation(triggers=[], scope="code")
        assert rec.reviewers == ["codex"]
        assert rec.priority == "normal"
        assert "two-provider" in rec.reason.lower() or "default" in rec.reason.lower()

    def test_triggers_add_gemini(self):
        rec = build_recommendation(triggers=["architecture-heavy"], scope="code")
        assert "codex" in rec.reviewers
        assert "gemini" in rec.reviewers
        assert rec.priority == "high"
        assert "architecture-heavy" in rec.triggers_matched

    def test_docs_only_low_priority(self):
        rec = build_recommendation(triggers=[], scope="docs-only")
        assert rec.priority == "low"
        assert rec.reviewers == ["codex"]

    def test_tests_only_low_priority(self):
        rec = build_recommendation(triggers=[], scope="tests-only")
        assert rec.priority == "low"

    def test_multiple_triggers_high_priority(self):
        rec = build_recommendation(
            triggers=["architecture-heavy", "high-stakes"], scope="mixed"
        )
        assert rec.priority == "high"
        assert "gemini" in rec.reviewers
        assert len(rec.triggers_matched) == 2

    def test_recommendation_to_json(self):
        rec = build_recommendation(triggers=["research-heavy"], scope="code")
        j = rec.to_dict()
        assert isinstance(j, dict)
        assert "reviewers" in j
        assert "reason" in j
        assert "priority" in j
        assert "triggers_matched" in j
        assert "orchestrator" in j
        assert j["orchestrator"] == "claude"

    def test_recommendation_json_serializable(self):
        rec = build_recommendation(triggers=[], scope="code")
        output = json.dumps(rec.to_dict())
        parsed = json.loads(output)
        assert parsed["reviewers"] == ["codex"]


# ---------------------------------------------------------------------------
# Unit tests: GEMINI_TRIGGERS constant
# ---------------------------------------------------------------------------
class TestGeminiTriggers:
    def test_all_five_triggers_defined(self):
        expected = {
            "architecture-heavy",
            "research-heavy",
            "ambiguous-requirements",
            "high-stakes",
            "context-saturation",
        }
        assert set(GEMINI_TRIGGERS.keys()) == expected

    def test_each_trigger_has_rationale(self):
        for name, trigger in GEMINI_TRIGGERS.items():
            assert "rationale" in trigger, f"{name} missing rationale"


# ---------------------------------------------------------------------------
# Integration tests: CLI interface
# ---------------------------------------------------------------------------
class TestCLIInterface:
    """Test the script can be invoked from CLI."""

    def test_stdin_mode(self):
        """Script reads diff from stdin when --stdin is passed."""
        diff = """\
diff --git a/scripts/ai/foo.py b/scripts/ai/foo.py
--- a/scripts/ai/foo.py
+++ b/scripts/ai/foo.py
@@ -1 +1 @@
-old
+new
"""
        script = str(Path(__file__).resolve().parent.parent / "review_routing_gate.py")
        result = subprocess.run(
            ["uv", "run", "python", script, "--stdin"],
            input=diff,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent.parent.parent),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        output = json.loads(result.stdout)
        assert "reviewers" in output
        assert "codex" in output["reviewers"]

    def test_stdin_large_diff_triggers_saturation(self):
        """Large diff via stdin triggers context-saturation."""
        lines = ["diff --git a/big.py b/big.py", "--- a/big.py", "+++ b/big.py", "@@ -1,1 +1,600 @@"]
        for i in range(600):
            lines.append(f"+line_{i} = {i}")
        diff = "\n".join(lines)
        script = str(Path(__file__).resolve().parent.parent / "review_routing_gate.py")
        result = subprocess.run(
            ["uv", "run", "python", script, "--stdin"],
            input=diff,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent.parent.parent),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        output = json.loads(result.stdout)
        assert "gemini" in output["reviewers"]
        assert "context-saturation" in output["triggers_matched"]

    def test_empty_diff_exits_with_error(self):
        """Empty diff should produce an error."""
        script = str(Path(__file__).resolve().parent.parent / "review_routing_gate.py")
        result = subprocess.run(
            ["uv", "run", "python", script, "--stdin"],
            input="",
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent.parent.parent),
        )
        assert result.returncode != 0

    def test_help_flag(self):
        """--help should work."""
        script = str(Path(__file__).resolve().parent.parent / "review_routing_gate.py")
        result = subprocess.run(
            ["uv", "run", "python", script, "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent.parent.parent),
        )
        assert result.returncode == 0
        assert "routing" in result.stdout.lower() or "review" in result.stdout.lower()
