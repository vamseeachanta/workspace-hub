"""Independent literal counts for the checkpoint teaching example.

Case budgets, exit values and hand counts cite the worked cases and CLI contract
in docs/guides/autonomous-loop-patterns.md, rather than the implementation.
"""

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest


# Layout citation: this file is tests/workflow/test_checkpoint_loop_example.py.
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "examples/workflow/checkpoint_loop.py"
GUIDE = ROOT / "docs/guides/autonomous-loop-patterns.md"


def invoke(tmp_path, outcomes, budget):
    source = tmp_path / "literal outcomes.json"
    source.write_text(json.dumps(outcomes), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--budget", str(budget)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    # Reading the input and writing stdout must leave the scratch input intact.
    assert json.loads(source.read_text(encoding="utf-8")) == outcomes
    assert sorted(path.name for path in tmp_path.iterdir()) == [source.name]
    return result


def test_checkpoint_success(tmp_path):
    # Hand count: the first outcome succeeds; the second is never attempted.
    result = invoke(tmp_path, ["success", "retry"], 3)
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        '{"attempts":1,"budget":3,"history":["success"],"status":"success"}\n'
    )


def test_checkpoint_retry(tmp_path):
    # Hand count: one retry plus one success consumes two outcomes, not three.
    result = invoke(tmp_path, ["retry", "success", "retry"], 3)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "attempts": 2, "budget": 3, "history": ["retry", "success"], "status": "success"
    }


def test_checkpoint_budget_exhausted(tmp_path):
    # Hand count: two retries fill the budget; the third outcome is unvisited.
    result = invoke(tmp_path, ["retry", "retry", "success"], 2)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "attempts": 2, "budget": 2, "history": ["retry", "retry"],
        "status": "budget_exhausted",
    }


@pytest.mark.parametrize("budget", [0, -1, "invalid", "1.5"])
def test_invalid_budget(tmp_path, budget):
    # Nonpositive and noninteger budgets cannot permit an attempt (guide contract).
    result = invoke(tmp_path, ["success"], budget)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "budget must be a positive integer" in result.stderr


def test_input_exhausted(tmp_path):
    # Hand count: one supplied retry cannot create the second permitted attempt.
    result = invoke(tmp_path, ["retry"], 2)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "attempts": 1, "budget": 2, "history": ["retry"], "status": "input_exhausted"
    }


def test_success_on_last_permitted_attempt(tmp_path):
    # Hand count: retry, retry, success uses all three allowed attempts.
    result = invoke(tmp_path, ["retry", "retry", "success"], 3)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "attempts": 3, "budget": 3, "history": ["retry", "retry", "success"],
        "status": "success",
    }


def test_budget_and_input_end_together(tmp_path):
    # Hand count: one retry uses the one permitted attempt; budget takes precedence.
    result = invoke(tmp_path, ["retry"], 1)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "attempts": 1, "budget": 1, "history": ["retry"], "status": "budget_exhausted"
    }


@pytest.mark.parametrize("outcomes", [[], {}, "success", [True], ["unknown"],
                                       ["success", "unknown"]])
def test_invalid_outcomes(tmp_path, outcomes):
    result = invoke(tmp_path, outcomes, 1)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "input must be a nonempty JSON array of retry or success" in result.stderr


@pytest.mark.parametrize("contents", ["[", "not JSON"])
def test_invalid_json(tmp_path, contents):
    source = tmp_path / "input.json"
    source.write_text(contents, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--budget", "1"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "input must be readable UTF-8 JSON" in result.stderr
    assert str(source) not in result.stderr


@pytest.mark.parametrize("input_kind", ["missing", "directory", "invalid_utf8"])
def test_unreadable_input(tmp_path, input_kind):
    source = tmp_path / "input.json"
    if input_kind == "directory":
        source.mkdir()
    elif input_kind == "invalid_utf8":
        source.write_bytes(b"\xff")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--budget", "1"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "input must be readable UTF-8 JSON" in result.stderr
    assert str(source) not in result.stderr


def test_documented_checkpoint_command(tmp_path):
    commands = re.findall(r"```sh\n(python examples/workflow/checkpoint_loop\.py [^\n]+)\n```",
                          GUIDE.read_text(encoding="utf-8"))
    # Literal cases from the guide; counts are the hand enumerations above.
    cases = [
        (["success", "retry"], 3, 0, 1, "success"),
        (["retry", "success", "retry"], 3, 0, 2, "success"),
        (["retry", "retry", "success"], 2, 1, 2, "budget_exhausted"),
        (["success"], 0, 2, None, None),
    ]
    assert len(commands) == len(cases)
    source = tmp_path / "documented input.json"
    environment = dict(os.environ, CHECKPOINT_INPUT=str(source))
    for command, (outcomes, budget, exit_code, attempts, status) in zip(commands, cases):
        source.write_text(json.dumps(outcomes), encoding="utf-8")
        # Execute the documented tokens directly, preserving paths with spaces.
        args = shlex.split(command)
        assert args.pop(0) == "python"
        args = [environment["CHECKPOINT_INPUT"] if arg == "$CHECKPOINT_INPUT" else arg
                for arg in args]
        assert args == ["examples/workflow/checkpoint_loop.py", "--input", str(source),
                        "--budget", str(budget)]
        result = subprocess.run(
            [sys.executable, *args], cwd=ROOT, env=environment,
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == exit_code
        if attempts is None:
            assert result.stdout == ""
            assert "budget must be a positive integer" in result.stderr
        else:
            assert json.loads(result.stdout)["attempts"] == attempts
            assert json.loads(result.stdout)["budget"] == budget
            assert json.loads(result.stdout)["status"] == status
