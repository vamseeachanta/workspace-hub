"""Scheduled sync must reject oversized blobs before creating or publishing commits."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
# GitHub's documented 100 MiB limit, converted independently to bytes.
LIMIT_BYTES = 100 * 1024 * 1024


@pytest.mark.parametrize("stage,size,expected", [
    ("pending", LIMIT_BYTES + 1, 1), ("index", LIMIT_BYTES + 1, 1),
    ("pending", LIMIT_BYTES, 0), ("index", LIMIT_BYTES, 0), ("small", 10, 0),
])
def test_sync_blob_limit_prevents_commit_and_push(tmp_path, stage, size, expected):
    repo = tmp_path / "machine"
    (repo / ".git").mkdir(parents=True)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    git = bindir / "git"
    git.write_text('''#!/bin/bash
printf '%s\\n' "$*" >> "$CALLS"
case "$1" in
  rev-parse) echo "machine/$(hostname -s)" ;;
  rev-list)
    if [[ "$*" == *--objects* ]]; then echo object; else echo 0; fi ;;
  ls-files) echo index-object ;;
  cat-file)
    input=$(cat)
    if [[ "$STAGE" == pending && "$input" == object ]] ||
       [[ "$STAGE" == index && "$input" == index-object ]]; then
      echo "object blob $BLOB_BYTES"
    else echo 'object blob 10'; fi ;;
  diff) exit 1 ;;
esac
exit 0
''', encoding="utf-8", newline="\n")
    git.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH=f"{bindir}{os.pathsep}{env['PATH']}", STAGE=stage,
               BLOB_BYTES=str(size), CALLS=str(tmp_path / "calls"))
    result = subprocess.run([shutil.which("bash"), str(ROOT / "scripts/sync/sync-machine-branch.sh"),
                             str(repo)], env=env, capture_output=True, text=True,
                            encoding="utf-8")
    assert result.returncode == expected, result.stdout + result.stderr
    calls = Path(env["CALLS"]).read_text(encoding="utf-8").splitlines()
    if expected:
        assert "100 MiB" in result.stdout + result.stderr
        assert not any(line.startswith(("commit ", "push ")) for line in calls)
    else:
        assert any(line.startswith("push ") for line in calls)


@pytest.mark.parametrize("size,expected", [(10, 0), (LIMIT_BYTES, 0),
                                         (LIMIT_BYTES + 1, 1)])
def test_real_git_pending_history(tmp_path, size, expected):
    """Exercise the actual history pipeline with trees and named blob records."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args, input=None):
        return subprocess.run([shutil.which("git"), *args], cwd=tmp_path, env=env,
                              input=input, capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout.strip()

    git("init", "--quiet")
    empty_tree = git("mktree", input="")
    base = git("commit-tree", empty_tree, input="test: initial state\n")
    git("update-ref", "refs/remotes/origin/main", base)
    payload = tmp_path / "payload"
    payload.touch()
    os.truncate(payload, size)
    blob = git("hash-object", "-w", "payload")
    tree = git("mktree", input=f"100644 blob {blob}\tpayload\n")
    pending = git("commit-tree", tree, "-p", base, input="test: pending state\n")
    # Removing the blob at the tip must not hide oversized unpublished history.
    tip = git("commit-tree", empty_tree, "-p", pending, input="test: empty tip\n")
    git("update-ref", "HEAD", tip)
    source = (ROOT / "scripts/sync/sync-machine-branch.sh").read_text(encoding="utf-8")
    function = source.split("check_blob_sizes() {", 1)[1].split("\n}", 1)[0]
    pipeline = next(line for line in source.splitlines()
                    if line.startswith("git rev-list --objects ")).removesuffix(" ||")
    # Execute production guard code only; no mirror, commit or push is permitted.
    result = subprocess.run([shutil.which("bash"), "-c",
                             "set -o pipefail\ncheck_blob_sizes() {" + function +
                             "\n}\n" + pipeline], cwd=tmp_path, env=env,
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == expected, result.stdout + result.stderr
    assert ("100 MiB" in result.stderr) == bool(expected)
