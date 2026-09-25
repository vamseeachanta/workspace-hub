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
collector-x  fleet-collector
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
        "fleet-collector", "ace-linux-1", "ace-win-1", "ace-win-2"]
    assert out["generated_by"] == "fleet-collector fleet-daily-collector"


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


# --- Codex r1 (C18): every host value must end as an approved public label ---

def _write(snap: Path, data: dict) -> bytes:
    snap.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return snap.read_bytes()


@pytest.mark.parametrize("label", [
    "ace-win-1", "ace-win-2", "ace-linux-1", "ace-linux-2", "gpu-claw",
    "fleet-collector", "mac-1", "spark-1",
])
def test_approved_labels_are_public_labels(label):
    assert fsl.is_public_label(label)


@pytest.mark.parametrize("label", ["collector-x", "box-7", "mac", "spark-abc", ""])
def test_other_values_are_not_public_labels(label):
    assert not fsl.is_public_label(label)


def test_registry_logical_names_are_public_labels():
    """Every logical name the workstation registry lists must be accepted."""
    import yaml

    reg = yaml.safe_load((ROOT / "config" / "workstations" / "registry.yaml")
                         .read_text(encoding="utf-8"))
    logical = {k for k in reg["machines"] if fsl.LABEL_RE.match(k)}
    logical |= {m["hostname"] for m in reg["machines"].values()
                if isinstance(m.get("hostname"), str) and m["hostname"].startswith("ace-")}
    assert {"ace-win-1", "ace-win-2", "ace-linux-1", "ace-linux-2", "gpu-claw"} <= (
        logical | {"gpu-claw"})
    for name in logical:
        assert fsl.is_public_label(name), "registry logical name rejected"


def test_identity_line_for_non_label_host_fails_closed(env):
    """A map that keeps a physical name as its own 'label' must not publish it."""
    m, snap = env
    m.write_text(MAP_TEXT.replace("collector-x  fleet-collector",
                                  "collector-x  collector-x"), encoding="utf-8")
    before = snap.read_bytes()
    r = run("--map", str(m), str(snap))
    assert r.returncode == 2
    assert snap.read_bytes() == before
    assert "collector-x" not in r.stdout + r.stderr


def test_neutral_labels_for_unregistered_hosts(env):
    m, snap = env
    m.write_text(MAP_TEXT + "laptop-q  mac-1\ndgx-q9  spark-1\n", encoding="utf-8")
    data = snapshot()
    data["machines"] += [{"name": "laptop-q", "reachable": False},
                         {"name": "DGX-Q9", "reachable": False}]
    _write(snap, data)
    assert run("--map", str(m), str(snap)).returncode == 0
    out = json.loads(snap.read_text(encoding="utf-8"))
    assert [x["name"] for x in out["machines"]][-2:] == ["mac-1", "spark-1"]
    assert all(fsl.is_public_label(x["name"]) for x in out["machines"])
    assert fsl.is_public_label(out["generated_by"].split()[0])


def test_hostname_fragment_in_branch_is_rewritten(env):
    m, snap = env
    m.write_text(MAP_TEXT + "zeta-hq-node07  ace-win-3\n", encoding="utf-8")
    data = snapshot()
    data["machines"][0]["branch"] = "port/node07-parked-items"
    data["machines"][1]["branch"] = "feat/zeta-hq-node07-sync"
    _write(snap, data)
    r = run("--map", str(m), str(snap))
    assert r.returncode == 0, r.stderr
    text = snap.read_text(encoding="utf-8")
    out = json.loads(text)
    assert out["machines"][0]["branch"] == "port/ace-win-3-parked-items"
    assert out["machines"][1]["branch"] == "feat/ace-win-3-sync"
    assert "node07" not in text and "zeta" not in text


def test_hostname_fragment_left_elsewhere_fails_closed(env):
    m, snap = env
    m.write_text(MAP_TEXT + "zeta-hq-node07  ace-win-3\n", encoding="utf-8")
    data = snapshot()
    data["machines"][3]["note"] = "ssh to node07 refused"
    before = _write(snap, data)
    r = run("--map", str(m), str(snap))
    assert r.returncode == 2
    assert snap.read_bytes() == before
    assert "node07" not in r.stdout + r.stderr


def test_ambiguous_fragment_fails_closed(env):
    """A fragment shared by two physical names cannot be rewritten safely."""
    m, snap = env
    m.write_text(MAP_TEXT + "zeta-hq-node07  ace-win-3\nzeta-hq-node08  ace-win-4\n",
                 encoding="utf-8")
    data = snapshot()
    data["machines"][0]["branch"] = "port/zeta-parked-items"
    before = _write(snap, data)
    assert run("--map", str(m), str(snap)).returncode == 2
    assert snap.read_bytes() == before


def test_unmapped_host_value_left_after_labelling_fails_closed(env):
    """Belt and braces: the written file is re-read and every host value checked."""
    m, snap = env
    data = snapshot()
    data["generated_by"] = "stranger-box fleet-daily-collector"
    before = _write(snap, data)
    r = run("--map", str(m), str(snap))
    assert r.returncode == 2
    assert snap.read_bytes() == before


@pytest.mark.parametrize("name", ["2026-09-24.json", "2026-09-25.json"])
def test_committed_snapshots_carry_only_public_labels(name):
    """Codex r1: the committed public snapshots name hosts by label only."""
    path = ROOT / "docs" / "reports" / "fleet-snapshots" / name
    data = json.loads(path.read_text(encoding="utf-8"))
    assert fsl.is_public_label(data["generated_by"].split()[0])
    for m in data["machines"]:
        assert fsl.is_public_label(m["name"])
        branch = m.get("branch", "main")
        assert branch == "main" or not fsl.HOSTNAME_SHAPE_RE.search(branch)
    assert fsl.public_host_values_ok(data)

def test_unmapped_hostname_shape_in_branch_fails_closed(env):
    """A Windows-hostname-shaped fragment the map does not know still blocks."""
    m, snap = env
    data = snapshot()
    data["machines"][0]["branch"] = "port/" + "ws" + "77-parked-items"
    before = _write(snap, data)
    r = run("--map", str(m), str(snap))
    assert r.returncode == 2
    assert snap.read_bytes() == before
    assert "77-parked" not in r.stdout + r.stderr