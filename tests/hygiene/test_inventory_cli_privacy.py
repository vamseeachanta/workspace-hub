"""CLI privacy contract and hand-counted inventory README example."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts/hygiene/inventory.py"
SENTINEL = "REJECTED_ARGUMENT_SENTINEL"
INVALID_CASES = ("unknown", "integer", "missing")


@pytest.fixture
def cli_input(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    (root / "stray.txt").write_bytes(b"abc")
    config = tmp_path / f"{SENTINEL}.json"
    # README Worked example: one stray file containing three ASCII bytes.
    config.write_text(
        json.dumps({"root": str(root), "max_files": 1}), encoding="utf-8"
    )
    return config, tmp_path / "manifest.json"


def invalid_arguments(kind, config, output):
    required = ["--config", str(config), "--out", str(output)]
    if kind == "unknown":
        return [*required, f"--{SENTINEL}"]
    if kind == "integer":
        return [*required, "--fail-above", SENTINEL]
    assert kind == "missing"
    return ["--config", str(config)]


def run_cli(arguments, cwd):
    # Exercise the standalone bootstrap, without pytest's import path or Git bindings.
    env = {
        key: value
        for key, value in os.environ.items()
        if key != "PYTHONPATH" and not key.startswith("GIT_")
    }
    assert not cwd.is_relative_to(REPO_ROOT)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def assert_private_error(stdout, stderr, caller_program):
    assert stdout == ""
    assert stderr.startswith("usage: inventory.py ")
    assert "--config CONFIG --out OUT" in stderr
    assert stderr.endswith("inventory.py: error: invalid arguments\n")
    for stream in (stdout, stderr):
        assert SENTINEL not in stream
        assert str(caller_program) not in stream
        assert "Traceback" not in stream


@pytest.mark.parametrize("kind", INVALID_CASES)
def test_inventory_cli_parse_errors_do_not_reflect_input(kind, cli_input, tmp_path):
    config, output = cli_input
    result = run_cli(invalid_arguments(kind, config, output), tmp_path)
    # scripts/lib/safe_cli.py contract: argparse parse errors exit with status 2.
    assert result.returncode == 2
    assert_private_error(result.stdout, result.stderr, SCRIPT)
    assert not output.exists()


@pytest.mark.parametrize("kind", INVALID_CASES)
def test_invalid_arguments_never_start_inventory(
    kind, cli_input, tmp_path, monkeypatch, capsys
):
    spec = importlib.util.spec_from_file_location("inventory_cli_privacy", SCRIPT)
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)
    construct = Mock(side_effect=AssertionError("inventory started"))
    write = Mock(side_effect=AssertionError("output written"))
    monkeypatch.setattr(inventory, "build_manifest", construct)
    monkeypatch.setattr(Path, "write_text", write)
    caller_program = tmp_path / SENTINEL / "caller.py"
    monkeypatch.setattr(sys, "argv", [str(caller_program)])
    config, output = cli_input

    with pytest.raises(SystemExit) as caught:
        inventory.main(invalid_arguments(kind, config, output))

    construct.assert_not_called()
    write.assert_not_called()
    # Independent shared parser contract, also checked in test_input_boundaries.py.
    assert caught.value.code == 2
    captured = capsys.readouterr()
    assert_private_error(captured.out, captured.err, caller_program)


def test_inventory_cli_help_and_valid_input_preserved(cli_input, tmp_path):
    config, output = cli_input
    help_result = run_cli(["--help"], tmp_path)
    # README Exit codes: successful help/inventory returns zero.
    assert help_result.returncode == 0
    assert help_result.stderr == ""
    assert help_result.stdout.startswith("usage: inventory.py ")
    assert "Inventory metadata outside configured repositories and cache directories." in (
        help_result.stdout
    )
    for option in (
        "-h, --help", "--config CONFIG", "--out OUT", "--fail-above FAIL_ABOVE"
    ):
        assert option in help_result.stdout
    assert "show this help message and exit" in help_result.stdout
    assert str(SCRIPT) not in help_result.stdout
    assert not output.exists()

    # One-file bound and threshold come from the hand-counted README example.
    result = run_cli(
        ["--config", str(config), "--out", str(output), "--fail-above", "1"],
        tmp_path,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    # One abc file is three bytes; this fixture contains no repositories.
    assert result.stdout == "stray_files=1 bytes=3 repositories=0\n"
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["totals"]["count"] == 1
    assert manifest["totals"]["bytes"] == 3
    assert manifest["repos"] == []
    assert [row["path"] for row in manifest["files"]] == ["stray.txt"]
