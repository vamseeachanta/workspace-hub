"""Static and offline execution contracts for issue #4227.

Expected names, dependencies and exit-code handling come from the original
workflow. Synthetic caller trees contain no helper checkout. Script equality is
checked directly, independently of the embedding generator's implementation.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ("domain_matrix_aggregate.py", "validate_selector_output.py", "quarantine_args.py")


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "hub"
    for relative in [".github/workflows/domain-matrix.yml", "scripts/ci/embed_domain_matrix.py"] + [
        f"scripts/ci/{name}" for name in SCRIPTS
    ]:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return root


def workflow(repo):
    return yaml.safe_load((repo / ".github/workflows/domain-matrix.yml").read_text(encoding="utf-8"))


def step(config, job, name):
    return next(item for item in config["jobs"][job]["steps"] if item.get("name") == name)


def test_job_identity_and_advisory_default(repo):
    config = workflow(repo)
    jobs = config["jobs"]
    assert set(jobs) == {"discover", "test-domain", "aggregate"}
    assert jobs["discover"]["name"] == "Discover domains"
    assert jobs["test-domain"]["name"] == "Domain ${{ matrix.name }}"
    assert jobs["aggregate"]["name"] == "Aggregate domain results"
    assert jobs["aggregate"]["if"] == "always()"
    assert jobs["aggregate"]["needs"] == ["discover", "test-domain"]
    assert jobs["test-domain"]["needs"] == "discover"
    assert jobs["test-domain"]["strategy"]["fail-fast"] is False
    call = config.get("on", config.get(True))["workflow_call"]
    assert call["inputs"]["enforce-contract"]["default"] is False
    assert call["inputs"]["enforce-contract"]["type"] == "boolean"
    test = step(config, "test-domain", "Run domain tests (${{ matrix.name }})")
    assert test["env"]["TARGETS"] == "${{ matrix.targets }}"
    assert test["env"]["MODE"] == "${{ matrix.mode }}"
    assert jobs["discover"]["outputs"]["matrix-size"] == "${{ steps.sel.outputs.matrix-size }}"


def test_embedded_scripts_equal_sources(repo):
    text = (repo / ".github/workflows/domain-matrix.yml").read_text(encoding="utf-8")
    for name in SCRIPTS:
        block = text.split(f"# BEGIN GENERATED: {name}\n")[1].split(f"# END GENERATED: {name}")[0]
        embedded = block.split("<<'DOMAIN_MATRIX_SCRIPT'\n")[1].split("          DOMAIN_MATRIX_SCRIPT\n")[0]
        actual = "".join(line.removeprefix("          ") for line in embedded.splitlines(keepends=True))
        assert actual == (repo / "scripts/ci" / name).read_text(encoding="utf-8"), (
            "Embedded source differs; run scripts/ci/embed_domain_matrix.py"
        )


def test_generator_check_and_regeneration(repo):
    generator = repo / "scripts/ci/embed_domain_matrix.py"
    command = [sys.executable, str(generator), "--root", str(repo)]
    assert subprocess.run(command + ["--check"], capture_output=True, check=False).returncode == 0
    source = repo / "scripts/ci/quarantine_args.py"
    source.write_text(source.read_text(encoding="utf-8") + "\n# synthetic drift\n", encoding="utf-8", newline="\n")
    assert subprocess.run(command + ["--check"], capture_output=True, check=False).returncode == 1
    subprocess.run(command, capture_output=True, check=True)
    subprocess.run(command + ["--check"], capture_output=True, check=True)


def execute(repo, tmp_path, job, name, **values):
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not on PATH; workflow shell execution unavailable")
    caller = tmp_path / "caller"
    caller.mkdir(exist_ok=True)
    runtime = tmp_path / "runtime"
    runtime.mkdir(exist_ok=True)
    env = dict(os.environ, RUNNER_TEMP=str(runtime), **values)
    return subprocess.run(
        [bash, "--noprofile", "--norc", "-eo", "pipefail", "-c", step(workflow(repo), job, name)["run"]],
        cwd=caller, env=env, capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("valid,enforce,expected", [(True, "false", 0), (False, "false", 0), (False, "true", 1)])
def test_discover_in_caller_tree(repo, tmp_path, valid, enforce, expected):
    caller = tmp_path / "caller"
    caller.mkdir()
    selector = caller / "select.py"
    matrix = {"include": [{"name": "core", "targets": "tests/core", "mode": "seq"}]} if valid else {}
    selector.write_text(f"print('matrix={json.dumps(matrix)}')\nprint('scope=full')\n", encoding="utf-8", newline="\n")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    git = binaries / "git"
    git.write_text('#!/bin/sh\nprintf "src/core.py\\n"\n', encoding="utf-8", newline="\n")
    git.chmod(0o755)
    output = tmp_path / "output"
    result = execute(
        repo, tmp_path, "discover", "Select domain matrix", BASE_SHA="synthetic",
        PUSH_BEFORE="", SELECTOR="select.py", ENFORCE_CONTRACT=enforce,
        GITHUB_OUTPUT=str(output), PATH=str(binaries) + os.pathsep + os.environ["PATH"],
    )
    assert result.returncode == expected, result.stderr
    assert f"matrix-size={1 if valid else 0}\n" in output.read_text(encoding="utf-8")


@pytest.mark.parametrize("test_code,expected", [(0, 0), (5, 0), (1, 1)])
def test_test_domain_quarantine_and_exit_codes(repo, tmp_path, test_code, expected):
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / "quarantine.txt").write_text("tests/core/test_a.py::test_a\n", encoding="utf-8", newline="\n")
    runner = caller / "runner.py"
    arguments = tmp_path / "arguments.json"
    runner.write_text(
        "import json, pathlib, sys\n"
        f'pathlib.Path({str(arguments)!r}).write_text(json.dumps(sys.argv[1:]), encoding="utf-8", newline="\\n")\n'
        f"raise SystemExit({test_code})\n", encoding="utf-8", newline="\n"
    )
    result = execute(
        repo, tmp_path, "test-domain", "Run domain tests (${{ matrix.name }})",
        TARGETS="tests/core", MODE="xdist", SHARD="core", TEST_RUNNER=f"{sys.executable} runner.py",
        QUARANTINE_FILE="quarantine.txt",
    )
    assert result.returncode == expected, result.stderr
    assert json.loads(arguments.read_text(encoding="utf-8")) == [
        "tests/core", "-n", "auto", "--deselect", "tests/core/test_a.py::test_a",
        "--deselect", "core/test_a.py::test_a", "--tb=short", "--junitxml=test-results-core.xml",
    ]


@pytest.mark.parametrize("discover,test,size,enforce,expected", [
    ("success", "success", "1", "false", 0),
    ("success", "success", "0", "false", 0),
    ("success", "success", "0", "true", 1),
    ("failure", "success", "1", "false", 1),
    ("success", "cancelled", "1", "false", 1),
    ("success", "skipped", "0", "false", 1),
])
def test_aggregate_in_caller_tree(repo, tmp_path, discover, test, size, enforce, expected):
    result = execute(
        repo, tmp_path, "aggregate", "Aggregate domain results", DISCOVER_RESULT=discover,
        TEST_DOMAIN_RESULT=test, SCOPE="modules", MATRIX_SIZE=size, ENFORCE_CONTRACT=enforce,
    )
    assert result.returncode == expected, result.stderr


def test_hosted_contract_suite_is_blocking():
    config = yaml.safe_load(
        (ROOT / ".github/workflows/baseline-check.yml").read_text(encoding="utf-8")
    )
    job = config["jobs"]["test"]
    contract = step(config, "test", "Run domain matrix contract tests")
    assert not job.get("continue-on-error", False)
    assert not contract.get("continue-on-error", False)
    assert "if" not in contract
    assert "uv run --no-project --with pytest --with pyyaml" in contract["run"]
    assert "python -m pytest tests/ci/" in contract["run"]
