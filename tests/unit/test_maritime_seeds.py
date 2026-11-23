"""
ABOUTME: TDD schema validation tests for maritime law knowledge seed files — WRK-1126
ABOUTME: Validates YAML structure, required fields, counts, and uniqueness
"""

import pytest
import yaml
from pathlib import Path

SEEDS_DIR = Path(__file__).parents[2] / "knowledge" / "seeds"
CASES_FILE = SEEDS_DIR / "maritime-law-cases.yaml"
LIABILITIES_FILE = SEEDS_DIR / "maritime-liabilities.yaml"

REQUIRED_FIELDS = {"id", "category", "subcategory", "title", "learned_at", "source", "context"}


def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def test_maritime_cases_required_fields():
    """Every case entry must have all required metadata fields."""
    data = _load_yaml(CASES_FILE)
    entries = data.get("entries", [])
    assert entries, "maritime-law-cases.yaml must have at least one entry"
    for entry in entries:
        missing = REQUIRED_FIELDS - set(entry.keys())
        assert not missing, f"Entry {entry.get('id', '?')} missing fields: {missing}"


def test_maritime_cases_minimum_count():
    """maritime-law-cases.yaml must contain at least 10 entries."""
    data = _load_yaml(CASES_FILE)
    entries = data.get("entries", [])
    assert len(entries) >= 10, f"Expected ≥10 case entries, got {len(entries)}"


def test_maritime_liabilities_minimum_count():
    """maritime-liabilities.yaml must contain at least 5 entries."""
    data = _load_yaml(LIABILITIES_FILE)
    entries = data.get("entries", [])
    assert len(entries) >= 5, f"Expected ≥5 liability entries, got {len(entries)}"


def test_category_is_maritime_law():
    """All entries in both files must have category == 'maritime-law'."""
    for path in (CASES_FILE, LIABILITIES_FILE):
        data = _load_yaml(path)
        for entry in data.get("entries", []):
            assert entry.get("category") == "maritime-law", (
                f"Entry {entry.get('id', '?')} in {path.name} "
                f"has category={entry.get('category')!r}, expected 'maritime-law'"
            )


def test_cases_ids_are_unique():
    """No duplicate IDs across both seed files."""
    all_ids = []
    for path in (CASES_FILE, LIABILITIES_FILE):
        data = _load_yaml(path)
        for entry in data.get("entries", []):
            eid = entry.get("id", "")
            assert eid, f"Entry in {path.name} has empty or missing id"
            all_ids.append(eid)
    duplicates = {eid for eid in all_ids if all_ids.count(eid) > 1}
    assert not duplicates, f"Duplicate IDs found across seed files: {duplicates}"
