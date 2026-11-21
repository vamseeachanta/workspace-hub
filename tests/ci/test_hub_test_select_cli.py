"""CLI regressions for the saved-diff examples in issue #4228.

Expectations are hand-enumerated: the rename joins the data and skills
families (one literal file each, hence two files); documentation selects none.
R100 denotes an unchanged rename in Git's --name-status -z format; basis:
https://git-scm.com/docs/git-diff, also cited by test_hub_test_select.py.
Exit zero means success; malformed input must fail without partial selection.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

# This module is under tests/ci, so the third ancestor is the repository root.
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/hub_test_select.py"


def _snapshot(root):
    """Record directory membership as well as every file's exact bytes."""
    return {
        path.relative_to(root).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in root.rglob("*")
    }


@pytest.fixture
def run_selector(tmp_path):
    root = tmp_path / "selector-root"
    config = root / "config/ci"
    config.mkdir(parents=True)
    # Literal inventory from the issue example, independent of selector output.
    inventory = {
        "families": {
            "tests/data": ["tests/data/test_alpha.py"],
            "tests/skills": ["tests/skills/test_beta.py"],
        }
    }
    (config / "hub-test-families.json").write_text(json.dumps(inventory), encoding="utf-8")
    (config / "hub-test-rules.json").write_bytes(
        (ROOT / "config/ci/hub-test-rules.json").read_bytes()
    )
    for name in ("tests/data/test_alpha.py", "tests/skills/test_beta.py"):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            'raise AssertionError("Dry run imported a fixture test module")\n'
            '\ndef test_must_not_run():\n'
            '    raise AssertionError("Dry run executed a fixture test")\n',
            encoding="utf-8",
        )
    caller = tmp_path / "caller"
    caller.mkdir()
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    def run(command, raw):
        diff = root / "saved-diff.bin"
        diff.write_bytes(raw)
        before = _snapshot(tmp_path)
        try:
            return subprocess.run(
                [sys.executable, str(SCRIPT), command, "--root", str(root),
                 "--diff-file", str(diff)],
                cwd=caller, env=env, capture_output=True, text=True,
                # Operational bound in seconds; no selector timing is asserted.
                timeout=30,
            )
        finally:
            assert _snapshot(tmp_path) == before

    return run


def test_cli_rename_unions_source_and_destination_families(run_selector):
    raw = b"R100\0scripts/data/old.py\0tests/skills/test_beta.py\0"
    expected_json = {
        "paths": [
            {"status": "R100", "path": "scripts/data/old.py",
             "rule": "script-area", "families": ["tests/data"]},
            {"status": "R100", "path": "tests/skills/test_beta.py",
             "rule": "test-area", "families": ["tests/skills"]},
        ],
        "families": ["tests/data", "tests/skills"],
        "files": ["tests/data/test_alpha.py", "tests/skills/test_beta.py"],
        "file_count": 2,
    }
    expected_text = (
        "R100 scripts/data/old.py\n"
        "  rule: script-area\n"
        "  families: tests/data\n"
        "R100 tests/skills/test_beta.py\n"
        "  rule: test-area\n"
        "  families: tests/skills\n"
        "Selected families: tests/data, tests/skills\n"
        "Test files: 2\n"
        "Pytest: python -m pytest -q -- tests/data/test_alpha.py tests/skills/test_beta.py\n"
    )
    for command in ("json", "explain"):
        result = run_selector(command, raw)
        assert result.returncode == 0
        assert result.stderr == ""
        if command == "json":
            assert json.loads(result.stdout) == expected_json
        else:
            assert result.stdout == expected_text


def test_cli_document_deletion_selects_no_tests(run_selector):
    raw = b"D\0docs/guide.md\0"
    expected_json = {
        "paths": [{"status": "D", "path": "docs/guide.md",
                   "rule": "documentation", "families": []}],
        "families": [],
        "files": [],
        "file_count": 0,
    }
    expected_text = (
        "D docs/guide.md\n"
        "  rule: documentation\n"
        "  families: none\n"
        "Selected families: none\n"
        "Test files: 0\n"
        "Pytest: none\n"
    )
    for command in ("json", "explain"):
        result = run_selector(command, raw)
        assert result.returncode == 0
        assert result.stderr == ""
        assert "python -m pytest" not in result.stdout
        if command == "json":
            assert json.loads(result.stdout) == expected_json
        else:
            assert result.stdout == expected_text


@pytest.mark.parametrize("command", ["json", "explain"])
@pytest.mark.parametrize("raw", [
    # A valid selecting record precedes each error to detect partial output.
    b"M\0tests/data/test_alpha.py\0R100\0scripts/data/old.py\0",
    b"M\0tests/data/test_alpha.py\0D\0docs/guide.md",
], ids=["incomplete-rename", "missing-final-nul"])
def test_cli_rejects_truncated_diff_without_partial_selection(run_selector, command, raw):
    result = run_selector(command, raw)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == (
        "Selection failed: check refs, inventory, rules and diff format\n"
    )
    assert "Traceback" not in result.stderr
