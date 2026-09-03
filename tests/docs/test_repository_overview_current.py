from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "repositories" / "work_surface_inventory.py"
JSON_REPORT = ROOT / "docs" / "reports" / "work-surface-inventory.json"
OVERVIEW = ROOT / "docs" / "WORKSPACE_HUB_REPOSITORY_OVERVIEW.md"


def _module():
    spec = importlib.util.spec_from_file_location("work_surface_inventory", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_repository_overview_is_rendered_from_committed_inventory():
    inventory = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert OVERVIEW.read_text(encoding="utf-8") == _module().render_markdown(inventory)
    overview = OVERVIEW.read_text(encoding="utf-8")
    assert "| State |" in overview
    assert "declared-missing" in overview
    assert "observed-unregistered" in overview


def test_committed_inventory_is_public_safe():
    inventory = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    encoded = JSON_REPORT.read_text(encoding="utf-8")
    assert inventory["schema_version"] == 1
    assert set(inventory) == {"repositories", "schema_version", "summary"}
    assert set(inventory["summary"]) >= {
        "configured", "present", "missing", "non_git", "unknown", "adapter_coverage"
    }
    assert "/Users/" not in encoded and "/mnt/" not in encoded
    assert "https://" not in encoded and "git@" not in encoded
    assert all(item["name"] for item in inventory["repositories"])
