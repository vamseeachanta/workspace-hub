"""Run the revision 1 worked example literally, with temporary fixture paths.

The hand calculation is byte equality: the builder emits 'example\n' and the
reference contains those same bytes. Adding extra.html gives the singleton
unregistered set {docs/reports/extra.html}.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts/hygiene/check_build_commands.sh"
DOC = ROOT / "scripts/hygiene/BUILD_COMMANDS.md"


def test_worked_example(tmp_path):
    """Execute the documented shell block and compare its documented stdout."""
    document = DOC.read_text()
    script = re.search(r"<!-- example:start -->\n```sh\n(.*?)\n```", document, re.DOTALL)
    output = re.search(r"<!-- output:start -->\n```text\n(.*?)\n```", document, re.DOTALL)
    assert script and output
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"EXAMPLE_ROOT": str(tmp_path), "CHECKER": str(WRAPPER)})
    result = subprocess.run(
        ["sh", "-eu", "-c", script.group(1)], check=False, env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == output.group(1) + "\n"


@pytest.mark.parametrize("argument", ["--run", "--suggest", "--normalise"])
def test_wrapper_refuses_dynamic_flags(argument, tmp_path):
    """A hook invocation cannot opt into code execution or suggestion mode."""
    result = subprocess.run(
        ["sh", str(WRAPPER), argument], check=False, cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "static checks only" in result.stderr


def test_wrapper_shell_syntax():
    """POSIX sh parses the thin wrapper without executing it."""
    assert subprocess.run(["sh", "-n", str(WRAPPER)], check=False, capture_output=True).returncode == 0
