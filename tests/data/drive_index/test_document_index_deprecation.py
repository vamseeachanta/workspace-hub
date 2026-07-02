from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE_A = REPO_ROOT / "scripts/data/document-index/phase-a-index.py"
CONFIG = REPO_ROOT / "scripts/data/document-index/config.yaml"


def test_config_dde_source_disabled():
    cfg = yaml.safe_load(CONFIG.read_text())
    assert cfg["sources"]["dde_project"]["enabled"] is False
    assert "DROPS all 495,487 dde rows" in CONFIG.read_text()
    assert "/mnt/dde/.dde-knowledge/index.db" in CONFIG.read_text()  # abs-path-allowed


def test_force_rebuild_retention_semantics(tmp_path: Path):
    index = tmp_path / "index.jsonl"
    index.write_text(
        json.dumps({"path": "/mnt/dde/documents/legacy.pdf", "source": "dde_project"}) + "\n"  # abs-path-allowed
    )
    cfg = {
        "output": {"index_path": str(index)},
        "sources": {"dde_project": {"enabled": False, "paths": []}},
        "exclude_patterns": [],
        "cad_extensions": [],
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    subprocess.run([sys.executable, str(PHASE_A), "--config", str(cfg_path)], check=True)
    resume_rows = [json.loads(line) for line in index.read_text().splitlines()]
    assert [row["path"] for row in resume_rows] == ["/mnt/dde/documents/legacy.pdf"]  # abs-path-allowed

    index.write_text(
        json.dumps({"path": "/mnt/dde/documents/legacy.pdf", "source": "dde_project"}) + "\n"  # abs-path-allowed
    )
    subprocess.run([sys.executable, str(PHASE_A), "--config", str(cfg_path), "--force"], check=True)
    assert index.read_text().strip() == ""
