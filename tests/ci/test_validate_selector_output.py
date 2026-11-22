"""Issue #4227 contract examples, constructed independently as literal maps.

The valid map has one include entry, so its hand-counted matrix size is one.
Each negative example changes one contract property; no network is used.
"""

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/ci/validate_selector_output.py"


@pytest.fixture
def sample(tmp_path):
    script = tmp_path / SOURCE.name
    script.write_bytes(SOURCE.read_bytes())
    return script, {"include": [{"name": "core-1.unit", "targets": "tests/core", "mode": "xdist"}]}


def output(matrix, scope="modules"):
    return f"matrix={json.dumps(matrix)}\nscope={scope}\n"


@pytest.mark.parametrize("scope", ["full", "modules", "skip"])
def test_valid(sample, scope):
    script, matrix = sample
    assert runpy.run_path(str(script))["validate"](output(matrix, scope)) == 1


@pytest.mark.parametrize("broken", [
    "json", "object", "include-missing", "include-type", "include-empty", "entry-type",
    "name-missing", "name-empty", "name-type", "name-unsafe", "name-duplicate",
    "targets-missing", "targets-empty", "targets-type", "mode-missing", "mode-invalid",
    "scope-missing", "scope-empty", "scope-invalid", "matrix-missing", "matrix-duplicate",
    "scope-duplicate", "json-duplicate", "json-nonfinite", "axis-invalid", "exclude-invalid",
])
def test_contract_rule(sample, broken):
    script, matrix = sample
    entry = matrix["include"][0]
    text = None
    if broken == "json":
        text = "matrix={bad}\nscope=full\n"
    elif broken == "object":
        matrix = []
    elif broken == "include-missing":
        matrix = {}
    elif broken == "include-type":
        matrix = {"include": {}}
    elif broken == "include-empty":
        matrix = {"include": []}
    elif broken == "entry-type":
        matrix = {"include": ["core"]}
    elif broken.startswith("name-"):
        if broken == "name-missing":
            del entry["name"]
        elif broken == "name-duplicate":
            matrix["include"].append(dict(entry))
        else:
            entry["name"] = {"name-empty": " ", "name-type": 1, "name-unsafe": "core / bad"}[broken]
    elif broken.startswith("targets-"):
        if broken == "targets-missing":
            del entry["targets"]
        else:
            entry["targets"] = {"targets-empty": " \t", "targets-type": []}[broken]
    elif broken.startswith("mode-"):
        if broken == "mode-missing":
            del entry["mode"]
        else:
            entry["mode"] = "parallel"
    elif broken == "scope-missing":
        text = output(matrix).split("scope=")[0]
    elif broken.startswith("scope-"):
        text = output(matrix, "" if broken == "scope-empty" else "other")
        if broken == "scope-duplicate":
            text = output(matrix) + "scope=full\n"
    elif broken == "matrix-missing":
        text = "scope=modules\n"
    elif broken == "matrix-duplicate":
        text = output(matrix) + f"matrix={json.dumps(matrix)}\n"
    elif broken == "json-duplicate":
        text = 'matrix={"include": [], "include": [{}]}\nscope=full\n'
    elif broken == "json-nonfinite":
        text = output(matrix).replace('"xdist"', 'NaN')
    elif broken == "axis-invalid":
        matrix["python"] = "3.x"
    elif broken == "exclude-invalid":
        matrix["exclude"] = ["core"]
    validate = runpy.run_path(str(script))["validate"]
    with pytest.raises((ValueError, TypeError)):
        validate(output(matrix) if text is None else text)


@pytest.mark.parametrize("advisory,expected", [(False, 1), (True, 0)])
def test_cli_invalid(sample, tmp_path, advisory, expected):
    script, _ = sample
    source = tmp_path / "selector-output"
    source.write_text("matrix={}\nscope=skip\n")
    destination = tmp_path / "step-output"
    result = subprocess.run(
        [sys.executable, str(script), str(source), "--github-output", str(destination)]
        + (["--advisory"] if advisory else []),
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == expected
    assert destination.read_text() == "matrix-size=0\n"
    assert "::warning::" in result.stdout if advisory else "::error::" in result.stdout
