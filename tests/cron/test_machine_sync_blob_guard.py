"""Scheduled sync must reject oversized blobs before creating or publishing commits."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("stage,expected", [("pending", 1), ("index", 1), ("small", 0)])
def test_sync_blob_limit_prevents_commit_and_push(tmp_path, stage, expected):
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
      echo 'object blob 104857601'
    else echo 'object blob 10'; fi ;;
  diff) exit 1 ;;
esac
exit 0
''')
    git.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH=f"{bindir}:{env['PATH']}", STAGE=stage, CALLS=str(tmp_path / "calls"))
    result = subprocess.run([shutil.which("bash"), str(ROOT / "scripts/sync/sync-machine-branch.sh"),
                             str(repo)], env=env, capture_output=True, text=True)
    assert result.returncode == expected, result.stdout + result.stderr
    calls = Path(env["CALLS"]).read_text().splitlines()
    if expected:
        assert "100 MiB" in result.stdout + result.stderr
        assert not any(line.startswith(("commit ", "push ")) for line in calls)
    else:
        assert any(line.startswith("push ") for line in calls)
