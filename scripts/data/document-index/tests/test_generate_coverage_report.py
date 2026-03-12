#!/usr/bin/env python3
"""TDD tests for generate-coverage-report.py."""
import subprocess
from pathlib import Path
import yaml
import pytest

HUB_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = HUB_ROOT / "scripts/data/document-index/generate-coverage-report.py"
OUTPUT = HUB_ROOT / "docs/document-intelligence/domain-coverage.md"


def _run(*args):
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(SCRIPT)] + list(args),
        cwd=HUB_ROOT, capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def test_dry_run_exits_zero():
    """--dry-run must exit 0."""
    rc, out, err = _run("--dry-run")
    assert rc == 0, f"dry-run failed: {err}"


def test_dry_run_contains_header():
    """--dry-run output must contain the report header."""
    rc, out, err = _run("--dry-run")
    assert "Domain Coverage Report" in out


def test_dry_run_contains_table():
    """--dry-run output must contain the markdown table header row."""
    rc, out, err = _run("--dry-run")
    assert "| Domain |" in out
    assert "| Total |" in out or "Total" in out


def test_writes_output_file():
    """Running without --dry-run must write domain-coverage.md."""
    rc, out, err = _run()
    assert rc == 0, f"Failed: {err}"
    assert OUTPUT.exists(), f"Output file not created: {OUTPUT}"
    content = OUTPUT.read_text()
    assert "Domain Coverage Report" in content


def test_compute_domain_stats():
    """compute_domain_stats groups correctly."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_report", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fake_standards = [
        {"domain": "pipeline", "status": "done", "exhausted": False},
        {"domain": "pipeline", "status": "gap", "exhausted": False},
        {"domain": "cathodic-protection", "status": "done", "exhausted": True},
    ]
    stats = mod.compute_domain_stats(fake_standards)
    assert stats["pipeline"]["total"] == 2
    assert stats["pipeline"]["done"] == 1
    assert stats["pipeline"]["gap"] == 1
    assert stats["cathodic-protection"]["exhausted"] == 1
    assert stats["cathodic-protection"]["done"] == 1
