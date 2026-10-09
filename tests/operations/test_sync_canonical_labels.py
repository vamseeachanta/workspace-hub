import os
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/operations/sync-canonical-labels.sh"


def _write_fake_gh(tmp_path: Path, body: str) -> Path:
    gh = tmp_path / "gh"
    gh.write_text(body, encoding="utf-8")
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    return gh


def _run_sync(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}{os.pathsep}{env['PATH']}"
    env["GH_LOG"] = str(tmp_path / "gh.log")
    return subprocess.run(
        ["bash", str(SCRIPT), "--owner", "owner", "--repo", "repo", *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


FAKE_GH_BASE = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_LOG"
if [[ "$1 $2" == "label list" ]]; then
  printf '%s\\n' 'dispatch:ready\tfbca04\told ready'
  exit 0
fi
if [[ "$1 $2" == "label create" ]]; then
  exit 0
fi
printf 'unexpected gh call: %s\\n' "$*" >&2
exit 64
"""


def test_sync_canonical_labels_defaults_to_dry_run_and_reports_drift(tmp_path):
    log = tmp_path / "gh.log"
    _write_fake_gh(tmp_path, FAKE_GH_BASE)
    result = _run_sync(tmp_path)

    assert result.returncode == 0
    assert "would update owner/repo dispatch:ready" in result.stdout
    assert "ok owner/repo" in result.stdout
    calls = log.read_text(encoding="utf-8")
    assert "label list --repo owner/repo" in calls
    assert "label create" not in calls


def test_sync_canonical_labels_requires_apply_before_writing(tmp_path):
    log = tmp_path / "gh.log"
    _write_fake_gh(tmp_path, FAKE_GH_BASE)
    result = _run_sync(tmp_path, "--apply")

    assert result.returncode == 0
    calls = log.read_text(encoding="utf-8")
    assert "label create dispatch:ready --repo owner/repo" in calls
    assert "--force" in calls


def test_sync_canonical_labels_redirects_gh_stdin_inside_label_loop(tmp_path):
    log = tmp_path / "gh.log"
    gh = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_LOG"
if [[ "$1 $2" == "label create" ]]; then
  if read -r swallowed; then
    printf 'gh consumed stdin: %s\\n' "$swallowed" >&2
    exit 91
  fi
  exit 0
fi
exit 64
"""
    _write_fake_gh(tmp_path, gh)
    result = _run_sync(tmp_path, "--apply")

    assert result.returncode == 0
    assert "gh consumed stdin" not in result.stderr
    calls = log.read_text(encoding="utf-8")
    assert "label create dispatch:ready" in calls
    assert "label create needs:cross-review" in calls


def test_sync_canonical_labels_marks_repo_failed_after_any_label_failure(tmp_path):
    log = tmp_path / "gh.log"
    gh = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GH_LOG"
if [[ "$1 $2" == "label create" && "$3" == "dispatch:done" ]]; then
  printf 'nope\\n' >&2
  exit 17
fi
if [[ "$1 $2" == "label create" ]]; then
  exit 0
fi
exit 64
"""
    _write_fake_gh(tmp_path, gh)
    result = _run_sync(tmp_path, "--apply")

    assert result.returncode != 0
    assert "FAILED owner/repo" in result.stderr
    assert "ok owner/repo" not in result.stdout
