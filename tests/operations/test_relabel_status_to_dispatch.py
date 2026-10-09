from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "operations" / "relabel-status-to-dispatch.sh"


def _fake_gh(tmp_path: Path) -> tuple[Path, Path]:
    gh = tmp_path / "gh"
    log = tmp_path / "gh.calls"
    gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "${FAKE_GH_LOG}"
if [[ "$1 $2" == "repo list" ]]; then
  printf '%s\\n' 'owner/alpha'
  printf '%s\\n' 'owner/beta'
  exit 0
fi
if [[ "$1 $2" == "label list" ]]; then
  repo=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$repo" == "owner/alpha" ]]; then
    printf '%s\\n' 'status:done'
    printf '%s\\n' 'status:closed'
    printf '%s\\n' 'status:implemented'
  fi
  if [[ -f "${FAKE_LABEL_STATE}" ]]; then
    awk -F '\\t' -v repo="$repo" '$1 == repo {print $2}' "${FAKE_LABEL_STATE}"
  fi
  exit 0
fi
if [[ "$1 $2" == "label create" ]]; then
  label="$3"
  repo=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  printf '%s\\t%s\\n' "$repo" "$label" >> "${FAKE_LABEL_STATE}"
  exit 0
fi
if [[ "$1 $2" == "issue list" ]]; then
  repo=""
  label=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      --label) label="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$repo:$label" == "owner/alpha:status:done" ]]; then
    printf '%s\\n' '1'
  fi
  exit 0
fi
if [[ "$1 $2" == "pr list" ]]; then
  repo=""
  label=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      --label) label="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$repo:$label" == "owner/alpha:status:closed" ]]; then
    printf '%s\\n' '2'
  fi
  exit 0
fi
if [[ "$1 $2" == "issue edit" || "$1 $2" == "pr edit" ]]; then
  repo=""
  add=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="$2"; shift 2 ;;
      --add-label) add="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$add" == dispatch:* ]] && ! grep -Fxq "$(printf '%s\\t%s' "$repo" "$add")" "${FAKE_LABEL_STATE}"; then
    printf 'missing replacement label: %s:%s\\n' "$repo" "$add" >&2
    exit 65
  fi
  exit 0
fi
if [[ "$1 $2" == "label delete" ]]; then
  exit 0
fi
printf 'unexpected gh call: %s\\n' "$*" >&2
exit 64
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    return gh, log


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    gh, log = _fake_gh(tmp_path)
    env = {
        **os.environ,
        "GH_BIN": str(gh),
        "FAKE_GH_LOG": str(log),
        "FAKE_LABEL_STATE": str(tmp_path / "labels.state"),
    }
    return subprocess.run(
        ["bash", str(SCRIPT), "--owner", "owner", *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_dry_run_is_default_and_does_not_edit_or_delete(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "DRY-RUN" in result.stdout
    assert "issue edit" in result.stdout
    assert "label delete" in result.stdout

    calls = (tmp_path / "gh.calls").read_text(encoding="utf-8")
    assert "issue edit" not in calls
    assert "label delete" not in calls


def test_apply_relabels_issues_and_prs_across_non_archived_repos(tmp_path: Path) -> None:
    result = _run(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr

    calls = (tmp_path / "gh.calls").read_text(encoding="utf-8")
    assert (
        "issue edit 1 --repo owner/alpha --remove-label status:done "
        "--add-label dispatch:done"
    ) in calls
    assert (
        "pr edit 2 --repo owner/alpha --remove-label status:closed "
        "--add-label dispatch:done"
    ) in calls
    assert "label create dispatch:done --repo owner/alpha" in calls


def test_apply_deletes_retired_labels_only_after_issue_and_pr_counts_are_zero(tmp_path: Path) -> None:
    result = _run(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr

    calls = (tmp_path / "gh.calls").read_text(encoding="utf-8")
    assert "label delete status:done --repo owner/alpha --yes" not in calls
    assert "label delete status:closed --repo owner/alpha --yes" not in calls
    assert "label delete status:implemented --repo owner/alpha --yes" in calls


def test_missing_repo_labels_are_skipped_without_issue_or_pr_probe(tmp_path: Path) -> None:
    result = _run(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr

    calls = (tmp_path / "gh.calls").read_text(encoding="utf-8")
    assert "issue list --repo owner/beta" not in calls
    assert "pr list --repo owner/beta" not in calls
    assert "label delete status:implemented --repo owner/beta --yes" not in calls


def test_apply_fails_closed_on_github_api_errors_without_deleting_labels(tmp_path: Path) -> None:
    gh = tmp_path / "gh"
    log = tmp_path / "gh.calls"
    gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "${FAKE_GH_LOG}"
if [[ "$1 $2" == "repo list" ]]; then
  printf '%s\\n' 'owner/alpha'
  exit 0
fi
if [[ "$1 $2" == "label list" ]]; then
  printf '%s\\n' 'status:done'
  exit 0
fi
if [[ "$1 $2" == "label create" ]]; then
  exit 0
fi
if [[ "$1 $2" == "issue list" ]]; then
  printf '%s\\n' 'HTTP 502: bad gateway' >&2
  exit 1
fi
if [[ "$1 $2" == "pr list" ]]; then
  exit 0
fi
if [[ "$1 $2" == "label delete" ]]; then
  exit 0
fi
exit 0
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env = {**os.environ, "GH_BIN": str(gh), "FAKE_GH_LOG": str(log)}

    result = subprocess.run(
        ["bash", str(SCRIPT), "--owner", "owner", "--apply"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode != 0
    assert "HTTP 502: bad gateway" in result.stderr
    calls = log.read_text(encoding="utf-8")
    assert "label delete" not in calls


def test_apply_replaces_less_advanced_dispatch_label_with_status_target(tmp_path: Path) -> None:
    gh = tmp_path / "gh"
    log = tmp_path / "gh.calls"
    gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "${FAKE_GH_LOG}"
if [[ "$1 $2" == "repo list" ]]; then
  printf '%s\\n' 'owner/alpha'
  exit 0
fi
if [[ "$1 $2" == "label list" ]]; then
  printf '%s\\n' 'status:done'
  printf '%s\\n' 'dispatch:ready'
  printf '%s\\n' 'dispatch:done'
  exit 0
fi
if [[ "$1 $2" == "issue list" ]]; then
  label=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --label) label="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$label" == "status:done" ]]; then
    printf '%s\\t%s\\n' '1' 'dispatch:ready'
  fi
  exit 0
fi
if [[ "$1 $2" == "pr list" ]]; then
  exit 0
fi
if [[ "$1 $2" == "issue edit" || "$1 $2" == "label delete" ]]; then
  exit 0
fi
exit 0
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env = {**os.environ, "GH_BIN": str(gh), "FAKE_GH_LOG": str(log)}

    result = subprocess.run(
        ["bash", str(SCRIPT), "--owner", "owner", "--apply"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    calls = log.read_text(encoding="utf-8")
    assert (
        "issue edit 1 --repo owner/alpha --remove-label status:done "
        "--remove-label dispatch:ready --add-label dispatch:done"
    ) in calls


def test_apply_keeps_more_advanced_dispatch_label_when_status_is_less_advanced(tmp_path: Path) -> None:
    gh = tmp_path / "gh"
    log = tmp_path / "gh.calls"
    gh.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "${FAKE_GH_LOG}"
if [[ "$1 $2" == "repo list" ]]; then
  printf '%s\\n' 'owner/alpha'
  exit 0
fi
if [[ "$1 $2" == "label list" ]]; then
  printf '%s\\n' 'status:pending'
  printf '%s\\n' 'dispatch:ready'
  printf '%s\\n' 'dispatch:done'
  exit 0
fi
if [[ "$1 $2" == "issue list" ]]; then
  label=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --label) label="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  if [[ "$label" == "status:pending" ]]; then
    printf '%s\\t%s\\n' '1' 'dispatch:done'
  fi
  exit 0
fi
if [[ "$1 $2" == "pr list" ]]; then
  exit 0
fi
if [[ "$1 $2" == "issue edit" || "$1 $2" == "label delete" ]]; then
  exit 0
fi
exit 0
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    env = {**os.environ, "GH_BIN": str(gh), "FAKE_GH_LOG": str(log)}

    result = subprocess.run(
        ["bash", str(SCRIPT), "--owner", "owner", "--apply"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    calls = log.read_text(encoding="utf-8")
    assert "issue edit 1 --repo owner/alpha --remove-label status:pending\n" in calls
    assert "--add-label dispatch:ready" not in calls
    assert "--remove-label dispatch:done" not in calls
