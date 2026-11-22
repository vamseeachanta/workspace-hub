"""Execute the canonical contract's synthetic files verbatim, without packages."""

import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/standards/UV_WORKFLOW_CONTRACT.md"
FILE_BLOCK = re.compile(
    r"<!-- example-file: ([\w./-]+) -->\n```\w+\n(.*?)\n```", re.DOTALL
)
EXAMPLE_FILES = {
    "pyproject.toml",
    "toy_workflow/__init__.py",
    "toy_workflow/__main__.py",
    "toy_workflow/engine.py",
    "toy_workflow/router.py",
    "examples/workflows/scaled_sum/input.yml",
    "docs/registry/workflows.yaml",
    "tests/workflows/test_scaled_sum.py",
}


@pytest.fixture
def example(tmp_path):
    blocks = FILE_BLOCK.findall(CONTRACT.read_text(encoding="utf-8"))
    assert {name for name, _ in blocks} == EXAMPLE_FILES
    assert len(blocks) == len(EXAMPLE_FILES), "duplicate example file"
    for name, body in blocks:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body + "\n", encoding="utf-8")
    return tmp_path


def run_python(root, *args):
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, *args], cwd=root, env=env,
        capture_output=True, text=True, check=False,
    )


def test_documented_module_invocation_and_hand_calculation(example):
    completed = run_python(
        example, "-m", "toy_workflow", "examples/workflows/scaled_sum/input.yml"
    )
    assert completed.returncode == 0, completed.stderr
    # Contract, "Synthetic arithmetic basis": (2 + 3 + 5) * 4 = 40 by hand.
    assert json.loads((example / "results/scaled_sum.json").read_text()) == {"total": 40}


@pytest.mark.parametrize("basename", ["scaled", "sum", "scaled_sum_extra", "other", ""])
def test_unknown_basename_fails_without_output(example, basename):
    path = example / "examples/workflows/scaled_sum/input.yml"
    cfg = yaml.safe_load(path.read_text())
    cfg["basename"] = basename
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    completed = run_python(example, "-m", "toy_workflow", str(path.relative_to(example)))
    assert completed.returncode != 0
    assert "ValueError: unknown basename" in completed.stderr
    assert not (example / cfg["output"]).exists()


@pytest.mark.parametrize("cfg", [{}, [], {"basename": None}])
def test_missing_or_malformed_routing_key_fails(example, cfg):
    path = example / "examples/workflows/scaled_sum/input.yml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    completed = run_python(example, "-m", "toy_workflow", str(path.relative_to(example)))
    assert completed.returncode != 0
    assert "ValueError: unknown basename" in completed.stderr
    assert not (example / "results").exists()


def test_registry_matches_example_and_current_normalizer(example):
    registry = yaml.safe_load((example / "docs/registry/workflows.yaml").read_text())
    # Schema and row versions follow the linked generator's REG_V2 test fixture.
    assert registry["schema_version"] == 2
    row, = registry["workflows"]
    cfg = yaml.safe_load((example / row["input"]).read_text())
    assert row["id"] == row["basename"] == cfg["basename"] == "scaled_sum"
    assert row["outputs"] == row["result"]["outputs"] == [cfg["output"]]
    assert row["runtime"] == "offline"
    assert (example / row["test"]).is_file()
    assert {p.parent.name for p in (example / "examples/workflows").glob("*/input.yml")} == {
        row["basename"]
    }
    command = shlex.split(registry["invocation"].format(input=row["input"]))
    assert command == ["uv", "run", "python", "-m", "toy_workflow", row["input"]]
    # Use the same interpreter selected by uv for pytest; no nested environment.
    completed = run_python(example, *command[3:])
    assert completed.returncode == 0, completed.stderr
    assert {p.relative_to(example).as_posix() for p in (example / "results").iterdir()} == set(
        row["outputs"]
    )
    for output in row["outputs"]:
        assert (example / output).stat().st_size > 0
        # Independent hand calculation in the contract, not the router's return value.
        assert json.loads((example / output).read_text()) == {"total": 40}

    spec = importlib.util.spec_from_file_location(
        "contract_manifest", ROOT / "scripts/workflow/generate_workflow_manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    normalized = module.normalize_row("synthetic", registry, row)
    for field in ("id", "basename", "input", "outputs", "runtime", "result", "version"):
        assert normalized[field] == row[field]
    assert normalized["invocation"] == registry["invocation"]
    assert normalized["license_gated"] is False
    assert normalized["request_schema"] is None
    assert normalized["response_schema"] is None
    assert normalized["determinism"] is None


def test_registry_test_reference_runs_verbatim(example):
    registry = yaml.safe_load((example / "docs/registry/workflows.yaml").read_text())
    row, = registry["workflows"]
    completed = run_python(example, row["test"])
    assert completed.returncode == 0, completed.stderr
    assert "OK" in completed.stderr


def test_contract_local_links_resolve():
    text = CONTRACT.read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    assert links
    for target in links:
        if "://" not in target:
            assert (CONTRACT.parent / target.split("#")[0]).is_file(), target
