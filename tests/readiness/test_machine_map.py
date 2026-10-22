"""Synthetic contracts for the private map boundary in issue #3498.

Counts and times are hand calculations, not measurements: at midnight on the
next day a midnight observation is one day old; equal age/limit is fresh.
Schema tags and field sets come from docs/readiness/machine-map.md.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/readiness/machine_map.py"
spec = importlib.util.spec_from_file_location("machine_map", SCRIPT)
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)


def record(source="self-report"):
    return {
        "schema_version": 1, "machine": "compute", "role": "executor",
        "source": source, "updated_at": "2026-10-01T00:00:00+00:00",
        "data_sources": [{"name": "archive", "reachable": True}],
        "services": [{"name": "worker", "kind": "unit", "state": "active"}],
        "auth_surfaces": {"gh": True, "codex": False},
    }


def private_root(tmp_path):
    root = tmp_path / "private"
    (root / "machine-ecosystem").mkdir(parents=True)
    (root / "machine-ecosystem/private.json").write_text('{"visibility":"private"}')
    return root


def test_write_projection_and_idempotency(tmp_path):
    root = private_root(tmp_path)
    assert mm.write_map(root, record()) is True
    path = root / "machine-ecosystem/machines/compute.yaml"
    before = path.read_bytes()
    stamp = path.stat().st_mtime_ns
    newer = record()
    newer["updated_at"] = "2026-10-02T00:00:00+00:00"
    assert mm.write_map(root, newer) is False
    assert path.read_bytes() == before and path.stat().st_mtime_ns == stamp
    pointer = mm.project(root, "compute")
    assert pointer == {
        "present": True, "updated_at": record()["updated_at"],
        "content_hash": hashlib.sha256(before).hexdigest(),
    }
    newer["data_sources"][0]["reachable"] = False
    assert mm.write_map(root, newer) is True
    assert mm.project(root, "compute")["content_hash"] != pointer["content_hash"]


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(machine="../escape"),
    lambda r: r.update(role="invalid"),
    lambda r: r.update(source="observed-somewhere"),
    lambda r: r.update(updated_at="not-a-date"),
    lambda r: r.update(updated_at="2026-10-01T00:00:00"),
    lambda r: r.update(extra="private detail"),
    lambda r: r.update(schema_version=True),
    lambda r: r["data_sources"][0].update(reachable="yes"),
    lambda r: r["data_sources"].append(r["data_sources"][0]),
    lambda r: r["services"][0].update(command="private detail"),
    lambda r: r["auth_surfaces"].update(gh="private detail"),
])
def test_schema_rejects_ambiguous_records(mutate):
    r = record()
    mutate(r)
    with pytest.raises(ValueError):
        mm.validate_map(r)


def test_private_destination_and_symlink_escape(tmp_path):
    with pytest.raises(ValueError):
        mm.write_map(ROOT, record())
    root = private_root(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "machine-ecosystem/machines").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        mm.write_map(root, record())
    assert not list(outside.iterdir())


def test_projection_fails_closed_without_leaking(tmp_path):
    root = private_root(tmp_path)
    assert mm.project(None, "compute") == mm.ABSENT
    assert mm.project(root, "compute") == mm.ABSENT
    maps = root / "machine-ecosystem/machines"
    maps.mkdir()
    (maps / "compute.yaml").write_text('{"updated_at":"private-detail"}')
    assert mm.project(root, "compute") == mm.ABSENT
    with pytest.raises(ValueError):
        mm.project(root, "../escape")


def test_collection_uses_names_and_presence_only(tmp_path, monkeypatch):
    path = tmp_path / "data"
    path.mkdir()
    config = {
        "role": "executor", "probe_timeout_seconds": 1,
        "data_sources": [{"name": "archive", "path": str(path)},
                         {"name": "missing", "path": str(path / "missing")}],
        "services": [{"name": "worker", "kind": "unit", "target": "worker.service"},
                     {"name": "agent", "kind": "agent", "path": str(path)},
                     {"name": "refresh", "kind": "cron", "target": "refresh"}],
        "auth_surfaces": ["gh", "codex"],
    }
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[0] == "systemctl":
            return subprocess.CompletedProcess(args, 0, "active\n", "")
        return subprocess.CompletedProcess(args, 0, "* * * * * private-command # machine-map:refresh\n", "")

    monkeypatch.setattr(mm.subprocess, "run", run)
    monkeypatch.setattr(mm.shutil, "which", lambda name: "/bin/tool" if name == "gh" else None)
    r = mm.collect("compute", config, record()["updated_at"])
    assert r["data_sources"] == [{"name": "archive", "reachable": True},
                                 {"name": "missing", "reachable": False}]
    assert {s["name"]: s["state"] for s in r["services"]} == {
        "worker": "active", "agent": "present", "refresh": "present"}
    assert r["auth_surfaces"] == {"gh": True, "codex": False}
    assert not any("private-command" in str(v) or str(path) in str(v) for v in r.values())
    assert all(args[0] in {"systemctl", "crontab"} for args in calls)


def test_probe_errors_are_not_absence(tmp_path, monkeypatch):
    def unavailable(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(mm.subprocess, "run", unavailable)
    config = {"role": "executor", "probe_timeout_seconds": 1, "data_sources": [],
              "services": [{"name": "worker", "kind": "unit", "target": "worker.service"}],
              "auth_surfaces": []}
    assert mm.collect("compute", config, record()["updated_at"])["services"][0]["state"] == "not_evaluated"


def test_seed_and_private_matrix_coverage(tmp_path):
    root = private_root(tmp_path)
    mm.write_map(root, record("seeded-manual"))
    html = mm.build_matrix(root, ["compute", "portable"])
    assert "seeded-manual" in html and "self-report" not in html
    assert "portable" in html and "MISSING-EVIDENCE" in html
    assert "archive" in html and "worker" in html and "executor" in html
    assert "true" in html and "active" in html
    assert mm.build_matrix(root, ["compute", "portable"]) == html


def test_cli_wrapper_and_seed_do_not_print_private_content(tmp_path):
    root = private_root(tmp_path)
    seed = root / "machine-ecosystem/seed.json"
    seed.write_text(json.dumps(record("seeded-manual")))
    wrapper = ROOT / "scripts/readiness/collect-machine-map.sh"
    env = {**os.environ, "MACHINE_MAP_ADMIN_ROOT": str(root), "MACHINE_MAP_PYTHON": sys.executable}
    res = subprocess.run(["bash", str(wrapper), "seed", "--input", str(seed)],
                         env=env, capture_output=True, text=True, check=True)
    assert res.stdout.strip() == "changed"
    assert res.stderr == ""
    res = subprocess.run([sys.executable, str(SCRIPT), "project", "--machine", "compute"],
                         env=env, capture_output=True, text=True, check=True)
    assert set(json.loads(res.stdout)) == {"present", "updated_at", "content_hash"}
    assert "archive" not in res.stdout and str(root) not in res.stdout


@pytest.mark.parametrize("body", ["[]", '{"source":"seeded-manual"}', '{"role":[]}'])
def test_cli_invalid_private_input_has_sanitized_error(tmp_path, body):
    root = private_root(tmp_path)
    source = root / "machine-ecosystem/input.json"
    source.write_text(body)
    result = subprocess.run([sys.executable, str(SCRIPT), "seed", "--input", str(source)],
                            env={**os.environ, "MACHINE_MAP_ADMIN_ROOT": str(root)},
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "machine-map: invalid or unavailable private inventory input\n"


def test_worked_example(tmp_path):
    spec = importlib.util.spec_from_file_location("map_example", ROOT / "examples/readiness/machine_map_example.py")
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    output = tmp_path / "example"
    pointer = example.run(output)
    assert pointer["present"] is True
    assert example.run(output) == pointer
    html = (output / "machine-ecosystem/matrix.html").read_text()
    assert "seeded-manual" in html and "MISSING-EVIDENCE" in html


def test_collection_normalizes_row_order(tmp_path):
    root = private_root(tmp_path)
    r = record()
    r["data_sources"].append({"name": "backup", "reachable": False})
    assert mm.write_map(root, r)
    r["data_sources"].reverse()
    r["updated_at"] = "2026-10-02T00:00:00+00:00"
    assert not mm.write_map(root, r)


def test_projection_refuses_wrong_identity_and_duplicate_fields(tmp_path):
    root = private_root(tmp_path)
    mm.write_map(root, record())
    path = root / "machine-ecosystem/machines/compute.yaml"
    r = record()
    r["machine"] = "portable"
    path.write_text(json.dumps(r))
    assert mm.project(root, "compute") == mm.ABSENT
    path.write_text('{"machine":"compute","machine":"portable"}')
    assert mm.project(root, "compute") == mm.ABSENT


@pytest.mark.parametrize("services", [["invalid"], [None], "invalid"])
def test_cli_invalid_probe_rows_have_sanitized_error(tmp_path, services):
    root = private_root(tmp_path)
    config = {"role": "executor", "probe_timeout_seconds": 1, "data_sources": [],
              "services": services, "auth_surfaces": []}
    source = root / "machine-ecosystem/probes.json"
    source.write_text(json.dumps(config))
    result = subprocess.run([sys.executable, str(SCRIPT), "collect", "--machine", "compute", "--input", str(source)],
                            env={**os.environ, "MACHINE_MAP_ADMIN_ROOT": str(root)},
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "machine-map: invalid or unavailable private inventory input\n"
