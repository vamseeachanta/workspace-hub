from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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
