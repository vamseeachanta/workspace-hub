"""Behavior contracts for the cost CLI's advertised table and CSV formats.

Synthetic inputs, not prices: alpha has inputs 10 + 20 = 30, outputs 2 + 3 = 5,
cost 0.2 + 0.3 = 0.5 and two records. Beta has inputs 7, outputs 1, cost 0.1
and one record. Expected values below are these independent hand calculations.
Exit codes follow scripts/ai/wrk_cost_report.py: success 0, empty filter 1.
"""

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

CLI = Path(__file__).resolve().parents[2] / "scripts/ai/wrk_cost_report.py"
FORMATS = ("table", "csv")
EXPECTED = {
    "alpha": ("30", "5", "0.5000", "2", "fixture"),
    "beta": ("7", "1", "0.1000", "1", "fixture"),
}


@pytest.fixture
def cost_file(tmp_path):
    rows = [
        ("alpha", 10, 2, 0.2),
        ("alpha", 20, 3, 0.3),
        ("beta", 7, 1, 0.1),
    ]
    path = tmp_path / "costs.jsonl"
    path.write_text(
        "".join(
            json.dumps(
                {"wrk": key, "input_tokens": inputs, "output_tokens": outputs,
                 "cost_usd": cost, "provider": "fixture"}
            ) + "\n"
            for key, inputs, outputs, cost in rows
        ),
        encoding="utf-8",
    )
    return path


def run_cost(path, output_format, *options):
    return subprocess.run(
        [sys.executable, str(CLI), "--data-file", str(path), *options,
         *(["--csv"] if output_format == "csv" else [])],
        capture_output=True, text=True, check=False,
    )


def cost_rows(stdout, output_format):
    if output_format == "csv":
        rows = list(csv.reader(io.StringIO(stdout)))
        assert rows.pop(0) == ["WRK-ID", "INPUT", "OUTPUT", "COST_USD",
                               "SESSIONS", "PROVIDERS"]
    else:
        rows = [line.replace("$", "").split() for line in stdout.splitlines()
                if line.startswith(("alpha ", "beta "))]
    # A dict alone would silently hide duplicate rendered identities.
    assert len({row[0] for row in rows}) == len(rows)
    return {row[0]: tuple(row[1:]) for row in rows}


@pytest.mark.parametrize("output_format", FORMATS)
@pytest.mark.parametrize("selected", (None, "alpha", "beta"))
def test_filter_changes_rows_in_every_format(cost_file, output_format, selected):
    result = run_cost(cost_file, output_format, *([selected] if selected else []))
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    expected = EXPECTED if selected is None else {selected: EXPECTED[selected]}
    assert cost_rows(result.stdout, output_format) == expected
    if selected:
        assert ("beta" if selected == "alpha" else "alpha") not in result.stdout


@pytest.mark.parametrize("output_format", FORMATS)
def test_empty_filter_is_explicit_in_every_format(cost_file, output_format):
    result = run_cost(cost_file, output_format, "absent")
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip() == "No records for absent"


@pytest.mark.parametrize("output_format", FORMATS)
def test_unadvertised_json_is_rejected(cost_file, output_format):
    """The existing argparse contract rejects unknown options with exit 2."""
    result = run_cost(cost_file, output_format, "--json")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "unrecognized arguments: --json" in result.stderr
