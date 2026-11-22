"""Inventory expectations follow the test_*.py convention in pyproject.toml.

All expected counts are independent counts of the literal fixture paths below.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "scripts/ci/hub_test_inventory.py"


def load_inventory():
    spec = importlib.util.spec_from_file_location("hub_inventory", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree(root, paths):
    for name in paths:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_ok():\n    pass\n", encoding="utf-8")


def test_grouping_and_counts(tmp_path):
    """Hand count: data has two files; the other four families have one each."""
    tree(tmp_path, [
        "tests/data/test_a.py", "tests/data/deep/test_b.py",
        "tests/test_root.py", "scripts/data/nested/tests/test_c.py",
        "scripts/ci/tests/test_d.py", "coordination/tests/test_e.py",
        "tests/data/helper.py", "other/tests/test_ignored.py",
    ])
    result = load_inventory().inventory(tmp_path)
    assert result["file_count"] == 6
    assert result["families"] == {
        "coordination/tests": ["coordination/tests/test_e.py"],
        "scripts/ci/tests": ["scripts/ci/tests/test_d.py"],
        "scripts/data/tests": ["scripts/data/nested/tests/test_c.py"],
        "tests/data": ["tests/data/deep/test_b.py", "tests/data/test_a.py"],
        "tests/root": ["tests/test_root.py"],
    }


def test_drift_check(tmp_path):
    """One generated file agrees; adding a second file must fail the check."""
    tree(tmp_path, ["tests/data/test_a.py"])
    target = tmp_path / "inventory.json"
    command = [sys.executable, "-I", str(SOURCE), "--root", str(tmp_path),
               "--output", str(target)]
    assert subprocess.run(command, capture_output=True, check=False).returncode == 0
    before = target.read_bytes()
    assert subprocess.run([*command, "--check"], capture_output=True, check=False).returncode == 0
    tree(tmp_path, ["tests/data/test_new.py"])
    assert subprocess.run([*command, "--check"], capture_output=True, check=False).returncode == 1
    assert target.read_bytes() == before


def test_missing_inventory_is_drift(tmp_path):
    command = [sys.executable, "-I", str(SOURCE), "--root", str(tmp_path),
               "--output", str(tmp_path / "missing.json"), "--check"]
    assert subprocess.run(command, capture_output=True, check=False).returncode == 1


def test_symlinks_and_cache_trees_are_not_tests(tmp_path):
    tree(tmp_path, ["tests/data/test_a.py", "tests/.venv/test_b.py"])
    (tmp_path / "tests/test_link.py").symlink_to(tmp_path / "tests/data/test_a.py")
    result = load_inventory().inventory(tmp_path)
    assert result["file_count"] == 1


def test_stable_serialization(tmp_path):
    tree(tmp_path, ["tests/z/test_b.py", "tests/a/test_a.py"])
    module = load_inventory()
    first = module.serialize(module.inventory(tmp_path))
    assert first == module.serialize(module.inventory(tmp_path))
    assert json.loads(first)["file_count"] == 2
