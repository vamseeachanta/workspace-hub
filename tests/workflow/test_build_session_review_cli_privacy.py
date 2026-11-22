"""Subprocess coverage for private argument errors and unchanged CLI parsing."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


CLI = (Path(__file__).resolve().parent.parent.parent
       / "scripts" / "workflow" / "build_session_review.py")
SENTINEL = "SYNTHETIC_PRIVATE_ARGUMENT"
# Python argparse documentation, "Exiting methods": invalid arguments exit 2.
# https://docs.python.org/3/library/argparse.html#exiting-methods
PARSE_ERROR = 2

# Run the repository entry point with its post-parse dependencies replaced.
# The relocated output root also protects committed reports if parsing regresses.
BOOTSTRAP = """
import json
from pathlib import Path
import runpy
import sys

cli, root, mode, *args = sys.argv[1:]
root = Path(root)
main = runpy.run_path(cli)["main"]
scope = main.__globals__
scope["__file__"] = str(root / "scripts" / "workflow" / "entry.py")

def forbidden(*args, **kwargs):
    (root / "post-parse-called").write_text("unexpected work", encoding="utf-8")
    raise AssertionError("post-parse work ran")

def derive(base, repo_root, **kwargs):
    assert repo_root == root
    return {"base": base, "refs": [], **kwargs}

def build(payload, output, patterns, *, public, repo_root):
    assert output == root / "docs" / "reports" / "sessions"
    assert repo_root == root and public and patterns == []
    (root / "rendered.json").write_text(json.dumps(payload), encoding="utf-8")
    return {"file": "page.html", "slug": payload["slug"]}

scope["sani"].load_deny_patterns = forbidden if mode == "trap" else lambda path: []
scope["_git"] = forbidden
scope["derive_payload_from_git"] = forbidden if mode == "trap" else derive
scope["build"] = forbidden if mode == "trap" else build
raise SystemExit(main(args))
"""


def run_cli(args, tmp_path, *, mode=None):
    command = [sys.executable, str(CLI), *args]
    if mode is not None:
        command = [sys.executable, "-c", BOOTSTRAP, str(CLI), str(tmp_path), mode, *args]
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True)


def assert_private_failure(result):
    assert result.returncode == PARSE_ERROR
    assert SENTINEL not in result.stdout
    assert SENTINEL not in result.stderr
    assert result.stdout == ""
    assert "usage:" in result.stderr
    assert "[-h]" in result.stderr
    assert "error: invalid arguments" in result.stderr


def test_unknown_option_is_private(tmp_path):
    result = run_cli([
        "--from-git", "--since", "HEAD", "--emit-payload", "derived.json",
        f"--{SENTINEL}",
    ], tmp_path)
    assert_private_failure(result)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("failure", ["unknown-option", "missing-value"])
def test_parse_failure_has_no_side_effects(tmp_path, failure):
    args = ["--from-git", "--since", "HEAD", "--emit-payload", f"{SENTINEL}.json"]
    args += [f"--{SENTINEL}"] if failure == "unknown-option" else ["--title"]
    result = run_cli(args, tmp_path, mode="trap")
    assert_private_failure(result)
    assert list(tmp_path.iterdir()) == []


def test_help_remains_available(tmp_path):
    result = run_cli(["--help"], tmp_path, mode="trap")
    # Python sys.exit documentation: zero denotes successful termination.
    # https://docs.python.org/3/library/sys.html#sys.exit
    assert result.returncode == 0
    assert result.stderr == ""
    assert "Render a lean session-review page." in result.stdout
    for option in ("payload", "--from-git", "--since", "--slug", "--title",
                   "--headline", "--date", "--emit-payload"):
        assert option in result.stdout
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("emit", [False, True])
def test_successful_git_arguments_remain_available(tmp_path, emit):
    args = ["--from-git", "--since", "HEAD", "--slug", "demo", "--title", "Demo",
            "--headline", "Summary", "--date", "2026-10-15"]
    output = "derived.json" if emit else "rendered.json"
    if emit:
        args += ["--emit-payload", output]
    result = run_cli(args, tmp_path, mode="smoke")
    # Successful sys.exit status, as cited in test_help_remains_available.
    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads((tmp_path / output).read_text(encoding="utf-8"))
    assert payload == {
        "base": "HEAD", "refs": [], "slug": "demo", "title": "Demo",
        "headline": "Summary", "date": "2026-10-15",
    }
    assert {path.name for path in tmp_path.iterdir()} == {output}


def test_successful_manual_payload_remains_available(tmp_path):
    payload = {"slug": "demo", "title": "Demo", "date": "2026-10-15", "refs": []}
    (tmp_path / "payload.json").write_text(json.dumps(payload), encoding="utf-8")
    result = run_cli(["payload.json"], tmp_path, mode="smoke")
    # Successful sys.exit status, as cited in test_help_remains_available.
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads((tmp_path / "rendered.json").read_text(encoding="utf-8")) == payload
    assert {path.name for path in tmp_path.iterdir()} == {"payload.json", "rendered.json"}
