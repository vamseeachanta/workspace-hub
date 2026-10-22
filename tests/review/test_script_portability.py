"""Portable helper regressions using canned output, never provider services.

Expected VALID and Markdown headings follow validate-review-output.sh's section
contract. The synthetic review supplies each required key independently. Fixture
permissions follow Git 2.44.0 git-update-index --chmod (0644 versus 0755).
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def executable(path, body):
    path.write_text("#!/usr/bin/env bash\n" + body)
    path.chmod(0o755)


def clone_review_fixture(tmp_path, helper_mode):
    """Build a tiny commit from explicit blobs, then clone its indexed modes."""
    source = tmp_path / "source.git"
    subprocess.run(["git", "init", "--bare", "-q", str(source)],
                   check=True, env=clean_env())
    # Synthetic metadata only; no local identity or configuration is changed.
    stream = bytearray(b"commit refs/heads/main\ncommitter Fixture <fixture> "
                       b"1700000000 +0000\ndata 7\nfixture\n")
    helpers = ("validate-review-output.sh", "render-structured-review.py")
    for name in (*helpers, "lib/codex-version-guard.sh",
                 "submit-to-codex.sh", "submit-to-claude.sh", "submit-to-gemini.sh"):
        mode = "100755" if name in helpers and helper_mode == 0o755 else "100644"
        content = (ROOT / "scripts/review" / name).read_bytes()
        stream.extend(f"M {mode} inline scripts/review/{name}\ndata {len(content)}\n".encode())
        stream.extend(content + b"\n")
    stream.extend(b"\ndone\n")
    subprocess.run(["git", "-C", str(source), "fast-import", "--quiet"],
                   input=stream, check=True, capture_output=True, env=clean_env())
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "clone", "--quiet", "--branch", "main",
                    str(source), str(checkout)], check=True,
                   capture_output=True, env=clean_env())
    return checkout


@pytest.mark.parametrize("provider", ["codex", "gemini", "claude"])
@pytest.mark.parametrize("helper_mode", [0o644, 0o755])
def test_submit_with_lost_helper_bits(tmp_path, provider, helper_mode):
    """All sections + explicit MINOR yield VALID, even without execute bits."""
    checkout = clone_review_fixture(tmp_path, helper_mode)
    review = checkout / "scripts" / "review"
    # Also model a filesystem that loses bits after clone.
    for name in ("validate-review-output.sh", "render-structured-review.py"):
        (review / name).chmod(helper_mode)
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps({
        "verdict": "MINOR", "summary": "Fixture result", "issues_found": [],
        "suggestions": [], "questions_for_author": [],
    }))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "provider-stub"
    executable(stub, '''
if [[ ${1:-} == --version ]]; then
  # Known-good boundary from scripts/review/lib/codex-version-guard.sh.
  echo 'codex 0.130.0'; exit 0
fi
while (($#)); do
  if [[ $1 == --output-last-message ]]; then
    cp "$FIXTURE_PAYLOAD" "$2"; exit 0
  fi
  shift
done
cat "$FIXTURE_PAYLOAD"
''')
    # A fake uv only dispatches the interpreter; no package/network work occurs.
    executable(bin_dir / "uv", "shift 3\nexec " + shlex.quote(sys.executable) + ' "$@"\n')
    executable(bin_dir / "getent", "exit 0\n")
    content = tmp_path / "input.md"
    content.write_text("Fixture content\n")
    env = clean_env() | {
        "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
        "HOME": str(tmp_path), "TMPDIR": str(tmp_path),
        "REPO_ROOT": str(checkout), "FIXTURE_PAYLOAD": str(payload),
        "CODEX_BIN": str(stub), "GEMINI_CMD": str(stub),
        "CLAUDE_CMD": str(stub), "CLAUDE_RETRIES": "1", "GEMINI_RETRIES": "1",
    }
    result = subprocess.run(
        ["bash", str(review / f"submit-to-{provider}.sh"),
         "--file", str(content), "--prompt", "Fixture"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "### Verdict: MINOR" in result.stdout
    assert "### Questions for Author" in result.stdout


@pytest.mark.parametrize("missing", [False, True])
def test_hook_paths_crlf(tmp_path, missing):
    """CRLF text and jq output refer to the same literal existing script path."""
    settings = tmp_path / ".claude/settings.json"
    settings.parent.mkdir()
    settings.write_bytes(b'{\r\n"command": "bash hook.sh"\r\n}\r\n')
    if not missing:
        (tmp_path / "hook.sh").write_text("true\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable(bin_dir / "jq", "printf 'hook.sh\\r\\n'\n")
    source = (ROOT / "scripts/readiness/nightly-readiness.sh").read_text()
    # Isolate the production function: the full readiness command probes services.
    function = source.split("check_r_hooks() {", 1)[1].split(
        "} ; check_r_hooks || true", 1
    )[0]
    result = subprocess.run(
        ["bash", "-c", 'log_pass() { echo "PASS $*"; }; '
         'log_fail() { echo "FAIL $*"; }; check_r_hooks() {' + function
         + "}; check_r_hooks"],
        env=clean_env() | {"WORKSPACE_HUB": str(tmp_path),
                           "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
        capture_output=True, text=True, check=True,
    )
    assert "\r" not in result.stdout
    assert "\\r" not in result.stdout
    assert ("FAIL" if missing else "PASS") in result.stdout


def test_native_command_switch_is_verbatim_and_scope_is_local(tmp_path):
    """MSYS2 Filesystem Paths, Automatic Unix -> Windows Path Conversion,
    retrieved 2026-10-22: semicolon-separated prefixes exclude matching argv.
    The hand-derived expected argv is /c plus one quoted mklink command;
    filenames are converted separately, whereas /c is a literal cmd switch.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable(bin_dir / "cmd", '''
printf '%s\\n' "$MSYS2_ARG_CONV_EXCL" "$@" > "$NATIVE_LOG"
''')
    source = (ROOT / "scripts/propagate-ecosystem.sh").read_text()
    functions = source.split("to_win_path() {", 1)[1].split("# --- is_link", 1)[0]
    log = tmp_path / "args.txt"
    result = subprocess.run(
        ["bash", "-c", 'to_win_path() {' + functions
         + '\nPLATFORM=windows; OPT_DRY_RUN=false; '
         'create_directory_link "$1" "$2"; '
         'printf "%s" "${MSYS2_ARG_CONV_EXCL-unset}"',
         "fixture", "C:/target folder", str(tmp_path / "link folder")],
        env=clean_env() | {"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
                           "NATIVE_LOG": str(log), "MSYS2_ARG_CONV_EXCL": "inherited"},
        capture_output=True, text=True, check=True,
    )
    lines = log.read_text().splitlines()
    assert lines[0:2] == ["/c", "/c"]
    assert lines[2].startswith('mklink /J "')
    assert lines[2].endswith('"C:\\target folder"')
    assert result.stdout == "inherited"
