"""Tests for scripts/hygiene/fleet_baseline.py (#4532)."""

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/fleet_baseline.py"


def load():
    spec = importlib.util.spec_from_file_location("fleet_baseline", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ssh_command_quotes_arguments_and_appends_label():
    fb = load()
    cmd = fb.build_command({"label": "h1", "ssh": "alias-1", "python": "python3",
                            "args": ["--roots", "D:/Discovery Projects"]})
    assert cmd[:2] == ["ssh", "-o"] and "alias-1" in cmd
    remote = cmd[-1]
    assert remote.startswith("python3 - ")
    assert "'D:/Discovery Projects'" in remote
    assert remote.endswith("--label h1")


def test_local_host_runs_without_ssh():
    fb = load()
    cmd = fb.build_command({"label": "here", "ssh": None, "args": ["--no-git"]})
    assert cmd[0] == sys.executable and "ssh" not in cmd
    assert cmd[-2:] == ["--label", "here"]


def test_run_writes_per_host_json_and_summary(tmp_path):
    fb = load()
    root = tmp_path / "root"
    (root / "big").mkdir(parents=True)
    (root / "big" / "f.bin").write_bytes(b"x" * 1000)
    (root / "tmp").mkdir()
    cfg = {"out_dir": str(tmp_path / "out"), "hosts": [{
        "label": "local-a", "ssh": None,
        "args": ["--roots", str(root), "--depth", "1", "--no-git", "--no-caches"]}]}
    run_dir = fb.run(cfg, date="2026-11-25")
    doc = json.loads((run_dir / "local-a.json").read_text(encoding="utf-8"))
    assert doc["label"] == "local-a"
    summary = (run_dir / "summary.md").read_text(encoding="utf-8")
    assert "local-a" in summary and "Disks" in summary


def test_failed_host_is_reported_not_dropped(tmp_path):
    fb = load()
    cfg = {"out_dir": str(tmp_path / "out"), "hosts": [{
        "label": "broken", "ssh": None, "python": sys.executable,
        "args": ["--depth", "not-a-number"]}]}
    run_dir = fb.run(cfg, date="2026-11-25")
    assert (run_dir / "broken.err").exists()
    assert "broken" in (run_dir / "summary.md").read_text(encoding="utf-8")
    assert "FAILED" in (run_dir / "summary.md").read_text(encoding="utf-8")
