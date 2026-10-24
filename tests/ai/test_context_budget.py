"""Context accounting: issue #3717 (2026), plus independent hand calculations."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ai/context_budget.py"
SPEC = importlib.util.spec_from_file_location("context_budget", SCRIPT)
budget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(budget)


@pytest.fixture
def observation():
    """Literal inputs from issue #3717, 'Measured, not estimated' (2026)."""
    return {
        "source": "Issue #3717, Measured, not estimated (2026)",
        "window_tokens": 1_000_000,
        "harness_tokens": {
            "system_prompt": 5_500,
            "system_tools": 14_000,
            "memory_files": 8_800,
            "skills": 7_500,
            "custom_agents": 314,
        },
        "message_tokens": 776_200,
        "tool_output_tokens": 165_500,
    }


def test_published_observation_without_double_counting(observation):
    """Hand calculation from #3717: H=5500+14000+8800+7500+314=36114.

    H/W*100 -> 3.6%; B/W*100 -> 16.6%; B/H -> 4.6.
    Accounted=36114+776200=812314; remaining=1000000-812314=187686.
    Bash results are already inside messages, so B is never added again.
    """
    result = budget.summarize(observation)
    assert result["harness_tokens"] == 36_114
    assert result["harness_window_pct"] == 3.6
    assert result["tool_output_window_pct"] == 16.6
    assert result["tool_to_harness_ratio"] == 4.6
    assert result["accounted_tokens"] == 812_314
    assert result["unaccounted_window_tokens"] == 187_686
    assert result["prose_saving"]["status"] == "NOT_EVALUATED"


def test_explicit_prose_bound():
    """Synthetic hand calculation: H=20+10=30, messages=70, tools=40.

    W=200; accounted=100, remaining=100; prose=10 -> 10/200*100=5.0%.
    This is a hypothetical deletion bound, not measured productivity.
    """
    result = budget.summarize({
        "source": "Synthetic hand calculation in test_explicit_prose_bound",
        "window_tokens": 200,
        "harness_tokens": {"instructions": 20, "tools": 10},
        "message_tokens": 70,
        "tool_output_tokens": 40,
        "auto_loaded_prose_tokens": 10,
    })
    assert result["harness_window_pct"] == 15.0
    assert result["tool_output_window_pct"] == 20.0
    assert result["accounted_tokens"] == 100
    assert result["unaccounted_window_tokens"] == 100
    assert result["prose_saving"] == {
        "status": "EVALUATED", "upper_bound_window_pct": 5.0,
    }


def test_zero_harness_does_not_invent_ratio(observation):
    """Hand calculation: H=0; B/H is undefined, not zero or infinity."""
    observation["harness_tokens"] = {"instructions": 0}
    assert budget.summarize(observation)["tool_to_harness_ratio"] is None


def test_measured_zero_prose_is_distinct_from_missing(observation):
    """Hand calculation: measured P=0 gives 100*0/W=0.0%, not unknown."""
    observation["auto_loaded_prose_tokens"] = 0
    assert budget.summarize(observation)["prose_saving"] == {
        "status": "EVALUATED", "upper_bound_window_pct": 0.0,
    }


@pytest.mark.parametrize("key,value", [
    ("window_tokens", 0),
    ("window_tokens", -1),
    ("window_tokens", True),
    ("message_tokens", -1),
    ("message_tokens", 1.5),
    ("tool_output_tokens", "165500"),
    ("tool_output_tokens", None),
    ("auto_loaded_prose_tokens", -1),
    ("auto_loaded_prose_tokens", False),
    ("auto_loaded_prose_tokens", None),
    ("source", ""),
    ("source", " "),
    ("source", 123),
    ("harness_tokens", {}),
    ("harness_tokens", []),
    ("harness_tokens", {"instructions": -1}),
    ("harness_tokens", {"instructions": True}),
    ("harness_tokens", {"instructions": 1.5}),
    ("harness_tokens", {"": 1}),
])
def test_invalid_measurements_rejected(observation, key, value):
    """Invalid domains follow the schema in BOUNDED_TOOL_OUTPUT.md."""
    observation[key] = value
    with pytest.raises(ValueError):
        budget.summarize(observation)


@pytest.mark.parametrize("field", [
    "source", "window_tokens", "harness_tokens", "message_tokens", "tool_output_tokens",
])
def test_missing_required_input_rejected(observation, field):
    del observation[field]
    with pytest.raises(ValueError):
        budget.summarize(observation)


@pytest.mark.parametrize("update", [
    {"tool_output_tokens": 776_201},
    {"message_tokens": 1_000_000},
    {"auto_loaded_prose_tokens": 36_115},
    {"unexpected": 0},
])
def test_inconsistent_or_unknown_fields_rejected(observation, update):
    """#3717 nesting: B<=M; disjoint H+M<=W; prose<=H; no silent typos."""
    observation.update(update)
    with pytest.raises(ValueError):
        budget.summarize(observation)


@pytest.mark.parametrize("value", [None, [], "text"])
def test_top_level_must_be_object(value):
    with pytest.raises(TypeError):
        budget.summarize(value)


def test_cli_matches_documented_example():
    """Run the exact documented fixture through the public CLI."""
    example = ROOT / "docs/examples/context-budget.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), str(example)],
        capture_output=True, text=True, check=True,
    )
    report = json.loads(process.stdout)
    assert report == budget.summarize(json.loads(example.read_text()))
    assert report["harness_window_pct"] == 3.6
    assert report["tool_output_window_pct"] == 16.6
    assert report["prose_saving"]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("raw", [
    "{", '{"source": "first", "source": "second"}', "[]",
])
def test_cli_rejects_bad_input_without_echoing_payload(tmp_path, raw):
    path = tmp_path / "observation.json"
    path.write_text(raw)
    process = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True,
        check=False,
    )
    assert process.returncode == 2  # argparse's standard usage-error status.
    assert process.stdout == ""
    assert "invalid context observation" in process.stderr
    assert "first" not in process.stderr
    assert str(tmp_path) not in process.stderr


def test_cli_missing_file_does_not_echo_path(tmp_path):
    process = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "missing.json")],
        capture_output=True, text=True, check=False,
    )
    assert process.returncode == 2  # argparse's standard usage-error status.
    assert "cannot read context observation" in process.stderr
    assert str(tmp_path) not in process.stderr


def test_cli_rejects_invalid_encoding_without_traceback(tmp_path):
    """Non-UTF-8 input is a usage error, with no payload or path disclosure."""
    path = tmp_path / "invalid.json"
    path.write_bytes(bytes([255]))  # Invalid standalone UTF-8 byte, not a token count.
    process = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True,
        check=False,
    )
    assert process.returncode == 2  # argparse's standard usage-error status.
    assert "invalid context observation" in process.stderr
    assert "Traceback" not in process.stderr
    assert str(tmp_path) not in process.stderr
