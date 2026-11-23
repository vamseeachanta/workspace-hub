from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILDER_PATH = REPO_ROOT / "scripts/data/drive-index/build_drive_index.py"
SEARCH_DIR = REPO_ROOT / "scripts/data/drive-index-search"

sys.path.insert(0, str(SEARCH_DIR))


@pytest.fixture()
def builder():
    spec = importlib.util.spec_from_file_location("build_drive_index_refresh", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fixture_tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "drive"
    for rel in ["root-a/alpha.txt", "root-a/riser_vortex.dat", "root-b/beta.pdf"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"content {rel}")
    return {"root": root, "db": tmp_path / "index.db"}


@pytest.fixture()
def multi_root_config(tmp_path: Path, fixture_tree: dict[str, Path]) -> Path:
    config = {
        "version": 1,
        "drives": {
            "fixture": {
                "roots": [
                    str(fixture_tree["root"] / "root-a"),
                    str(fixture_tree["root"] / "root-b"),
                ],
                "canonical_prefix": "/mnt/fixture",  # abs-path-allowed
                "db": str(fixture_tree["db"]),
                "excludes": ["skip"],
                "classification": {
                    "defaults": {
                        "asset_type": "file",
                        "discipline": "general",
                        "engineering_domain": "general",
                        "content_category": "file",
                    },
                    "extensions": {".pdf": "document", ".dat": "data"},
                },
            }
        },
    }
    path = tmp_path / "drive-index-config.yaml"
    path.write_text(yaml.safe_dump(config))
    return path


@pytest.fixture()
def profile(builder, multi_root_config: Path):
    return builder.load_profile(multi_root_config, "fixture")


def rows(db: Path, sql: str, params=()):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()
