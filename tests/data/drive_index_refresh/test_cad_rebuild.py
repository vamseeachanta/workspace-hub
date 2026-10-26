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
def test_shell_entry_passes_cad_builder_arguments(tmp_path, override_root):
    import json
    import os
    import shutil
    import yaml

    root = tmp_path / "drive"
    root.mkdir()
    (root / "widget.step").write_text("synthetic")
    index_dir = root / "_cad-index"
    dedup = index_dir / "dedup"
    dedup.mkdir(parents=True)
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
    if override_root:
        env["DRIVE_INDEX_CAD_ROOT"] = str(root)
    # Relocate all configured storage before executing even an older wrapper.
    synthetic_repo = tmp_path / "repository"
    script_dir = synthetic_repo / "scripts/data/drive-index"
    script_dir.mkdir(parents=True)
    shutil.copytree(BUILD.parent, script_dir / "cad")
    wrapper = script_dir / "refresh-drive-index.sh"
    source = REPO_ROOT / "scripts/data/drive-index"
    config = yaml.safe_load((source / "drive-index-config.yaml").read_text())
    prefix = config["drives"]["ace"]["canonical_prefix"]
    wrapper.write_text((source / wrapper.name).read_text().replace(prefix, str(root)))
    config["drives"]["ace"]["canonical_prefix"] = str(root)
    (script_dir / "drive-index-config.yaml").write_text(yaml.safe_dump(config))
    result = subprocess.run(["bash", str(wrapper), "cad"], env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in args_log.read_text().splitlines()]
    build_call = next(call for call in calls if call[0] == str(script_dir / "cad" / BUILD.name))
    assert build_call[1:] == [
        "--raw", str(index_dir / "cad-raw.tsv"),
        "--dedup", str(dedup),
        "--out", str(index_dir / "cad-readability-index.tsv"),
    ]
    assert "widget.glb" in (index_dir / "cad-readability-index.tsv").read_text()
    assert json.loads((index_dir / "refresh-state.json").read_text())["status"] == "ok"
