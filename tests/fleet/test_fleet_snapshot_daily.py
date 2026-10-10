"""Integration tests for the daily fleet snapshot writer wrapper."""

from __future__ import annotations

import json
import os
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
    _run(["git", "init", "-b", "main"], repo, check=True)
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


def test_daily_writer_commit_failure_restores_latest(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")
    before = (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_bytes()
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)

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
    assert _run(["git", "status", "--short"], repo, check=True).stdout == ""


def test_daily_writer_refuses_to_commit_other_staged_paths(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")
    other = repo / "README.md"
    other.write_text("staged but not owned\n", encoding="utf-8")
    _run(["git", "add", "README.md"], repo, check=True)
    before = (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_bytes()

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

    assert result.returncode == 2
    assert (repo / "docs" / "reports" / "fleet-snapshots" / "latest.json").read_bytes() == before
    assert _run(["git", "diff", "--cached", "--name-only"], repo, check=True).stdout == "README.md\n"


def test_daily_writer_refuses_non_main_branch(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")
    _run(["git", "checkout", "-b", "feature/test"], repo, check=True)

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

    assert result.returncode == 2
    assert "must run on main" in result.stderr


def test_daily_writer_keeps_collector_output_out_of_wrapper_log(tmp_path: Path) -> None:
    repo, map_path = _make_repo(tmp_path)
    source = tmp_path / "raw-snapshot.json"
    source.write_text(json.dumps(_snapshot("phys-box-b"), indent=2) + "\n", encoding="utf-8")
    collector = tmp_path / "collector.sh"
    collector.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'synthetic-hostname-shaped-output ws77'\n"
        "cp \"$1\" \"$FLEET_SNAPSHOT_OUT\"\n",
        encoding="utf-8",
    )
    collector.chmod(0o755)

    result = _run(
        ["bash", str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh")],
        repo,
        env={
            "FLEET_HUB": str(repo),
            "FLEET_LABEL_MAP": str(map_path),
            "FLEET_SNAPSHOT_COLLECT_CMD": f"{shlex.quote(str(collector))} {shlex.quote(str(source))}",
            "FLEET_NO_PUSH": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    assert "ws77" not in result.stdout + result.stderr


def test_print_scheduler_entry_uses_absolute_paths(tmp_path: Path) -> None:
    repo, _ = _make_repo(tmp_path)

    result = _run(
        ["bash", str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh"), "--print-scheduler-entry"],
        repo,
        env={"FLEET_HUB": str(repo), "PATH": os.environ["PATH"]},
    )

    assert result.returncode == 0
    assert "$WORKSPACE_HUB" not in result.stdout
    assert str(repo / "scripts" / "fleet" / "fleet-snapshot-daily.sh") in result.stdout
    assert str(repo / "logs" / "fleet" / "fleet-snapshot-daily.log") in result.stdout


def test_daily_writer_and_account_usage_cron_share_publish_lock() -> None:
    daily = SCRIPT.read_text(encoding="utf-8")
    account = (ROOT / "scripts" / "fleet" / "account-usage-cron.sh").read_text(
        encoding="utf-8"
    )

    assert "fleet-publish.lock" in daily
    assert "fleet-publish.lock" in account
    assert "flock" in daily
    assert "flock" in account
