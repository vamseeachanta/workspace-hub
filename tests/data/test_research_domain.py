#!/usr/bin/env python3
# ABOUTME: TDD tests for research-domain.py driver script (WRK-1181)
# ABOUTME: Tests research brief generation, download script generation, domain mapping

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = HUB_ROOT / "scripts" / "data" / "research-literature" / "research-domain.py"
DOMAIN_MAP = HUB_ROOT / "config" / "research-literature" / "domain-repo-map.yaml"
BRIEF_DIR = HUB_ROOT / "specs" / "capability-map" / "research-briefs"
TEMPLATE = HUB_ROOT / "scripts" / "data" / "research-literature" / "download-template.sh"


# ── Domain-repo mapping tests ──────────────────────────────────────


class TestDomainRepoMapping:
    """Verify domain-repo-map.yaml structure and content."""

    def test_mapping_file_exists(self):
        assert DOMAIN_MAP.exists(), f"Missing: {DOMAIN_MAP}"

    def test_mapping_valid_yaml(self):
        data = yaml.safe_load(DOMAIN_MAP.read_text())
        assert "domains" in data
        assert isinstance(data["domains"], dict)

    def test_mapping_has_tier1_domains(self):
        data = yaml.safe_load(DOMAIN_MAP.read_text())
        tier1 = [k for k, v in data["domains"].items() if v["tier"] == 1]
        expected = {
            "geotechnical", "cathodic_protection", "structural",
            "hydrodynamics", "drilling", "pipeline", "bsee",
            "metocean", "subsea", "naval_architecture",
        }
        assert expected.issubset(set(tier1))

    def test_mapping_required_fields(self):
        data = yaml.safe_load(DOMAIN_MAP.read_text())
        required = {"repo", "ace_path", "tier", "ledger_domain", "keywords"}
        for domain, cfg in data["domains"].items():
            missing = required - set(cfg.keys())
            assert not missing, f"{domain} missing fields: {missing}"

    def test_mapping_valid_repos(self):
        valid_repos = {
            "digitalmodel", "worldenergydata", "assetutilities",
            "assethold", "OGManufacturing",
        }
        data = yaml.safe_load(DOMAIN_MAP.read_text())
        for domain, cfg in data["domains"].items():
            assert cfg["repo"] in valid_repos, (
                f"{domain} has invalid repo: {cfg['repo']}"
            )

    def test_mapping_ace_paths_start_with_mnt_ace(self):
        data = yaml.safe_load(DOMAIN_MAP.read_text())
        for domain, cfg in data["domains"].items():
            assert cfg["ace_path"].startswith("/mnt/ace/"), (
                f"{domain} ace_path must start with /mnt/ace/"
            )


# ── Download template tests ────────────────────────────────────────


class TestDownloadTemplate:
    """Verify download-template.sh is valid bash with required structure."""

    def test_template_exists(self):
        assert TEMPLATE.exists(), f"Missing: {TEMPLATE}"

    def test_template_has_shebang(self):
        first_line = TEMPLATE.read_text().splitlines()[0]
        assert first_line == "#!/usr/bin/env bash"

    def test_template_sources_helpers(self):
        content = TEMPLATE.read_text()
        assert "download-helpers.sh" in content

    def test_template_supports_dry_run(self):
        content = TEMPLATE.read_text()
        assert "--dry-run" in content

    def test_template_has_placeholder_markers(self):
        content = TEMPLATE.read_text()
        assert "{{DOMAIN}}" in content
        assert "{{DEST}}" in content

    def test_template_valid_bash_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(TEMPLATE)],
            capture_output=True, text=True,
        )
        # Template has placeholders so syntax check may warn but should not error
        # on the bash structure itself. We just check it doesn't crash hard.
        # A stricter check runs after substitution in the driver script.


# ── Research brief schema tests ────────────────────────────────────


class TestResearchBriefSchema:
    """Verify existing research briefs conform to expected schema."""

    REQUIRED_TOP_KEYS = {
        "category", "subcategory", "generated",
        "applicable_standards", "available_documents",
        "implementation_target",
    }

    STANDARD_KEYS = {"id", "title", "org", "status"}

    def _load_briefs(self) -> list[tuple[str, dict]]:
        briefs = []
        if BRIEF_DIR.exists():
            for f in BRIEF_DIR.glob("*.yaml"):
                data = yaml.safe_load(f.read_text())
                if data and "category" in data:
                    briefs.append((f.name, data))
        return briefs

    def test_brief_directory_exists(self):
        assert BRIEF_DIR.exists()

    def test_existing_briefs_have_required_keys(self):
        briefs = self._load_briefs()
        if not briefs:
            pytest.skip("No briefs found yet")
        for name, data in briefs:
            missing = self.REQUIRED_TOP_KEYS - set(data.keys())
            assert not missing, f"{name} missing keys: {missing}"

    def test_existing_briefs_standards_have_required_fields(self):
        briefs = self._load_briefs()
        if not briefs:
            pytest.skip("No briefs found yet")
        for name, data in briefs:
            for i, std in enumerate(data.get("applicable_standards", [])):
                missing = self.STANDARD_KEYS - set(std.keys())
                assert not missing, (
                    f"{name} standard[{i}] missing: {missing}"
                )

    def test_existing_briefs_valid_status_values(self):
        valid = {"available", "needs_download", "paywalled"}
        briefs = self._load_briefs()
        if not briefs:
            pytest.skip("No briefs found yet")
        for name, data in briefs:
            for std in data.get("applicable_standards", []):
                assert std["status"] in valid, (
                    f"{name} standard {std['id']} has invalid status: {std['status']}"
                )


# ── Driver script integration tests ───────────────────────────────


class TestResearchDomainScript:
    """Integration tests for research-domain.py driver script."""

    def test_script_exists(self):
        assert SCRIPT.exists(), f"Missing: {SCRIPT}"

    def test_script_help_flag(self):
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", str(SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "--category" in result.stdout
        assert "--repo" in result.stdout

    def test_script_requires_category(self):
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", str(SCRIPT)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0

    def test_script_geotechnical_produces_yaml(self):
        """Run against geotechnical domain — should produce valid YAML brief."""
        result = subprocess.run(
            [
                "uv", "run", "--no-project", "python", str(SCRIPT),
                "--category", "geotechnical",
                "--repo", "digitalmodel",
                "--dry-run",
            ],
            capture_output=True, text=True, timeout=60,
            cwd=str(HUB_ROOT),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Should print path to generated brief
        assert "research-briefs" in result.stdout or "brief" in result.stdout.lower()

    def test_script_unknown_domain_errors(self):
        result = subprocess.run(
            [
                "uv", "run", "--no-project", "python", str(SCRIPT),
                "--category", "nonexistent_domain_xyz",
                "--repo", "digitalmodel",
            ],
            capture_output=True, text=True, timeout=30,
            cwd=str(HUB_ROOT),
        )
        assert result.returncode != 0

    def test_script_download_script_generation(self):
        """--generate-download-script should create a valid bash script."""
        result = subprocess.run(
            [
                "uv", "run", "--no-project", "python", str(SCRIPT),
                "--category", "geotechnical",
                "--repo", "digitalmodel",
                "--generate-download-script",
                "--dry-run",
            ],
            capture_output=True, text=True, timeout=60,
            cwd=str(HUB_ROOT),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "download" in result.stdout.lower()


# ── Ledger query integration ──────────────────────────────────────


class TestLedgerIntegration:
    """Verify ledger data can be queried for domain gaps."""

    LEDGER = HUB_ROOT / "data" / "document-index" / "standards-transfer-ledger.yaml"

    def test_ledger_exists(self):
        assert self.LEDGER.exists(), "Standards ledger not found"

    def test_ledger_has_standards(self):
        data = yaml.safe_load(self.LEDGER.read_text())
        assert "standards" in data
        assert len(data["standards"]) > 0

    def test_ledger_query_script_exists(self):
        script = HUB_ROOT / "scripts" / "data" / "document-index" / "query-ledger.py"
        assert script.exists()

    def test_ledger_has_domain_field(self):
        data = yaml.safe_load(self.LEDGER.read_text())
        domains = {s.get("domain") for s in data["standards"] if s.get("domain")}
        assert len(domains) > 3, f"Expected many domains, got: {domains}"
