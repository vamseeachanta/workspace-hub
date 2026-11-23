#!/usr/bin/env python3
"""TDD tests for mark-exhausted.py."""
import copy
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml
import pytest

HUB_ROOT = Path(__file__).resolve().parents[4]
LEDGER = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"
SCRIPT = HUB_ROOT / "scripts/data/document-index/mark-exhausted.py"


def _load_ledger():
    with open(LEDGER) as f:
        return yaml.safe_load(f)


def _save_ledger(data: dict, path: Path) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def test_mark_exhausted_dry_run():
    """--dry-run must not modify the ledger."""
    data_before = _load_ledger()
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(SCRIPT),
         "--dry-run", "API-RP-1109", "digitalmodel/src/digitalmodel/cathodic_protection/api_rp_1109.py"],
        cwd=HUB_ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f"dry-run failed: {result.stderr}"
    data_after = _load_ledger()
    # Ledger should be unchanged
    assert data_before["standards"] == data_after["standards"], "dry-run must not modify ledger"


def test_find_entry_exact_match():
    """find_entry should locate an entry by exact ID."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mark_exhausted", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fake_standards = [{"id": "API-RP-1632", "exhausted": False}]
    result = mod.find_entry(fake_standards, "API-RP-1632")
    assert result is not None
    assert result["id"] == "API-RP-1632"


def test_find_entry_case_insensitive():
    """find_entry should match case-insensitively."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mark_exhausted", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fake_standards = [{"id": "API-RP-1632", "exhausted": False}]
    result = mod.find_entry(fake_standards, "api-rp-1632")
    assert result is not None


def test_find_entry_missing_returns_none():
    """find_entry returns None for unknown ID."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mark_exhausted", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fake_standards = [{"id": "API-RP-1632", "exhausted": False}]
    result = mod.find_entry(fake_standards, "DOES-NOT-EXIST-ZZZ")
    assert result is None


def test_mark_exhausted_modifies_fields_in_memory():
    """mark_exhausted correctly sets fields (using a temp ledger)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mark_exhausted", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Build a minimal in-memory ledger entry
    fake_entry = {
        "id": "TEST-ENTRY-001",
        "exhausted": False,
        "exhausted_at": None,
        "absorbed_into": [],
    }

    # Write to temp file and patch LEDGER
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump({"standards": [fake_entry]}, f)
        tmp_path = Path(f.name)

    original_ledger = mod.LEDGER
    mod.LEDGER = tmp_path
    try:
        mod.mark_exhausted("TEST-ENTRY-001", ["digitalmodel/src/digitalmodel/cathodic_protection/x.py"])
        data = yaml.safe_load(tmp_path.read_text())
        entry = data["standards"][0]
        assert entry["exhausted"] is True
        assert entry["exhausted_at"] is not None
        assert "digitalmodel/src/digitalmodel/cathodic_protection/x.py" in entry["absorbed_into"]
    finally:
        mod.LEDGER = original_ledger
        tmp_path.unlink(missing_ok=True)
