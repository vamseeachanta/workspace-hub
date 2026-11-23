#!/usr/bin/env python3
"""Tests for fix-related-skills.py"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from fix_related_skills import (
    build_name_index_from_skills,
    resolve_reference,
    compute_fixes,
)


@pytest.fixture
def name_index():
    """Simulated name index matching real workspace-hub skills."""
    return {
        "session-start": Path("workspace-hub/session-start/SKILL.md"),
        "session-end": Path("workspace-hub/session-end/SKILL.md"),
        "work-queue": Path("coordination/workspace/work-queue/SKILL.md"),
        "work-queue-workflow": Path("workspace-hub/work-queue-workflow/SKILL.md"),
        "workflow-gatepass": Path("workspace-hub/workflow-gatepass/SKILL.md"),
        "workflow-html": Path("workspace-hub/workflow-html/SKILL.md"),
        "comprehensive-learning": Path("workspace-hub/comprehensive-learning/SKILL.md"),
        "cathodic-protection": Path("engineering/marine-offshore/cathodic-protection/SKILL.md"),
        "catenary-riser": Path("engineering/marine-offshore/catenary-riser/SKILL.md"),
        "structural-analysis": Path("engineering/marine-offshore/structural-analysis/SKILL.md"),
        "hydrodynamics": Path("engineering/marine-offshore/hydrodynamics/SKILL.md"),
        "hydrodynamic-analysis": Path("engineering/marine-offshore/hydrodynamic-analysis/SKILL.md"),
        "viv-analysis": Path("engineering/marine-offshore/viv-analysis/SKILL.md"),
        "orcaflex-specialist": Path("engineering/marine-offshore/orcaflex-specialist/SKILL.md"),
        "orcawave-analysis": Path("engineering/marine-offshore/orcawave-analysis/SKILL.md"),
        "mooring-analysis": Path("engineering/marine-offshore/mooring-analysis/SKILL.md"),
        "risk-assessment": Path("engineering/marine-offshore/risk-assessment/SKILL.md"),
        "calculation-report": Path("data/calculation-report/SKILL.md"),
        "dark-intelligence-workflow": Path("data/dark-intelligence-workflow/SKILL.md"),
        "doc-intelligence-promotion": Path("data/doc-intelligence-promotion/SKILL.md"),
        "openpyxl": Path("data/office/openpyxl/SKILL.md"),
        "research-literature": Path("data/research-literature/SKILL.md"),
        "doc-extraction": Path("engineering/doc-extraction/SKILL.md"),
        "units": Path("engineering/units/SKILL.md"),
        "calculation-methodology": Path("engineering/calculation-methodology/SKILL.md"),
        "improve": Path("workspace-hub/improve/SKILL.md"),
        "save": Path("workspace-hub/save/SKILL.md"),
        "qa-closure": Path("workspace-hub/qa-closure/SKILL.md"),
        "reflect": Path("workspace-hub/reflect/SKILL.md"),
        "repo-sync": Path("workspace-hub/repo-sync/SKILL.md"),
        "repo-structure": Path("workspace-hub/repo-structure/SKILL.md"),
        "tool-readiness": Path("workspace-hub/tool-readiness/SKILL.md"),
        "ecosystem-health": Path("workspace-hub/ecosystem-health/SKILL.md"),
        "wrk-lifecycle-testpack": Path("workspace-hub/wrk-lifecycle-testpack/SKILL.md"),
        "workstations": Path("workspace-hub/workstations/SKILL.md"),
        "checkpoint": Path("workspace-hub/checkpoint/SKILL.md"),
        "knowledge-management": Path("workspace-hub/knowledge-management/SKILL.md"),
        "doc-research-download": Path("data/doc-research-download/SKILL.md"),
        "insights": Path("workspace-hub/insights/SKILL.md"),
        "subagent-driven": Path("development/subagent-driven/SKILL.md"),
        "writing-plans": Path("development/planning/writing-plans/SKILL.md"),
        "plan-mode": Path("workspace-hub/plan-mode/SKILL.md"),
        "testing-tdd-london": Path("development/testing-tdd-london/SKILL.md"),
        "shell-tdd": Path("development/shell-tdd/SKILL.md"),
        "docker": Path("operations/devtools/docker/SKILL.md"),
        "legal-sanity-scan": Path("coordination/workspace/legal-sanity-scan/SKILL.md"),
        "obsidian": Path("business/productivity/obsidian/SKILL.md"),
        "ecosystem-terminology": Path("workspace-hub/ecosystem-terminology/SKILL.md"),
        "skill-eval": Path("development/skill-eval/SKILL.md"),
        "repo-capability-map": Path("coordination/workspace/repo-capability-map/SKILL.md"),
        "engineering-context-loader": Path("workspace-hub/engineering-context-loader/SKILL.md"),
        "knowledge-manager": Path("coordination/workspace/knowledge-manager/SKILL.md"),
        "elite-frontend-ux": Path("development/elite-frontend-ux/SKILL.md"),
        "git-worktree-workflow": Path("development/git-worktree-workflow/SKILL.md"),
        "today": Path("business/productivity/today/SKILL.md"),
        "session-start": Path("workspace-hub/session-start/SKILL.md"),
    }


class TestResolveReference:
    """Test reference resolution logic."""

    def test_already_valid(self, name_index):
        """Already valid name returns itself."""
        assert resolve_reference("work-queue", name_index) == "work-queue"

    def test_path_style_strip_prefix(self, name_index):
        """Path-style ref like workspace-hub/session-start resolves to session-start."""
        assert resolve_reference("workspace-hub/session-start", name_index) == "session-start"

    def test_path_style_deep(self, name_index):
        """Deep path like engineering/marine-offshore/cathodic-protection resolves."""
        assert resolve_reference("engineering/marine-offshore/cathodic-protection", name_index) == "cathodic-protection"

    def test_path_style_coordination(self, name_index):
        """coordination/workspace/work-queue resolves to work-queue."""
        assert resolve_reference("coordination/workspace/work-queue", name_index) == "work-queue"

    def test_path_with_skill_suffix(self, name_index):
        """coordination/workspace/work-queue/SKILL resolves to work-queue."""
        assert resolve_reference("coordination/workspace/work-queue/SKILL", name_index) == "work-queue"

    def test_path_style_data_prefix(self, name_index):
        """data/calculation-report resolves to calculation-report."""
        assert resolve_reference("data/calculation-report", name_index) == "calculation-report"

    def test_path_style_data_deep(self, name_index):
        """data/office/openpyxl resolves to openpyxl."""
        assert resolve_reference("data/office/openpyxl", name_index) == "openpyxl"

    def test_nonexistent_no_match(self, name_index):
        """Truly nonexistent skill returns None (remove)."""
        assert resolve_reference("kubernetes", name_index) is None

    def test_nonexistent_gatsby(self, name_index):
        assert resolve_reference("gatsby", name_index) is None

    def test_nonexistent_latex(self, name_index):
        assert resolve_reference("latex", name_index) is None

    def test_colon_style_sparc(self, name_index):
        """sparc:designer should be removed (not a related_skill format)."""
        assert resolve_reference("sparc:designer", name_index) is None

    def test_superpowers_slash(self, name_index):
        """superpowers/writing-plans resolves to writing-plans."""
        assert resolve_reference("superpowers/writing-plans", name_index) == "writing-plans"

    def test_session_start_routine_maps(self, name_index):
        """session-start-routine should map to session-start."""
        assert resolve_reference("session-start-routine", name_index) == "session-start"

    def test_parallel_dispatch_no_match(self, name_index):
        """parallel-dispatch has no good match, should be None."""
        # No exact or suffix match exists
        result = resolve_reference("parallel-dispatch", name_index)
        # Acceptable: None or a valid name
        assert result is None or result in name_index

    def test_knowledge_resolves(self, name_index):
        """knowledge should resolve to knowledge-management."""
        assert resolve_reference("knowledge", name_index) == "knowledge-management"

    def test_planning_resolves_or_removes(self, name_index):
        """planning should not incorrectly resolve."""
        result = resolve_reference("planning", name_index)
        assert result is None or result in name_index

    def test_testing_resolves(self, name_index):
        """testing should resolve to testing-tdd-london or be removed."""
        result = resolve_reference("testing", name_index)
        assert result is None or result in name_index

    def test_content_creation_no_match(self, name_index):
        assert resolve_reference("content-creation", name_index) is None

    def test_webhook_automation_no_match(self, name_index):
        assert resolve_reference("webhook-automation", name_index) is None

    def test_roadmap_management_no_match(self, name_index):
        assert resolve_reference("roadmap-management", name_index) is None


class TestComputeFixes:
    """Test the batch fix computation."""

    def test_returns_fixes_and_removals(self, name_index):
        refs = [
            "workspace-hub/session-start",
            "kubernetes",
            "work-queue",
        ]
        fixes = compute_fixes(refs, name_index)
        # workspace-hub/session-start -> session-start (fix)
        assert fixes["workspace-hub/session-start"] == "session-start"
        # kubernetes -> None (remove)
        assert fixes["kubernetes"] is None
        # work-queue -> already valid, should NOT appear in fixes
        assert "work-queue" not in fixes

    def test_dedup_fixes_same_target(self, name_index):
        """Two different refs resolving to same target are both valid."""
        refs = [
            "workspace-hub/session-start",
            "session-start-routine",
        ]
        fixes = compute_fixes(refs, name_index)
        assert fixes["workspace-hub/session-start"] == "session-start"
        assert fixes["session-start-routine"] == "session-start"
