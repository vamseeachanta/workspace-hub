"""Refresh failure propagation and configured storage, without production writes."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "scripts/data/drive-index/build_drive_index.py"
WRAPPER = ROOT / "scripts/data/drive-index/refresh-drive-index.sh"


def test_scan_error_is_a_nonzero_cli_exit(tmp_path):
    config = tmp_path / "profile.yaml"
    db = tmp_path / "private/index.db"
    config.write_text(yaml.safe_dump({"drives": {"synthetic": {
        "roots": [str(tmp_path / "missing")], "db": str(db),
        "canonical_prefix": "synthetic", "classification": {}}}}))
    env = {k: v for k, v in os.environ.items()
           if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    result = subprocess.run([sys.executable, str(BUILDER), "--config", str(config),
                             "--drive", "synthetic", "--incremental", "--prune"],
                            env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    state = json.loads((db.parent / "refresh-state.json").read_text())
    assert state["status"] == "failed"
    assert state["error_count"] == 1
    assert state["rows_pruned"] == 0
    assert "No such file" in state["scan_errors"][0]["reason"]


def test_wrapper_uses_override_and_preserves_scan_diagnostics(tmp_path):
    # Do not execute the legacy wrapper: it ignores overrides and selects live storage.
    assert "DRIVE_INDEX_CONFIG" in WRAPPER.read_text()
    config = tmp_path / "profile.yaml"
    staged = tmp_path / "repository/scripts/data/drive-index"
    staged.mkdir(parents=True)
    shutil.copy2(WRAPPER, staged / WRAPPER.name)
    shutil.copy2(BUILDER, staged / BUILDER.name)
    private = tmp_path / "private"
    private.mkdir()
    db = private / "index.db"
    import sqlite3
    sqlite3.connect(db).close()
    config.write_text(yaml.safe_dump({"drives": {"ace": {
        "roots": [str(tmp_path / "missing")], "db": str(db),
        "canonical_prefix": "synthetic", "classification": {}}}}))
    notify = tmp_path / "notify.log"
    env = {k: v for k, v in os.environ.items()
           if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "DRIVE_INDEX_TEST_MODE"}}
    env.update(DRIVE_INDEX_CONFIG=str(config), DRIVE_INDEX_NOTIFY_LOG=str(notify))
    result = subprocess.run(["bash", str(staged / WRAPPER.name), "ace"], env=env,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 1, result.stdout + result.stderr
    state = json.loads((private / "refresh-state.json").read_text())
    assert state["status"] == "failed"
    assert state["scan_errors"][0]["path"] == str(tmp_path / "missing")
    assert state["error_count"] == 1
    assert "\tfail\t" in notify.read_text()
    assert "\tpass\t" not in notify.read_text()

    available = tmp_path / "available"
    available.mkdir()
    (available / "synthetic.txt").write_text("synthetic metadata")
    profile = yaml.safe_load(config.read_text())
    profile["drives"]["ace"]["roots"] = [str(available)]
    config.write_text(yaml.safe_dump(profile))
    recovered = subprocess.run(["bash", str(staged / WRAPPER.name), "ace"], env=env,
                               capture_output=True, text=True, check=False)
    assert recovered.returncode == 0, recovered.stderr
    state = json.loads((private / "refresh-state.json").read_text())
    assert state["status"] == "ok"
    assert state["row_count"] == 1
    assert state["error_count"] == 0
    assert "wrapper_error" not in state
