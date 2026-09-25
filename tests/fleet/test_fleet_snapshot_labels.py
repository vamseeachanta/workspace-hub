"""Tests for scripts/fleet/fleet_snapshot_labels.py (owner decision C18).

The fleet-daily-collector publishes docs/reports/fleet-snapshots/<date>.json to
this PUBLIC repository. The labeller rewrites every machine name to its logical
fleet label from a private map read at run time, and fails closed: a missing or
malformed map, or a name the map does not know, leaves the file untouched and
exits non-zero, so the collector's commit step never runs.

The physical names below are synthetic and chosen so they do not match the
identifier gate's hostname pattern.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "fleet" / "fleet_snapshot_labels.py"

sys.path.insert(0, str(SCRIPT.parent))
import fleet_snapshot_labels as fsl  # noqa: E402

MAP_TEXT = """\
# physical-name  logical-label
PHYS-BOX-A   ace-win-1
phys-box-b   ace-win-2
ace-linux-1  ace-linux-1
collector-x  collector-x
"""


def snapshot() -> dict:
    return {
        "generated_at": "2026-09-25T11:13:23.209983+00:00",
        "generated_by": "collector-x fleet-daily-collector",
        "date": "2026-09-25",
        "origin_main": "5328e112e",
        "fleet_size": 4,
        "reporting": 3,
        "report": {"latest_snapshot": "2026-09-25", "stale_days": 0},
        "machines": [
            {"name": "collector-x", "reachable": True, "branch": "main",
             "head": "abc1234", "behind": 0, "ahead": 0, "dirty": 0},
            {"name": "ace-linux-1", "reachable": True, "branch": "main",
             "head": "abc1234", "behind": 1, "ahead": 0, "dirty": 3976},
            {"name": "phys-box-a", "reachable": True, "branch": "main",
             "head": "abc1234", "behind": 0, "ahead": 0, "dirty": 9},
            {"name": "PHYS-BOX-B", "reachable": False, "note": "ssh_unreachable"},
        ],
    }


@pytest.fixture()
def env(tmp_path: Path):
    m = tmp_path / "fleet-label-map.txt"
    m.write_text(MAP_TEXT, encoding="utf-8")
    snap = tmp_path / "2026-09-25.json"
    snap.write_text(json.dumps(snapshot(), indent=2) + "\n", encoding="utf-8")
    return m, snap


def run(*args: str, extra_env: dict | None = None):
    import os

    e = {k: v for k, v in os.environ.items() if k != fsl.MAP_ENV}
    if extra_env:
        e.update(extra_env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=e,
    )


def test_physical_names_become_labels_case_insensitively(env):
    m, snap = env
    r = run("--map", str(m), str(snap))
    assert r.returncode == 0, r.stderr
    out = json.loads(snap.read_text(encoding="utf-8"))
    assert [x["name"] for x in out["machines"]] == [
        "collector-x", "ace-linux-1", "ace-win-1", "ace-win-2"]
    assert out["generated_by"] == "collector-x fleet-daily-collector"


def test_only_names_change_numbers_and_order_are_preserved(env):
    m, snap = env
    run("--map", str(m), str(snap))
    before, after = snapshot(), json.loads(snap.read_text(encoding="utf-8"))
    for b, a in zip(before["machines"], after["machines"]):
        b.pop("name"), a.pop("name")
        assert list(a) == list(b) and a == b
    for k in ("generated_at", "date", "origin_main", "fleet_size",
              "reporting", "report"):
        assert after[k] == before[k]
    assert list(after) == list(before)


def test_physical_collector_name_in_generated_by_is_mapped(env):
    m, snap = env
    data = snapshot()
    data["generated_by"] = "PHYS-BOX-A fleet-daily-collector"
    snap.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    assert run("--map", str(m), str(snap)).returncode == 0
    out = json.loads(snap.read_text(encoding="utf-8"))
    assert out["generated_by"] == "ace-win-1 fleet-daily-collector"


def test_already_labelled_file_is_byte_identical(env):
    m, snap = env
    run("--map", str(m), str(snap))
    first = snap.read_bytes()
    assert run("--map", str(m), str(snap)).returncode == 0
    assert snap.read_bytes() == first


def test_unknown_name_fails_closed_without_writing_or_printing_it(env):
    m, snap = env
    data = snapshot()
    data["machines"].append({"name": "stranger-box", "reachable": False})
    snap.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    before = snap.read_bytes()
    r = run("--map", str(m), str(snap))
    assert r.returncode != 0
    assert snap.read_bytes() == before
    assert "stranger-box" not in r.stdout + r.stderr


def test_missing_map_fails_closed(env, tmp_path):
    _, snap = env
    before = snap.read_bytes()
    r = run("--map", str(tmp_path / "absent.txt"), str(snap))
    assert r.returncode != 0
    assert snap.read_bytes() == before


def test_map_from_environment(env):
    m, snap = env
    r = run(str(snap), extra_env={fsl.MAP_ENV: str(m)})
    assert r.returncode == 0, r.stderr


def test_no_map_anywhere_fails_closed(env, tmp_path, monkeypatch):
    _, snap = env
    r = run(str(snap), extra_env={"HOME": str(tmp_path),
                                  "USERPROFILE": str(tmp_path)})
    assert r.returncode != 0


@pytest.mark.parametrize("bad", [
    "only-one-field\n",
    "a b c\n",
    "dup-x ace-win-1\nDUP-X ace-win-2\n",
])
def test_malformed_map_fails_closed(env, bad):
    m, snap = env
    m.write_text(bad, encoding="utf-8")
    before = snap.read_bytes()
    assert run("--map", str(m), str(snap)).returncode != 0
    assert snap.read_bytes() == before


def test_physical_name_left_anywhere_else_fails_closed(env):
    m, snap = env
    data = snapshot()
    data["machines"][1]["note"] = "reached via phys-box-b"
    snap.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    before = snap.read_bytes()
    r = run("--map", str(m), str(snap))
    assert r.returncode != 0
    assert snap.read_bytes() == before
    assert "phys-box-b" not in (r.stdout + r.stderr).lower()


def test_check_mode_reports_without_writing(env):
    m, snap = env
    before = snap.read_bytes()
    r = run("--map", str(m), "--check", str(snap))
    assert r.returncode == 1
    assert snap.read_bytes() == before
