#!/usr/bin/env python3
# ABOUTME: TDD tests for WRK-1170 new path/filename rules in phase-e2-remap.py
# ABOUTME: Validates reclassification of "other" domain documents into proper domains

"""Tests for new PATH_RULES and FILENAME_RULES added in WRK-1170."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add script to path so we can import the rule functions
import importlib

_script_dir = str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
sys.path.insert(0, _script_dir)
_mod = importlib.import_module("phase-e2-remap")
apply_path_rules = _mod.apply_path_rules
apply_filename_rules = _mod.apply_filename_rules


# ---------------------------------------------------------------------------
# Path rule tests — knowledge_skills/projects
# ---------------------------------------------------------------------------

class TestKnowledgeSkillsProjectsRules:
    """Test reclassification of disciplines/knowledge_skills/projects paths."""

    def test_halliburton_path_maps_to_installation(self):
        path = "/mnt/ace/docs/disciplines/knowledge_skills/projects/halliburton/drilling_report.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "installation"
        assert "digitalmodel" in repos

    def test_halliburton_any_extension(self):
        path = "/mnt/ace/docs/disciplines/knowledge_skills/projects/halliburton/data.xlsx"
        result = apply_path_rules(path, "xlsx")
        assert result is not None
        assert result[0] == "installation"

    def test_ks_projects_fallback_maps_to_project_management(self):
        path = "/mnt/ace/docs/disciplines/knowledge_skills/projects/some_other/report.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "project-management"

    def test_ks_halliburton_takes_priority_over_fallback(self):
        path = "/mnt/ace/docs/disciplines/knowledge_skills/projects/halliburton/test.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "installation", "Halliburton rule should match before fallback"


# ---------------------------------------------------------------------------
# Path rule tests — 2H Projects
# ---------------------------------------------------------------------------

class TestTwoHProjectsRules:
    """Test reclassification of dde/0000 O&G/2H Projects paths."""

    def test_2h_projects_maps_to_marine(self):
        path = "/mnt/remote/ace-linux-2/dde/0000 O&G/2H Projects/riser_design.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "marine"
        assert "digitalmodel" in repos

    def test_2h_projects_any_extension(self):
        path = "/mnt/remote/ace-linux-2/dde/0000 O&G/2H Projects/subsea/analysis.xlsx"
        result = apply_path_rules(path, "xlsx")
        assert result is not None
        assert result[0] == "marine"


# ---------------------------------------------------------------------------
# Path rule tests — disciplines/misc/projects
# ---------------------------------------------------------------------------

class TestMiscProjectsRules:
    """Test reclassification of disciplines/misc/projects paths."""

    def test_misc_gis_maps_to_energy_economics(self):
        path = "/mnt/ace/docs/disciplines/misc/projects/gis/map_overlay.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "energy-economics"
        assert "worldenergydata" in repos

    def test_misc_projects_fallback_maps_to_project_management(self):
        path = "/mnt/ace/docs/disciplines/misc/projects/admin/budget.xlsx"
        result = apply_path_rules(path, "xlsx")
        assert result is not None
        domain, repos, rule = result
        assert domain == "project-management"

    def test_misc_gis_takes_priority_over_fallback(self):
        path = "/mnt/ace/docs/disciplines/misc/projects/gis/data.csv"
        result = apply_path_rules(path, "csv")
        assert result is not None
        assert result[0] == "energy-economics", "GIS rule should match before fallback"


# ---------------------------------------------------------------------------
# Path rule tests — Spare directory
# ---------------------------------------------------------------------------

class TestSpareDirectoryRules:
    """Test reclassification of Codes & Standards/Spare paths."""

    def test_spare_guidelines_maps_to_pipeline(self):
        path = "/mnt/ace/O&G-Standards/Spare/Papers/Guidelines/SCR_design.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "pipeline"
        assert "digitalmodel" in repos

    def test_spare_otc_maps_to_marine(self):
        path = "/mnt/ace/O&G-Standards/Spare/Papers/Offshore Technology/OTC-12345.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "marine"

    def test_spare_reference_maps_to_materials(self):
        path = "/mnt/ace/O&G-Standards/Spare/Papers/Reference/fatigue_handbook.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "materials"

    def test_spare_papers_fallback_maps_to_pipeline(self):
        path = "/mnt/ace/O&G-Standards/Spare/Papers/SomeOther/paper.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "pipeline"

    def test_spare_mil_maps_to_structural(self):
        path = "/mnt/ace/O&G-Standards/Spare/MIL/MIL-STD-1689.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "structural"

    def test_spare_fallback_maps_to_pipeline(self):
        path = "/mnt/ace/O&G-Standards/Spare/some_random_file.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[0] == "pipeline"

    def test_spare_guidelines_before_papers_fallback(self):
        path = "/mnt/ace/O&G-Standards/Spare/Papers/Guidelines/test.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[2] == "spare_guidelines", "Guidelines should match before Papers fallback"


# ---------------------------------------------------------------------------
# Filename rule tests — OTC and TNE
# ---------------------------------------------------------------------------

class TestNewFilenameRules:
    """Test new filename rules for OTC papers and TNE reports."""

    def test_otc_space_prefix_maps_to_marine(self):
        result = apply_filename_rules("OTC 12345 - Deepwater Riser.pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "marine"
        assert "digitalmodel" in repos

    def test_otc_dash_prefix_maps_to_marine(self):
        result = apply_filename_rules("OTC-12345-Subsea-Systems.pdf")
        assert result is not None
        assert result[0] == "marine"

    def test_tne_prefix_maps_to_pipeline(self):
        result = apply_filename_rules("TNE-001 Pipeline Analysis.pdf")
        assert result is not None
        domain, repos, rule = result
        assert domain == "pipeline"
        assert "digitalmodel" in repos

    def test_tne_no_dash_prefix_maps_to_pipeline(self):
        result = apply_filename_rules("TNE Report Summary.pdf")
        assert result is not None
        assert result[0] == "pipeline"


# ---------------------------------------------------------------------------
# No false-positive tests
# ---------------------------------------------------------------------------

class TestNoFalsePositives:
    """Ensure new rules don't misclassify unrelated paths."""

    def test_halliburton_rule_doesnt_match_other_knowledge_paths(self):
        path = "/mnt/ace/docs/disciplines/knowledge/textbooks/engineering.pdf"
        result = apply_path_rules(path, "pdf")
        # Should match "disciplines/knowledge" catch-all, not halliburton
        if result is not None:
            assert result[2] != "ks_halliburton"

    def test_2h_rule_doesnt_match_random_2h(self):
        path = "/mnt/ace/docs/some/2H_file.pdf"
        result = apply_path_rules(path, "pdf")
        if result is not None:
            assert result[2] != "dde_2h_projects"

    def test_spare_rules_dont_match_raw_cs_spare(self):
        """Raw Codes & Standards/Spare is handled by raw_cs_spare — our new rules
        should NOT override that (they target paths without _standards/raw/)."""
        path = "/mnt/ace/docs/_standards/raw/0000 Codes & Standards/Spare/test.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[2] == "raw_cs_spare", "Raw spare should match before new Spare rules"

    def test_otc_filename_no_match_for_other_prefix(self):
        result = apply_filename_rules("OTCX Something.pdf")
        # Should not match OTC rule since "OTCX" != "OTC " or "OTC-"
        if result is not None:
            assert "otc" not in result[2].lower()

    def test_tne_filename_no_match_for_unrelated(self):
        result = apply_filename_rules("INTERNET Document.pdf")
        if result is not None:
            assert "tne" not in result[2].lower()

    def test_existing_well_classified_paths_unchanged(self):
        """Verify existing standards paths still match their original rules."""
        path = "/mnt/ace/docs/_standards/API/API-RP-2A.pdf"
        result = apply_path_rules(path, "pdf")
        assert result is not None
        assert result[2] == "ace_api"
