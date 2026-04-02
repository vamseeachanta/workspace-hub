"""Tests for automated download-and-catalog pipeline.

All network and filesystem operations are mocked so tests run in CI
without /mnt/ace or internet access.

GH issue: #1578
"""

import json
import os
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import yaml


# ---------------------------------------------------------------------------
# Lazy import of module under test
# ---------------------------------------------------------------------------

@pytest.fixture
def pipeline_module():
    """Import the pipeline module."""
    import importlib
    import sys
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts" / "data" / "research-literature"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    mod_name = "download_and_catalog"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    mod = importlib.import_module(mod_name)
    return mod


# ---------------------------------------------------------------------------
# Sample registry data
# ---------------------------------------------------------------------------

SAMPLE_REGISTRY = {
    "generated": "2026-04-02T04:25:44",
    "total_entries": 5,
    "entries": [
        {
            "id": "moordyn_repo",
            "url": "https://github.com/FloatingArrayDesign/MoorDyn",
            "name": "MoorDyn",
            "type": "github_repo",
            "domain": "marine_offshore",
            "local_backup_path": "",
            "download_status": "not_started",
            "last_checked": "2026-04-01",
            "relevance_score": 5,
        },
        {
            "id": "wave_energy_paper",
            "url": "https://example.com/wave-energy.pdf",
            "name": "Wave Energy Analysis",
            "type": "paper",
            "domain": "hydrodynamics",
            "local_backup_path": "",
            "download_status": "not_started",
            "last_checked": "2026-04-01",
            "relevance_score": 4,
        },
        {
            "id": "dnv_portal",
            "url": "https://www.dnv.com/standards",
            "name": "DNV Standards Portal",
            "type": "standard_portal",
            "domain": "structural",
            "local_backup_path": "",
            "download_status": "not_started",
            "last_checked": "2026-04-01",
            "relevance_score": 5,
        },
        {
            "id": "already_done",
            "url": "https://example.com/done.pdf",
            "name": "Already Downloaded",
            "type": "paper",
            "domain": "pipeline",
            "local_backup_path": "/mnt/ace/papers/done.pdf",
            "download_status": "downloaded",
            "last_checked": "2026-03-30",
            "relevance_score": 3,
        },
        {
            "id": "tutorial_entry",
            "url": "https://example.com/tutorial",
            "name": "Python Tutorial",
            "type": "tutorial",
            "domain": "data_science",
            "local_backup_path": "",
            "download_status": "not_started",
            "last_checked": "2026-04-01",
            "relevance_score": 2,
        },
    ],
}


@pytest.fixture
def sample_registry():
    return SAMPLE_REGISTRY.copy()


@pytest.fixture
def registry_file(tmp_path, sample_registry):
    """Write sample registry to a temp YAML file."""
    p = tmp_path / "online-resource-registry.yaml"
    p.write_text(yaml.dump(sample_registry, default_flow_style=False))
    return p


# ===========================================================================
# 1. Registry filtering
# ===========================================================================

class TestRegistryFiltering:
    """Filter registry entries by download_status and type."""

    def test_filters_not_started_and_correct_types(self, pipeline_module, sample_registry):
        """Should only return entries with download_status=not_started AND valid type."""
        result = pipeline_module.filter_downloadable(sample_registry["entries"])
        ids = [e["id"] for e in result]
        assert "moordyn_repo" in ids       # github_repo, not_started
        assert "wave_energy_paper" in ids   # paper, not_started
        assert "dnv_portal" in ids          # standard_portal, not_started
        assert "already_done" not in ids    # downloaded
        assert "tutorial_entry" not in ids  # tutorial type not in downloadable types

    def test_domain_filter(self, pipeline_module, sample_registry):
        """--domain flag should narrow to one domain."""
        result = pipeline_module.filter_downloadable(
            sample_registry["entries"], domain="hydrodynamics",
        )
        assert len(result) == 1
        assert result[0]["id"] == "wave_energy_paper"

    def test_limit_flag(self, pipeline_module, sample_registry):
        """--limit should cap the number of results."""
        result = pipeline_module.filter_downloadable(
            sample_registry["entries"], limit=1,
        )
        assert len(result) == 1

    def test_empty_registry(self, pipeline_module):
        """Empty entries list should return empty."""
        result = pipeline_module.filter_downloadable([])
        assert result == []


# ===========================================================================
# 2. Target path generation
# ===========================================================================

class TestPathGeneration:
    """Target path: /mnt/ace/<repo-name>/<domain>/"""

    def test_github_repo_path(self, pipeline_module):
        entry = {
            "id": "moordyn_repo",
            "url": "https://github.com/FloatingArrayDesign/MoorDyn",
            "type": "github_repo",
            "domain": "marine_offshore",
        }
        path = pipeline_module.determine_target_path(entry, ace_root="/mnt/ace")
        assert path == "/mnt/ace/downloads/github_repos/marine_offshore/MoorDyn"

    def test_paper_path(self, pipeline_module):
        entry = {
            "id": "wave_paper",
            "url": "https://example.com/wave-energy.pdf",
            "type": "paper",
            "domain": "hydrodynamics",
        }
        path = pipeline_module.determine_target_path(entry, ace_root="/mnt/ace")
        assert path == "/mnt/ace/downloads/papers/hydrodynamics"

    def test_standard_portal_path(self, pipeline_module):
        entry = {
            "id": "dnv_portal",
            "url": "https://www.dnv.com/standards",
            "type": "standard_portal",
            "domain": "structural",
        }
        path = pipeline_module.determine_target_path(entry, ace_root="/mnt/ace")
        assert path == "/mnt/ace/downloads/standards/structural"


# ===========================================================================
# 3. Dry-run mode
# ===========================================================================

class TestDryRunMode:
    """Dry-run should plan but not execute downloads."""

    @patch("subprocess.run")
    def test_dry_run_does_not_call_subprocess(self, mock_run, pipeline_module, sample_registry):
        """In dry-run, no subprocess calls should happen for actual downloads."""
        actions = pipeline_module.plan_downloads(
            sample_registry["entries"][:1],  # Just 1 github_repo
            ace_root="/tmp/fake-ace",
            dry_run=True,
        )
        # Should produce actions but subprocess should not be called
        mock_run.assert_not_called()
        assert len(actions) >= 1
        assert actions[0]["action"] in ("git_clone", "would_clone")

    def test_dry_run_actions_include_would_prefix(self, pipeline_module, sample_registry):
        """Dry-run actions should have a 'would_' prefix or dry_run flag."""
        filtered = pipeline_module.filter_downloadable(sample_registry["entries"])
        actions = pipeline_module.plan_downloads(
            filtered,
            ace_root="/tmp/fake-ace",
            dry_run=True,
        )
        for a in actions:
            assert a.get("dry_run") is True or a["action"].startswith("would_")


# ===========================================================================
# 4. Status update logic
# ===========================================================================

class TestStatusUpdate:
    """Registry YAML status updates after downloads."""

    def test_update_entry_status(self, pipeline_module):
        """After successful download, entry should be updated."""
        entry = {
            "id": "moordyn_repo",
            "download_status": "not_started",
            "local_backup_path": "",
            "last_checked": "2026-04-01",
        }
        updated = pipeline_module.update_entry_status(
            entry,
            new_status="downloaded",
            local_path="/mnt/ace/downloads/github_repos/marine_offshore/MoorDyn",
        )
        assert updated["download_status"] == "downloaded"
        assert updated["local_backup_path"] == "/mnt/ace/downloads/github_repos/marine_offshore/MoorDyn"
        # last_checked should be today's date
        today = datetime.now().strftime("%Y-%m-%d")
        assert updated["last_checked"] == today

    def test_manual_download_required_for_portals(self, pipeline_module):
        """Standard portals should be marked as manual_download_required."""
        entry = {
            "id": "dnv_portal",
            "type": "standard_portal",
            "download_status": "not_started",
            "local_backup_path": "",
            "last_checked": "2026-04-01",
        }
        updated = pipeline_module.update_entry_status(
            entry,
            new_status="manual_download_required",
            local_path="",
        )
        assert updated["download_status"] == "manual_download_required"

    def test_failed_download_status(self, pipeline_module):
        """Failed downloads should set status to 'failed'."""
        entry = {
            "id": "bad_paper",
            "download_status": "not_started",
            "local_backup_path": "",
            "last_checked": "2026-04-01",
        }
        updated = pipeline_module.update_entry_status(
            entry,
            new_status="failed",
            local_path="",
        )
        assert updated["download_status"] == "failed"


# ===========================================================================
# 5. Report generation
# ===========================================================================

class TestDownloadReport:
    """Download report markdown generation."""

    def test_report_contains_actions(self, pipeline_module):
        """Report should list all actions taken."""
        actions = [
            {"id": "repo1", "action": "would_clone", "target": "/mnt/ace/downloads/github_repos/marine/Repo1", "dry_run": True},
            {"id": "paper1", "action": "would_download", "target": "/mnt/ace/downloads/papers/hydro", "dry_run": True},
            {"id": "portal1", "action": "manual_download_required", "target": "", "dry_run": True},
        ]
        report = pipeline_module.generate_download_report(actions, dry_run=True)
        assert "repo1" in report
        assert "paper1" in report
        assert "portal1" in report
        assert "DRY RUN" in report or "dry run" in report.lower()

    def test_report_has_date(self, pipeline_module):
        """Report filename pattern uses YYYY-MM-DD."""
        actions = []
        report = pipeline_module.generate_download_report(actions, dry_run=False)
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in report


# ===========================================================================
# 6. Integration: registry loading
# ===========================================================================

class TestRegistryLoading:
    """Full pipeline registry load from YAML."""

    def test_load_registry(self, pipeline_module, registry_file):
        """Should load and return entries from YAML file."""
        data = pipeline_module.load_registry(str(registry_file))
        assert len(data["entries"]) == 5
        assert data["total_entries"] == 5
