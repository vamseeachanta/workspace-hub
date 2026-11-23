"""Tests for calc-examples-mapper.py — 3 standard lookups."""
import subprocess
import sys
from pathlib import Path

import pytest

MAPPER = Path(__file__).parent / "calc-examples-mapper.py"
HUB_ROOT = Path(__file__).resolve().parents[3]
INDEX_FILE = HUB_ROOT / "data" / "document-index" / "index.jsonl"


def run_mapper(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MAPPER), *args],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(not INDEX_FILE.exists(), reason="index.jsonl not present")
class TestCalcExamplesMapper:
    def test_dnv_os_f101_outputs_yaml(self):
        result = run_mapper("--standard", "DNV-OS-F101", "--domain", "pipeline", "--top", "3")
        assert result.returncode == 0
        assert "- standard: DNV-OS-F101" in result.stdout
        assert "domain: pipeline" in result.stdout
        assert "files:" in result.stdout

    def test_api_rp_2a_wsd_structural(self):
        result = run_mapper("--standard", "API-RP-2A-WSD", "--domain", "structural", "--top", "3")
        assert result.returncode == 0
        assert "- standard: API-RP-2A-WSD" in result.stdout

    def test_dnv_rp_b401_cp(self):
        result = run_mapper("--standard", "DNV-RP-B401", "--domain", "cathodic-protection", "--top", "3")
        assert result.returncode == 0
        assert "- standard: DNV-RP-B401" in result.stdout

    def test_no_results_returns_comment(self):
        result = run_mapper("--standard", "NONEXISTENT-STD-9999", "--domain", "pipeline", "--top", "3")
        assert result.returncode == 0
        assert "No matching records" in result.stdout

    def test_top_flag_limits_output(self):
        result = run_mapper("--standard", "DNV-OS-F101", "--domain", "pipeline", "--top", "2")
        assert result.returncode == 0
        file_count = result.stdout.count("  - path:")
        assert file_count <= 2


@pytest.mark.skipif(not INDEX_FILE.exists(), reason="index.jsonl not present")
class TestQueryDocsExtensions:
    def test_calc_only_flag(self):
        """query-docs.sh --calc-only returns only CAL/RPT paths."""
        result = subprocess.run(
            ["bash", str(HUB_ROOT / "scripts" / "readiness" / "query-docs.sh"),
             "--calc-only", "--limit", "5", "--format", "paths"],
            capture_output=True, text=True, cwd=str(HUB_ROOT),
        )
        assert result.returncode == 0
        for line in result.stdout.strip().splitlines():
            if line and not line.startswith("#") and "/" in line:
                assert any(p in line for p in ["/CAL/", "-CAL-", "-RPT-"]), \
                    f"Non-calc path returned: {line}"

    def test_standard_flag(self):
        """query-docs.sh --standard DNV-OS-F101 returns relevant entries."""
        result = subprocess.run(
            ["bash", str(HUB_ROOT / "scripts" / "readiness" / "query-docs.sh"),
             "--standard", "DNV-OS-F101", "--limit", "5"],
            capture_output=True, text=True, cwd=str(HUB_ROOT),
        )
        assert result.returncode == 0
        assert "result(s)" in result.stdout
