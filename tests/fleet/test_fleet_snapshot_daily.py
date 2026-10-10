"""Integration tests for the daily fleet snapshot writer wrapper."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "fleet" / "fleet-snapshot-daily.sh"
LABELLER = ROOT / "scripts" / "fleet" / "fleet_snapshot_labels.py"

MAP_TEXT = """\
collector-x fleet-collector
phys-box-a ace-win-1
phys-box-b ace-linux-1
"""


def _snapshot(name: str = "phys-box-a") -> dict:
    return {
        "generated_at": "2026-10-10T00:00:00+00:00",
        "generated_by": "collector-x fleet-daily-collector",
        "date": "2026-10-10",
        "origin_main": "abcdef123",
        "fleet_size": 1,
        "reporting": 1,
        "report": {"latest_snapshot": "2026-10-10", "stale_days": 0},
        "machines": [
            {
                "name": name,
                "reachable": True,
                "branch": "main",
                "head": "abcdef123",
                "behind": 0,
                "ahead": 0,
                "dirty": 0,
            }
        ],
    }


def _run(cmd: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess:
    check = kwargs.pop("check", False)
    return subprocess.run(
        cmd, check=check, cwd=cwd, text=True, capture_output=True, **kwargs
    )


def _make_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "scripts" / "fleet").mkdir(parents=True)
    (repo / "docs" / "reports" / "fleet-snapshots").mkdir(parents=True)
    shutil.copy2(LABELLER, repo / "scripts" / "fleet" / "fleet_snapshot_labels.py")
    shutil.copy2(SCRIPT, repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh")
    map_path = tmp_path / "fleet-label-map.txt"
    map_path.write_text(MAP_TEXT, encoding="utf-8")
    latest = repo / "docs" / "reports" / "fleet-snapshots" / "latest.json"
    latest.write_text(json.dumps(_snapshot("ace-win-1"), indent=2) + "\n", encoding="utf-8")
    _run(["git", "init"], repo, check=True)
    _run(["git", "config", "user.email", "test@example.invalid"], repo, check=True)
    _run(["git", "config", "user.name", "Test Writer"], repo, check=True)
    _run(["git", "add", "."], repo, check=True)
    _run(["git", "commit", "-m", "seed latest"], repo, check=True)
    return repo, map_path


def test_daily_writer_overwrites_latest_only_after_labelling(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")

    result = _run(
        ["bash", str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh")],
        repo,
        env={
            "FLEET_HUB": str(repo),
            "FLEET_LABEL_MAP": str(map_path),
            "FLEET_SNAPSHOT_SOURCE": str(source),
            "FLEET_NO_PUSH": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    snap_dir = repo / "docs" / "reports" / "fleet-snapshots"
    assert sorted(p.name for p in snap_dir.glob("*.json")) == ["latest.json"]
    latest = json.loads((snap_dir / "latest.json").read_text(encoding="utf-8"))
    assert latest["generated_by"].split()[0] == "fleet-collector"
    assert [machine["name"] for machine in latest["machines"]] == ["ace-linux-1"]
    assert _run(["git", "status", "--short"], repo, check=True).stdout == ""
    assert _run(["git", "rev-list", "--count", "HEAD"], repo, check=True).stdout.strip() == "2"


def test_daily_writer_collect_command_writes_to_temp_output(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")

    result = _run(
        ["bash", str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh")],
        repo,
        env={
            "FLEET_HUB": str(repo),
            "FLEET_LABEL_MAP": str(map_path),
            "FLEET_SNAPSHOT_COLLECT_CMD": f"cp {shlex.quote(str(source))} \"$FLEET_SNAPSHOT_OUT\"",
            "FLEET_NO_PUSH": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    latest = json.loads(
        (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_text(
            encoding="utf-8"
        )
    )
    assert [machine["name"] for machine in latest["machines"]] == ["ace-linux-1"]
    assert _run(["git", "status", "--short"], repo, check=True).stdout == ""


def test_daily_writer_labeller_failure_leaves_latest_uncommitted(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("unknown-box"), indent=2) + "\n", encoding="utf-8")
    before = (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_bytes()
    head = _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout.strip()

    result = _run(
        ["bash", str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh")],
        repo,
        env={
            "FLEET_HUB": str(repo),
            "FLEET_LABEL_MAP": str(map_path),
            "FLEET_SNAPSHOT_SOURCE": str(source),
            "FLEET_NO_PUSH": "1",
        },
    )

    assert result.returncode != 0
    assert (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_bytes() == before
    assert _run(["git", "rev-parse", "HEAD"], repo, check=True).stdout.strip() == head
    assert _run(["git", "status", "--short"], repo, check=True).stdout == ""
