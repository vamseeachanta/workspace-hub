"""Calibrate late refusal in the canonical recipe, without launching children.

Source: docs/modules/testing/TESTING_FRAMEWORK_STANDARDS.md, "Disposable
actual-CLI recipe and worked example", delimited block and Answer table.
Literal outcomes and markers below encode that table independently of invoke.
Real import-path evidence remains in test_python_runner_entrypoint_contract.py.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

import pytest

# This file is under tests/docs; two parent directories reach the checkout root.
ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs/modules/testing/TESTING_FRAMEWORK_STANDARDS.md"
# Caller-selected test budget, matching the baseline file's example_results.
# The standard's input contract requires a positive subprocess watchdog.
WATCHDOG_SECONDS = 30
SENTINEL = "ENTRYPOINT_SENTINEL\n"
TEST_BODY = "ENTRYPOINT_TEST_BODY\n"
IMPORT_ERROR = "ModuleNotFoundError: No module named 'scripts'\n"
UNEXPECTED_OUTPUT = "INJECTED_UNEXPECTED_EXIT"


class Observation(NamedTuple):
    name: str
    caller: str
    runner: str | None
    collect: bool
    outcome: pytest.ExitCode
    stdout: str
    stderr: str = ""
    fail: bool = False


# Flatten the documented invocation sequence, without reproducing its loops.
# Outcomes/markers: the standard's Answer table and separate test-body marker.
OBSERVATIONS = (
    Observation("good-checkout-collect", "checkout", "good_runner.py", True,
                pytest.ExitCode.OK, SENTINEL),
    Observation("broken-checkout-collect", "checkout", "broken_runner.py", True,
                pytest.ExitCode.INTERRUPTED, "", IMPORT_ERROR),
    Observation("good-checkout-run", "checkout", "good_runner.py", False,
                pytest.ExitCode.OK, SENTINEL + TEST_BODY),
    Observation("broken-checkout-run", "checkout", "broken_runner.py", False,
                pytest.ExitCode.INTERRUPTED, "", IMPORT_ERROR),
    Observation("failing-checkout-run", "checkout", "good_runner.py", False,
                pytest.ExitCode.TESTS_FAILED, SENTINEL + TEST_BODY, fail=True),
    Observation("good-outside-collect", "outside", "good_runner.py", True,
                pytest.ExitCode.OK, SENTINEL),
    Observation("broken-outside-collect", "outside", "broken_runner.py", True,
                pytest.ExitCode.INTERRUPTED, "", IMPORT_ERROR),
    Observation("good-outside-run", "outside", "good_runner.py", False,
                pytest.ExitCode.OK, SENTINEL + TEST_BODY),
    Observation("broken-outside-run", "outside", "broken_runner.py", False,
                pytest.ExitCode.INTERRUPTED, "", IMPORT_ERROR),
    Observation("failing-outside-run", "outside", "good_runner.py", False,
                pytest.ExitCode.TESTS_FAILED, SENTINEL + TEST_BODY, fail=True),
    Observation("module-checkout-collect", "checkout", None, True,
                pytest.ExitCode.OK, SENTINEL),
)
# Independently chosen controls span TESTS_FAILED, INTERRUPTED and OK expectations.
LATE_POSITIONS = (
    "failing-checkout-run", "broken-outside-run", "module-checkout-collect",
)


def documented_recipe():
    text = STANDARD.read_text()
    start = "<!-- python-entrypoint-probe:start -->"
    end = "<!-- python-entrypoint-probe:end -->"
    assert start in text and end in text
    section = text.split(start, maxsplit=1)[1].split(end, maxsplit=1)[0]
    source = section.split("```python\n", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return compile(source, "<documented entrypoint recipe>", "exec")


def expected_command(observation, repo):
    """Command arguments come from the standard's disposable entrypoint layout."""
    if observation.runner is not None:
        command = [sys.executable, str(repo / "scripts" / observation.runner)]
        return command + (["--collect-only"] if observation.collect else [])
    return [
        sys.executable, "-m", "pytest", "-c", str(repo / "pytest.ini"),
        "--rootdir", str(repo), "--import-mode=importlib", "-p", "no:cacheprovider",
        "-q", "-s", "--collect-only", str(repo / "probe_tests/test_import_probe.py"),
    ]


def scratch_snapshot(scratch):
    return {
        str(path.relative_to(scratch)): path.read_bytes() if path.is_file() else None
        for path in scratch.rglob("*")
    }


class FakeChildren:
    """Only preceding expected observations are synthetic successes."""

    def __init__(self, scratch, position, failure):
        self.scratch = scratch
        self.base = scratch / "recipe"
        self.repo = self.base / "checkout with spaces"
        self.position = position
        self.failure = failure
        self.calls = []
        self.writes = []
        self.writes_at_refusal = None
        self.tree_at_refusal = None
        self.environment = os.environ.copy()
        for key in ("PYTHONPATH", "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PROBE_FAIL"):
            self.environment.pop(key, None)
        self.environment.update(
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1",
        )
        target = next(row for row in OBSERVATIONS if row.name == position)
        self.timeout_error = subprocess.TimeoutExpired(
            expected_command(target, self.repo), timeout=WATCHDOG_SECONDS,
        )

    def make_scratch(self, *, prefix):
        self.writes.append(("mkdtemp", prefix))
        assert prefix == "python-entrypoint-"
        self.base.mkdir()
        return str(self.base)

    def run(self, command, **kwargs):
        # Indexing this independent table rejects extra children as well as order.
        row = OBSERVATIONS[len(self.calls)]
        self.calls.append(row.name)
        assert command == expected_command(row, self.repo)
        cwd = self.repo if row.caller == "checkout" else self.base / "unrelated caller"
        child_env = dict(self.environment, PROBE_EXPECTED_CWD=str(cwd))
        if row.fail:
            child_env["PROBE_FAIL"] = "yes"
        # Compare inherited environment values without exposing them on failure.
        if kwargs.get("env") != child_env:
            pytest.fail("Child environment differs from the sanitized caller", pytrace=False)
        options = {key: value for key, value in kwargs.items() if key != "env"}
        assert options == {
            "cwd": cwd, "capture_output": True,
            "text": True, "timeout": WATCHDOG_SECONDS, "check": False,
        }
        if row.name == self.position:
            self.writes_at_refusal = list(self.writes)
            self.tree_at_refusal = scratch_snapshot(self.scratch)
            if self.failure == "timeout":
                raise self.timeout_error
            # Exit codes source: the standard cites pytest's public ExitCode enum.
            # USAGE_ERROR differs from every selected control's expected outcome.
            assert pytest.ExitCode.USAGE_ERROR != row.outcome
            return subprocess.CompletedProcess(
                command, pytest.ExitCode.USAGE_ERROR, "", UNEXPECTED_OUTPUT,
            )
        return subprocess.CompletedProcess(command, row.outcome, row.stdout, row.stderr)

    def assert_refusal(self):
        names = [row.name for row in OBSERVATIONS]
        # Inclusive prefix: the position's zero-based index plus the refused call.
        expected_count = names.index(self.position) + 1
        assert len(self.calls) == expected_count
        assert self.calls == names[:expected_count]
        assert self.writes_at_refusal is not None
        assert self.writes == self.writes_at_refusal
        assert scratch_snapshot(self.scratch) == self.tree_at_refusal


@pytest.fixture
def fake_children(tmp_path, monkeypatch):
    # pytest's caller selects its temporary parent outside the repository.
    assert not tmp_path.resolve().is_relative_to(ROOT)
    # Poison inherited options to verify the recipe's documented sanitization.
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    monkeypatch.setenv("PYTEST_ADDOPTS", "--invalid-inherited-option")
    monkeypatch.setenv("PYTEST_PLUGINS", "missing_inherited_plugin")
    monkeypatch.setenv("PROBE_FAIL", "yes")
    monkeypatch.setenv("PROBE_TIMEOUT_SECONDS", str(WATCHDOG_SECONDS))

    def install(position, failure):
        children = FakeChildren(tmp_path, position, failure)
        original_write_text = Path.write_text
        original_mkdir = Path.mkdir

        def write_text(path, *args, **kwargs):
            children.writes.append(("write_text", path))
            return original_write_text(path, *args, **kwargs)

        def mkdir(path, *args, **kwargs):
            children.writes.append(("mkdir", path))
            return original_mkdir(path, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", write_text)
        monkeypatch.setattr(Path, "mkdir", mkdir)
        monkeypatch.setattr(tempfile, "mkdtemp", children.make_scratch)
        monkeypatch.setattr(subprocess, "run", children.run)
        return children

    return install


@pytest.mark.parametrize("position", LATE_POSITIONS)
def test_late_timeout_emits_no_success(position, fake_children, capsys):
    children = fake_children(position, "timeout")
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        exec(documented_recipe(), {})
    assert caught.value is children.timeout_error
    children.assert_refusal()
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("position", LATE_POSITIONS)
def test_late_unexpected_exit_emits_no_success(position, fake_children, capsys):
    children = fake_children(position, "unexpected-exit")
    with pytest.raises(AssertionError) as caught:
        exec(documented_recipe(), {})
    # Verify the recipe's status assertion fired, rather than a fake's assertion.
    assert caught.value.args == (
        (position, pytest.ExitCode.USAGE_ERROR, UNEXPECTED_OUTPUT),
    )
    children.assert_refusal()
    assert capsys.readouterr().out == ""
