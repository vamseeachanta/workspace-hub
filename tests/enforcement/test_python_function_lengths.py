"""Behavior tests for the Python physical-line guardrail."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "enforcement" / "check_python_function_lengths.py"


def _run(tmp_path: Path, source: str, *options: str) -> subprocess.CompletedProcess[str]:
    target = tmp_path / "sample.py"
    target.write_text(source, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(CHECKER), *options, str(target)],
        capture_output=True,
        text=True,
    )


def _function(line_count: int, header: str = "def sample():") -> str:
    return "\n".join([header, *["    pass"] * (line_count - 1)]) + "\n"


def test_rejects_a_51_line_function(tmp_path):
    result = _run(tmp_path, _function(51), "--max-function-lines", "50")

    assert result.returncode == 1
    assert "sample" in result.stdout
    assert "51" in result.stdout


def test_rejects_nested_and_async_functions_independently(tmp_path):
    nested = "def outer():\n" + "\n".join(
        ["    async def nested():", *["        pass"] * 50]
    ) + "\n"

    result = _run(tmp_path, nested, "--max-function-lines", "50")

    assert result.returncode == 1
    assert "nested" in result.stdout
    assert "51" in result.stdout


def test_decorators_are_included_in_the_function_span(tmp_path):
    source = "@first\n@second\ndef decorated():\n" + "    pass\n" * 48

    result = _run(tmp_path, source, "--max-function-lines", "50")

    assert result.returncode == 1
    assert "decorated" in result.stdout
    assert "51" in result.stdout


def test_comments_and_blank_lines_are_included_in_the_function_span(tmp_path):
    interior = ["    # comment" if index % 2 else "" for index in range(49)]
    source = "\n".join(["def spaced():", *interior, "    pass"]) + "\n"

    result = _run(tmp_path, source, "--max-function-lines", "50")

    assert result.returncode == 1
    assert "spaced" in result.stdout
    assert "51" in result.stdout


def test_accepts_a_valid_50_line_function_and_400_line_file(tmp_path):
    source = _function(50) + "\n" * 350

    result = _run(
        tmp_path,
        source,
        "--max-file-lines",
        "400",
        "--max-function-lines",
        "50",
    )

    assert result.returncode == 0


def test_rejects_a_401_line_file_with_cli_limit(tmp_path):
    result = _run(tmp_path, "pass\n" * 401, "--max-file-lines", "400")

    assert result.returncode == 1
    assert "401" in result.stdout
