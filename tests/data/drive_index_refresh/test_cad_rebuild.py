from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCAN = REPO_ROOT / "scripts/data/drive-index/cad/scan_cad_raw.py"
BUILD = REPO_ROOT / "scripts/data/drive-index/cad/build_cad_index.py"
HEADER = "path\tformat\tecosystem\treadability\tread_tool\tglb\tname_description\tproject\tsize\tmtime"


def test_cad_scan_raw_format(tmp_path):
    root = tmp_path / "ace"
    for rel in ["a/model.step", "a/drawing.dwg", "a/part.sldprt", "a/readme.txt"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")
    raw = tmp_path / "cad-raw.tsv"

    result = subprocess.run([sys.executable, str(SCAN), "--root", str(root), "--out", str(raw)], text=True, capture_output=True)

    assert result.returncode == 0
    lines = raw.read_text().splitlines()
    assert len(lines) == 3
    assert all(len(line.split("\t")) == 3 for line in lines)
    assert not any("readme.txt" in line for line in lines)


def test_cad_builder_output_header_stable(tmp_path):
    raw = tmp_path / "cad-raw.tsv"
    raw.write_text("10\t2026-07-02T00:00:00Z\t/mnt/ace/docs/disciplines/proj/widget.step\n")  # abs-path-allowed
    out = tmp_path / "cad-readability-index.tsv"

    result = subprocess.run(
        [sys.executable, str(BUILD), "--raw", str(raw), "--dedup", str(tmp_path / "dedup"), "--out", str(out)],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert out.read_text().splitlines()[0] == HEADER
    assert not out.with_suffix(out.suffix + ".tmp").exists()


@pytest.mark.parametrize("override_root", [True, False])
@pytest.mark.parametrize("fail_step", [None, "scan_cad_raw.py", "build_cad_index.py", "config"])
def test_shell_entry_cad_arguments_and_state(tmp_path, override_root, fail_step):
    import json
    import os
    import shutil
    import yaml

    root = tmp_path / "drive"
    root.mkdir()
    (root / "widget.step").write_text("synthetic")
    index_dir = root / "_cad-index"
    state_file = index_dir / "refresh-state.json"
    dedup = index_dir / "dedup"
    dedup.mkdir(parents=True)
    state_file.write_text(json.dumps({"status": "ok", "error": "stale"}))
    (dedup / "glb-library-manifest.tsv").write_text(
        f"source\tglb\n{root / 'widget.step'}\twidget.glb\n"
    )
    user_dir = tmp_path / "user"
    bin_dir = user_dir / ".local" / "bin"
    bin_dir.mkdir(parents=True)
    args_log = tmp_path / "args.jsonl"
    shim = bin_dir / "python3"
    shim.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['CAD_ARGS_LOG'], 'a') as log:\n"
        "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1] == '-c' and os.environ.get('CAD_FAIL_STEP') == 'config':\n"
        "    sys.stderr.write('synthetic configuration failure\\n')\n"
        "    sys.exit(9)\n"
        "if sys.argv[1].endswith('/' + os.environ.get('CAD_FAIL_STEP', 'no-failure')):\n"
        "    sys.stderr.write('synthetic command failure\\n')\n"
        "    sys.exit(9)\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, *sys.argv[1:]])\n"
    )
    shim.chmod(0o755)
    # Resolve no packages: the test interpreter already supplies YAML support.
    uv_shim = bin_dir / "uv"
    uv_shim.write_text('#!/usr/bin/env bash\nshift 3\nexec "$@"\n')
    uv_shim.chmod(0o755)
    env = os.environ.copy()
    env.pop("DRIVE_INDEX_TEST_MODE", None)
    env.update(
        HOME=str(user_dir), TMPDIR=str(tmp_path),
        CAD_ARGS_LOG=str(args_log),
        DRIVE_INDEX_NOTIFY_LOG=str(tmp_path / "notify.log"),
    )
    env.pop("DRIVE_INDEX_CAD_ROOT", None)
    env.pop("CAD_FAIL_STEP", None)
    if fail_step:
        env["CAD_FAIL_STEP"] = fail_step
    if override_root:
        env["DRIVE_INDEX_CAD_ROOT"] = str(root)
    # Isolate the obsolete failure destination, distinct from either selected root.
    synthetic_repo = tmp_path / "repository"
    script_dir = synthetic_repo / "scripts/data/drive-index"
    script_dir.mkdir(parents=True)
    shutil.copytree(BUILD.parent, script_dir / "cad")
    wrapper = script_dir / "refresh-drive-index.sh"
    source = REPO_ROOT / "scripts/data/drive-index"
    config = yaml.safe_load((source / "drive-index-config.yaml").read_text())
    prefix = config["drives"]["ace"]["canonical_prefix"]
    default_root = tmp_path / "default-drive"
    configured_root = tmp_path / "configured-drive" if override_root else root
    unselected_states = []
    for unselected_root in {default_root, configured_root} - {root}:
        unselected_state = unselected_root / "_cad-index" / "refresh-state.json"
        unselected_state.parent.mkdir(parents=True)
        unselected_state.write_text(json.dumps({"status": "ok", "error": "unchanged"}))
        unselected_states.append(unselected_state)
    wrapper.write_text((source / wrapper.name).read_text().replace(prefix, str(default_root)))
    config["drives"]["ace"]["canonical_prefix"] = str(configured_root)
    (script_dir / "drive-index-config.yaml").write_text(yaml.safe_dump(config))
    result = subprocess.run(
        ["bash", str(wrapper), "cad"], cwd=synthetic_repo, env=env, text=True, capture_output=True,
    )
    for unselected_state in unselected_states:
        assert json.loads(unselected_state.read_text()) == {"status": "ok", "error": "unchanged"}
    if fail_step == "config" and not override_root:
        assert result.returncode != 0
        assert "synthetic configuration failure" in result.stderr
        assert "\tfail\t" in (tmp_path / "notify.log").read_text()
        assert json.loads(state_file.read_text()) == {"status": "ok", "error": "stale"}
        assert not (synthetic_repo / ".tmp").exists()
        return
    if fail_step and fail_step != "config":
        assert result.returncode != 0
        assert "synthetic command failure" in result.stderr
        payload = json.loads(state_file.read_text())
        assert payload["status"] == "failed"
        assert fail_step in payload["error"]
        assert "\tfail\t" in (tmp_path / "notify.log").read_text()
        return
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in args_log.read_text().splitlines()]
    build_call = next(call for call in calls if call[0] == str(script_dir / "cad" / BUILD.name))
    assert build_call[1:] == [
        "--raw", str(index_dir / "cad-raw.tsv"),
        "--dedup", str(dedup),
        "--out", str(index_dir / "cad-readability-index.tsv"),
    ]
    assert "widget.glb" in (index_dir / "cad-readability-index.tsv").read_text()
    assert json.loads(state_file.read_text())["status"] == "ok"
