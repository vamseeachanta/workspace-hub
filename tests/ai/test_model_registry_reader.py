"""Exercise the shell readers against declared synthetic registry values.

Source for expected integers: CONTEXT_VALUES and FALLBACK below. These assigned
fixture values distinguish keys; they make no claims about real model limits.
"""

import os
from pathlib import Path
import subprocess

import pytest


READER = Path(__file__).resolve().parent.parent.parent / "scripts/lib/model-registry.sh"
# Put regex lookalikes first so a nonliteral lookup cannot pass by ordering.
CONTEXT_VALUES = {
    "samplew": 111,
    "sample[wide]": 222,
    "sampleXrelease": 333,
    "sample.release": 444,
    "ordinary": 555,
    "tabbed": 666,
    "zero": 0,
}
FALLBACK = 777
MODEL_ID = "sample[wide].release"


@pytest.fixture
def registry(tmp_path):
    path = tmp_path / "registry.yaml"
    entries = "".join(f"  {key}: {value}\n" for key, value in CONTEXT_VALUES.items())
    path.write_text(
        f'latest_models:\n  test_primary: "{MODEL_ID}"  # retained comment\n'
        f"context_windows_k:\n{entries}"
    )
    return path


def read_registry(registry, function, *args):
    return subprocess.run(
        ["bash", "-c", 'source "$1"; shift; "$@"', "bash", str(READER), function, *args],
        env={**os.environ, "MODEL_REGISTRY_FILE": str(registry)},
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.mark.parametrize("key, expected", CONTEXT_VALUES.items())
def test_context_keys_are_literal(registry, key, expected):
    result = read_registry(registry, "registry_ctx_k", key, str(FALLBACK))
    assert result.stdout == f"{expected}\n"
    assert result.stderr == ""


@pytest.mark.parametrize("key", ["sample[wide]", "sample.release"])
def test_context_lookalike_cannot_replace_absent_key(registry, key):
    lookalikes = ("samplew", "sampleXrelease")
    registry.write_text(
        "context_windows_k:\n"
        + "".join(f"  {name}: {CONTEXT_VALUES[name]}\n" for name in lookalikes)
    )
    result = read_registry(registry, "registry_ctx_k", key, str(FALLBACK))
    assert result.stdout == f"{FALLBACK}\n"
    assert result.stderr == ""


def test_unknown_context_uses_requested_fallback(registry):
    result = read_registry(registry, "registry_ctx_k", "unknown", str(FALLBACK))
    assert result.stdout == f"{FALLBACK}\n"
    assert result.stderr == ""


@pytest.mark.parametrize(
    "entry",
    [
        "  ordinary:{value}\n",
        "\tordinary:\t{value} # comment\n",
        "    ordinary:  {value}  # comment\n",
        "  ordinary: {value}",
    ],
)
def test_context_supported_formatting(registry, entry):
    registry.write_text(
        "context_windows_k:\n" + entry.format(value=CONTEXT_VALUES["ordinary"])
    )
    result = read_registry(registry, "registry_ctx_k", "ordinary", str(FALLBACK))
    assert result.stdout == f"{CONTEXT_VALUES['ordinary']}\n"
    assert result.stderr == ""


def test_context_first_matching_value_wins(registry):
    with registry.open("a") as stream:
        stream.write(f"  ordinary: {FALLBACK}\n")
    result = read_registry(registry, "registry_ctx_k", "ordinary", str(FALLBACK))
    assert result.stdout == f"{CONTEXT_VALUES['ordinary']}\n"


def test_context_empty_value_uses_requested_fallback(registry):
    registry.write_text("context_windows_k:\n  ordinary: # no numeric value\n")
    result = read_registry(registry, "registry_ctx_k", "ordinary", str(FALLBACK))
    assert result.stdout == f"{FALLBACK}\n"
    assert result.stderr == ""


def test_latest_model_reader_preserves_quoted_id(registry):
    result = read_registry(registry, "registry_model", "test_primary", "unused")
    assert result.stdout == f"{MODEL_ID}\n"
    assert result.stderr == ""


def test_latest_model_reader_preserves_fallback_warning(registry):
    result = read_registry(registry, "registry_model", "unknown", "fallback-model")
    assert result.stdout == "fallback-model\n"
    assert "WARN: key 'unknown' not found" in result.stderr
    assert "using fallback 'fallback-model'" in result.stderr
