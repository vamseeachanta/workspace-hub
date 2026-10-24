"""Boundary tests for the registered ecosystem-sync exemption (issue #3985).

Expected paths come from the Direct-main exemptions entry in
.claude/rules/merge-authorization.md. Rejection status comes from the script's
exit-6 contract. These are literal membership examples, not generated answers.
Only function definitions and constants are loaded; the scheduled entry point
is never executed. Git responses below are synthetic and cannot publish data.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".claude/cron/ecosystem-sync.sh"
# Source: ecosystem-sync.sh, guard_staged/guard_outgoing rejection contract.
REJECTED = 6


@pytest.fixture
def guard(tmp_path):
    text = SCRIPT.read_text(encoding="utf-8")
    # Load the actual helpers without lock, pull, sync, commit or push actions.
    definitions = text.split('STATE_FILE=', 1)[1].split('# Parse args', 1)[0]
    definitions = 'STATE_FILE=' + definitions
    assert "guard_staged() {" in definitions
    assert "guard_outgoing() {" in definitions

    def run(body, *, data=b"", **variables):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_")}
        env.update(TMPDIR=str(tmp_path), LOG=str(tmp_path / "guard.log"))
        env.update(variables)
        return subprocess.run(
            ["bash", "-c", "set -euo pipefail\n" + definitions + "\n" + body],
            cwd=tmp_path, env=env, input=data, capture_output=True, check=False,
            # Local test budget only; no operational acceptance limit.
            timeout=10,
        )

    return run


@pytest.mark.parametrize("path,allowed", [
    (".claude/state/ecosystem-sync/last-sync.yaml", True),
    ("docs/sync-reports/digest.md", True),
    ("docs/sync-reports/nested/digest.md", True),
    ("docs/sync-reports/space and\nnewline.md", True),
    ("docs/sync-reports/-option.md", True),
    (".claude/state/ecosystem-sync/last-sync.yaml.bak", False),
    (".claude/state/ecosystem-sync/extra.yaml", False),
    ("docs/sync-reports", False),
    ("docs/sync-reports-old/digest.md", False),
    ("README.md", False),
    ("outside\nfile.md", False),
])
def test_path_membership_uses_exact_state_and_report_subtree(guard, path, allowed):
    """Hand check: exact state equality OR report-directory prefix with slash.

    For example, reports-old is outside because the next character is a hyphen,
    whereas nested/digest.md is inside because the slash belongs to the prefix.
    NUL terminates a path; newline is part of the path, not another record.
    """
    record = path.encode() + b"\0"
    result = guard("outside_allowlist_z", data=record)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (b"" if allowed else record)


def test_filter_preserves_foreign_record_order_and_nul_delimiters(guard):
    """Hand check: discard the report, retain the two foreign paths in order."""
    result = guard(
        "outside_allowlist_z",
        data=b"first\0docs/sync-reports/ok.md\0second\npart\0",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"first\0second\npart\0"


@pytest.mark.parametrize("path,git_rc,expected", [
    ("docs/sync-reports/digest.md", "0", 0),
    ("README.md", "0", REJECTED),
    ("docs/sync-reports/digest.md", "1", REJECTED),
    ("README.md", "1", REJECTED),
])
def test_staged_guard_rejects_foreign_paths_and_partial_git_failure(
    guard, path, git_rc, expected,
):
    """A path match cannot override a failed Git query (independent truth table)."""
    result = guard(
        '''git() {
          [[ "$*" == "diff --cached --name-only -z --no-renames" ]] || return 99
          printf '%s\\0' "$CASE_PATH"
          return "$CASE_GIT_RC"
        }
        guard_staged
        printf reached''',
        CASE_PATH=path, CASE_GIT_RC=git_rc,
    )
    assert result.returncode == expected, result.stderr
    assert result.stdout == (b"reached" if expected == 0 else b"")


@pytest.mark.parametrize("fault,expected", [
    ("none", 0),
    ("missing-ref", REJECTED),
    ("rev-list", REJECTED),
    ("merge-list", REJECTED),
    ("merge-present", REJECTED),
    ("range-query", REJECTED),
    ("commit-query", REJECTED),
    ("foreign-range", REJECTED),
    ("foreign-commit", REJECTED),
])
def test_outgoing_guard_fails_closed_at_each_git_query(guard, fault, expected):
    """Hand check: every query must succeed, no merges, all paths allowed.

    The foreign-commit case models an add then revert: the net range is allowed
    but an individual commit touched README.md, so range-only checking is wrong.
    The fake Git accepts only the expected captured-OID queries; mutable branch
    queries and removal of no-renames/NUL flags are rejected as unexpected.
    """
    result = guard(
        '''git() {
          case "$*" in
            "rev-parse --verify --quiet refs/remotes/origin/main")
              [[ "$CASE_FAULT" != "missing-ref" ]] ;;
            "rev-list refs/remotes/origin/main..captured")
              [[ "$CASE_FAULT" != "rev-list" ]] || return 1
              printf 'commit-a\\ncommit-b\\n' ;;
            "rev-list --merges refs/remotes/origin/main..captured")
              [[ "$CASE_FAULT" != "merge-list" ]] || return 1
              if [[ "$CASE_FAULT" == "merge-present" ]]; then printf 'merge-c\\n'; fi ;;
            "diff --name-only -z --no-renames refs/remotes/origin/main...captured")
              printf 'docs/sync-reports/digest.md\\0'
              [[ "$CASE_FAULT" != "range-query" ]] || return 1
              if [[ "$CASE_FAULT" == "foreign-range" ]]; then printf 'README.md\\0'; fi ;;
            "diff-tree --no-commit-id --name-only -r -z --root --no-renames commit-a"|\
            "diff-tree --no-commit-id --name-only -r -z --root --no-renames commit-b")
              printf 'docs/sync-reports/digest.md\\0'
              [[ "$CASE_FAULT" != "commit-query" ]] || return 1
              if [[ "$CASE_FAULT" == "foreign-commit" && "${*: -1}" == "commit-b" ]]; then
                printf 'README.md\\0'
              fi ;;
            *) return 99 ;;
          esac
        }
        guard_outgoing captured
        printf reached''',
        CASE_FAULT=fault,
    )
    assert result.returncode == expected, result.stderr
    assert result.stdout == (b"reached" if expected == 0 else b"")
