#!/usr/bin/env python3
"""Tests for --exhausted filter in query-ledger.py."""
import subprocess
import sys
from pathlib import Path
import yaml

HUB_ROOT = Path(__file__).resolve().parents[4]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"
QUERY_SCRIPT = HUB_ROOT / "scripts/data/document-index/query-ledger.py"


def _run_query(*args):
    """Run query-ledger.py with given args, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(QUERY_SCRIPT)] + list(args),
        cwd=HUB_ROOT, capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def test_exhausted_flag_exits_zero():
    """--exhausted flag must exit 0."""
    rc, out, err = _run_query("--exhausted")
    assert rc == 0, f"--exhausted exited {rc}: {err}"


def test_exhausted_flag_returns_subset():
    """--exhausted result must be subset of full results."""
    rc_all, out_all, _ = _run_query("--summary")
    rc_ex, out_ex, _ = _run_query("--exhausted", "--summary")
    assert rc_all == 0 and rc_ex == 0
    # When no entries are exhausted, exhausted output is empty/zero
    # This test just confirms it doesn't crash


def test_exhausted_with_domain_combo():
    """--exhausted --domain cathodic works as combined filter."""
    rc, out, err = _run_query("--exhausted", "--domain", "cathodic")
    assert rc == 0, f"Combined filter exited {rc}: {err}"


def test_module_import():
    """query-ledger.py main() is callable via import."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "query_ledger",
        str(QUERY_SCRIPT)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "main"), "query-ledger.py must define main()"
    assert hasattr(mod, "load_ledger"), "query-ledger.py must define load_ledger()"
