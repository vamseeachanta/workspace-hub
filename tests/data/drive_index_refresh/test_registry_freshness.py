from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from registry import RegistryError, load_registry


def _registry(tmp_path: Path, freshness: dict | None) -> Path:
    data = {
        "version": 1,
        "defaults": {"staleness_days": 90},
        "indexes": [
            {
                "id": "idx",
                "adapter": "jsonl",
                "path": "index.jsonl",
                "coverage": {"drives": ["/fixture"]},
                "freshness": freshness or {"built_at": "2026-01-01"},
                "builder": "builder.py",
                "adapter_params": {"path_field": "path", "search_fields": ["path"]},
            }
        ],
    }
    path = tmp_path / "registry.yml"
    path.write_text(yaml.safe_dump(data))
    (tmp_path / "index.jsonl").write_text("")
    return path


def test_registry_accepts_freshness_fields(tmp_path):
    path = _registry(
        tmp_path,
        {
            "built_at": "2026-03-26",
            "staleness_days": 14,
            "row_count": 1188891,
            "as_of": "2026-07-02",
            "state_file": "/mnt/ace/.ace-knowledge/refresh-state.json",  # abs-path-allowed
        },
    )

    registry = load_registry(path)

    assert registry.get("idx").freshness["row_count"] == 1188891


def test_registry_rejects_bad_freshness_types(tmp_path):
    path = _registry(tmp_path, {"built_at": "2026-03-26", "row_count": "many"})

    with pytest.raises(RegistryError, match="idx.*row_count"):
        load_registry(path)


def test_registry_freshness_fields_optional(tmp_path):
    path = _registry(tmp_path, {"built_at": "2026-03-26"})

    assert load_registry(path).get("idx").freshness["built_at"] == "2026-03-26"
