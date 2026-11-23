from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILDER_PATH = REPO_ROOT / "scripts/data/drive-index/build_drive_index.py"


@pytest.fixture()
def builder():
    spec = importlib.util.spec_from_file_location("build_drive_index", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fixture_tree(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "dde"
    files = [
        "documents/readme.txt",
        "documents/zero.dat",
        "documents/riser_fatigue_report.pdf",
        "Orcaflex/model run/sim.dat",
        "ABSG/design calc.xlsx",
        "Literature/paper one.pdf",
        "g-drive/project & notes.docx",
        "o-drive/unicode_cafe.txt",
        "Temp - Oil&Gas/input.inp",
    ]
    for rel in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"" if "zero" in rel else f"content {rel}".encode())
    for rel in ["$RECYCLE.BIN/decoy.txt", "System Volume Information/secret.txt"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("skip")
    (root / "documents/link").symlink_to(root / "ABSG", target_is_directory=True)
    return {"root": root, "db": tmp_path / "index.db"}


@pytest.fixture()
def config_path(tmp_path: Path, fixture_tree: dict[str, Path]) -> Path:
    config = {
        "version": 1,
        "drives": {
            "dde": {
                "root": str(fixture_tree["root"]),
                "canonical_prefix": "/mnt/dde",  # abs-path-allowed
                "db": str(fixture_tree["db"]),
                "excludes": ["$RECYCLE.BIN", "System Volume Information", ".dde-knowledge"],
                "classification": {
                    "defaults": {
                        "asset_type": "file",
                        "discipline": "general",
                        "engineering_domain": "general",
                        "content_category": "file",
                    },
                    "topdirs": {
                        "Orcaflex": {
                            "discipline": "engineering",
                            "engineering_domain": "offshore_analysis",
                            "content_category": "simulation",
                        },
                        "ABSG": {
                            "discipline": "engineering",
                            "engineering_domain": "marine",
                            "content_category": "project",
                        },
                    },
                    "extensions": {".pdf": "document", ".xlsx": "spreadsheet", ".dat": "data"},
                },
            }
        },
    }
    path = tmp_path / "drive-index-config.yaml"
    path.write_text(yaml.safe_dump(config))
    return path


@pytest.fixture()
def profile(builder, config_path: Path):
    return builder.load_profile(config_path, "dde")


def rows(db: Path, sql: str, params=()):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def make_raw_byte_file(root: Path) -> None:
    parent = root / "documents"
    raw = os.fsencode(parent) + b"/bad_\xff_name.txt"
    fd = os.open(raw, os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, b"bad name")
    finally:
        os.close(fd)
