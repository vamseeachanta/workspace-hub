"""Depth-relative `_section` boundary tests for build_skill_index (#3214).

Fixes the #3208 regression where `## When to Use` followed immediately by a
`### subsection` captured empty -> backfill, and the flat `#{1,2}` over-capture
(all-`###` files swallowing to EOF) + exact-vs-prefix mis-binding the r1 review
surfaced.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "build_skill_index.py"
spec = importlib.util.spec_from_file_location("build_skill_index", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["build_skill_index"] = mod
spec.loader.exec_module(mod)
_section = mod._section


def test_recovers_subsection_not_empty():
    # #3208 regression: ## heading immediately followed by ### subsection.
    body = "## When to Use This Skill\n### USE when:\n- doing X\n- doing Y\n## Next\nother"
    out = _section(body, "When to Use")
    assert "USE when" in out and "doing X" in out
    assert "other" not in out  # stops at the next ## (Next)


def test_h3_section_does_not_swallow_to_eof():
    # all-### file: ### Trigger must stop at the next ###, not run to EOF.
    body = "### Trigger\nuse when foo\n### Workflow\nstep 1\nstep 2\n### Example\nbig block"
    out = _section(body, "Trigger")
    assert "use when foo" in out
    assert "Workflow" not in out and "step 1" not in out  # bounded at next ###


def test_prefers_exact_shallowest_earliest_over_deep_subsection():
    # canonical ## heading must win over a deeper later ### with the same name.
    body = ("## When to Use\ncanonical text\n## Body\nstuff\n"
            "### When to Use\nphase-5 detail that must NOT be picked\n## End\nz")
    out = _section(body, "When to Use")
    assert "canonical text" in out
    assert "phase-5" not in out


def test_word_boundary_no_false_match():
    body = "## When to Useful tips\nshould not match\n## When to Use\nreal\n## End\n"
    out = _section(body, "When to Use")
    assert out == "real"


def test_case_insensitive_match():
    # "## When to use delegate_task" must match heading "When to Use".
    body = "## When to use delegate_task\ndelegate when busy\n## Other\nx"
    out = _section(body, "When to Use")
    assert "delegate when busy" in out


def test_no_heading_returns_empty():
    assert _section("## Overview\njust docs\n", "When to Use") == ""


def test_section_keeps_its_nested_subsections():
    # a ## section legitimately includes its ### subsections (up to the next ##).
    body = "## When to Use\nintro\n### case a\naaa\n### case b\nbbb\n## Next\nn"
    out = _section(body, "When to Use")
    assert "intro" in out and "aaa" in out and "bbb" in out
    assert "\nn" not in out
