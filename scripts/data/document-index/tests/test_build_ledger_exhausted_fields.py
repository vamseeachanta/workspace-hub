#!/usr/bin/env python3
"""Tests that build-ledger.py entry templates include exhausted fields."""
import subprocess
import sys
from pathlib import Path
import yaml

HUB_ROOT = Path(__file__).resolve().parents[4]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"


def test_ledger_entries_have_exhausted_fields():
    """Every ledger entry must have exhausted, exhausted_at, absorbed_into fields."""
    if not LEDGER.exists():
        # Regenerate
        result = subprocess.run(
            ["uv", "run", "--no-project", "python",
             "scripts/data/document-index/build-ledger.py"],
            cwd=HUB_ROOT, capture_output=True, text=True
        )
        assert result.returncode == 0, f"build-ledger.py failed: {result.stderr}"

    with open(LEDGER) as f:
        data = yaml.safe_load(f)

    standards = data.get("standards", [])
    assert len(standards) > 0, "Ledger must have entries"

    for s in standards[:20]:  # check first 20 for speed
        assert "exhausted" in s, f"Entry {s.get('id')} missing 'exhausted' field"
        assert "exhausted_at" in s, f"Entry {s.get('id')} missing 'exhausted_at' field"
        assert "absorbed_into" in s, f"Entry {s.get('id')} missing 'absorbed_into' field"
        assert s["exhausted"] is False, f"Entry {s.get('id')} exhausted should default to False"
        assert s["exhausted_at"] is None, \
            f"Entry {s.get('id')} exhausted_at should default to None"
        assert s["absorbed_into"] == [], \
            f"Entry {s.get('id')} absorbed_into should default to []"


def test_exhausted_field_type():
    """exhausted field must be boolean, not string or int."""
    with open(LEDGER) as f:
        data = yaml.safe_load(f)
    standards = data.get("standards", [])
    for s in standards[:20]:
        assert isinstance(s.get("exhausted"), bool), \
            f"Entry {s.get('id')}: exhausted must be bool, got {type(s.get('exhausted'))}"
