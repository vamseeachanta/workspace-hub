"""Synthetic inventory counts; expected values are independent hand counts."""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CAD_DIR = ROOT / "scripts/data/drive-index/cad"
SCRIPT = CAD_DIR / "report_cad_readiness.py"
HEADER = [
    "path", "format", "ecosystem", "readability", "read_tool", "glb",
    "name_description", "project", "size", "mtime",
]


@pytest.fixture()
def report(monkeypatch):
    monkeypatch.syspath_prepend(str(CAD_DIR))
    spec = importlib.util.spec_from_file_location("cad_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inventory(rows, header=HEADER):
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter="\t")
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def row(path="private-part.step", fmt="step", size="10", glb=""):
    return [path, fmt, "private", "claimed-readable", "private-tool", glb,
            "private-description", "private-project", size, "unknown"]


def test_hand_count_and_no_qualification(report):
    """Two STEP rows: 10+20=30 bytes, one link; one STL: 5 bytes.

    Total = 3 rows, 35 bytes, one reference. No conversion is executed,
    so neither a link nor a supplied readability label establishes readiness.
    """
    result = report.summarize(io.StringIO(inventory([
        row(size="10", glb="private-output.glb"),
        row("second.step", size="20"), row("mesh.stl", "stl", "5"),
    ])))
    assert result["inventory"] == {"files": 3, "bytes": 35, "glb_references": 1}
    assert result["formats"][0] == {
        "format": "step", "files": 2, "bytes": 30, "glb_references": 1,
        "suggested_tool": "pythonocc/OCC",
    }
    assert result["formats"][1]["format"] == "stl"
    assert all(value == "NOT_EVALUATED" for value in result["qualification"].values())
    assert "private" not in json.dumps(result)
    assert "claimed-readable" not in json.dumps(result)


def test_empty_inventory_is_zero_not_qualified(report):
    result = report.summarize(io.StringIO(inventory([])))
    assert result["inventory"] == {"files": 0, "bytes": 0, "glb_references": 0}
    assert result["formats"] == []
    assert result["qualification"]["readability"] == "NOT_EVALUATED"


@pytest.mark.parametrize("size", ["-1", "1.5", "nan", "inf", "", " 2", "1e3", "١"])
def test_reject_invalid_size(report, size):
    with pytest.raises(ValueError, match="size"):
        report.summarize(io.StringIO(inventory([row(size=size)])))


@pytest.mark.parametrize("rows", [
    [row(), row()], [row(path="")], [row(fmt="unknown-private-format")],
    [row()[:-1]], [row() + ["extra"]],
])
def test_reject_ambiguous_records_without_disclosing_cells(report, rows):
    with pytest.raises(ValueError) as error:
        report.summarize(io.StringIO(inventory(rows)))
    assert "private" not in str(error.value)


@pytest.mark.parametrize("header", [[], HEADER[:-1], list(reversed(HEADER))])
def test_reject_wrong_schema(report, header):
    with pytest.raises(ValueError, match="header"):
        report.summarize(io.StringIO(inventory([], header)))


def test_zero_size_and_quoted_fields(report):
    result = report.summarize(io.StringIO(inventory([
        row(path="private\tname.step", size="0"),
    ])))
    assert result["inventory"]["bytes"] == 0
    assert result["inventory"]["files"] == 1


def test_cli_digest_and_input_preservation(tmp_path):
    import hashlib

    source = tmp_path / "inventory.tsv"
    payload = inventory([row()]).encode()
    source.write_bytes(payload)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory", str(source)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["source_sha256"] == hashlib.sha256(payload).hexdigest()
    assert source.read_bytes() == payload
    assert str(tmp_path) not in result.stdout


def test_cli_invalid_input_emits_no_partial_report(tmp_path):
    source = tmp_path / "inventory.tsv"
    source.write_text(inventory([row(), row(fmt="invalid")]))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory", str(source)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "private" not in result.stderr


def test_cli_missing_input_does_not_disclose_path(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory", str(tmp_path / "private.tsv")],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "private" not in result.stderr


def test_cli_builder_pipeline(tmp_path):
    """One selected STEP plus one text file produces one catalog row of 4 bytes."""
    root = tmp_path / "synthetic"
    root.mkdir()
    (root / "block.step").write_text("demo")
    (root / "readme.txt").write_text("excluded")
    raw, built = tmp_path / "raw.tsv", tmp_path / "index.tsv"
    for script, args in [
        ("scan_cad_raw.py", ["--root", str(root), "--out", str(raw)]),
        ("build_cad_index.py", ["--raw", str(raw), "--dedup",
                                str(tmp_path / "no-dedup"), "--out", str(built)]),
        (SCRIPT.name, ["--inventory", str(built)]),
    ]:
        result = subprocess.run([sys.executable, str(CAD_DIR / script), *args],
                                capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["inventory"] == {
        "files": 1, "bytes": 4, "glb_references": 0,
    }


def test_shipped_example():
    """Hand count: STEP 10+20=30, STL 5; total 3 files, 35 bytes, 1 link."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory",
         str(ROOT / "examples/cad/readiness-inventory.tsv")],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["inventory"] == {"files": 3, "bytes": 35, "glb_references": 1}
    assert [(group["format"], group["files"], group["bytes"])
            for group in output["formats"]] == [("step", 2, 30), ("stl", 1, 5)]
