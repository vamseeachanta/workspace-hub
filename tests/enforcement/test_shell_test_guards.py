"""Tests for scripts/lib/shell-test-guards.sh (#3876).

The library gives shell harnesses runtime guards for the false-green class in
#3876: a selector skips a helper definition, the helper's later call fails
inside a command substitution, and two empty snapshots compare equal.

Every fixture is a neutral, synthetic harness under tmp_path. Nothing depends
on host paths, fleet state or real adapters.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "scripts" / "lib" / "shell-test-guards.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _bash(tmp_path: Path, body: str, env: dict | None = None):
    script = tmp_path / "harness.sh"
    lib = LIB.as_posix()
    script.write_text(
        "set -uo pipefail\n"
        f"source '{lib}' || exit 99\n" + textwrap.dedent(body).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    return subprocess.run(
        [BASH, script.name],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        env=env,
    )


# --- the original false green, reproduced neutrally -------------------------

ORIGINAL_SHAPE = """
PASS=0; FAIL=0
pass() { echo "PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAIL: $1"; FAIL=$((FAIL + 1)); }
if [[ "${TARGETED:-0}" != 1 ]]; then
  snapshot() { printf 'id-%s\\n' "$1"; }
fi
before="$(snapshot item 2>/dev/null)"
after="$(snapshot item 2>/dev/null)"
{ASSERT}
echo "passed=$PASS failed=$FAIL"
[[ "$FAIL" == 0 ]]
"""


def test_unguarded_targeted_run_is_a_false_green(tmp_path):
    """Documents the defect: no guard, targeted mode, harness exits 0."""
    body = ORIGINAL_SHAPE.replace(
        "{ASSERT}", '[[ "$after" == "$before" ]] && pass same || fail same'
    )
    result = _bash(tmp_path, body, env={**os.environ, "TARGETED": "1"})
    assert result.returncode == 0
    assert "PASS: same" in result.stdout


def test_guarded_targeted_run_fails(tmp_path):
    body = ORIGINAL_SHAPE.replace(
        "{ASSERT}",
        'assert_snapshot_unchanged same "$after" "$before" && pass same || fail same',
    )
    result = _bash(tmp_path, body, env={**os.environ, "TARGETED": "1"})
    assert result.returncode != 0
    assert "FAIL: same" in result.stdout
    assert "empty" in result.stderr


def test_guarded_default_run_still_passes(tmp_path):
    body = ORIGINAL_SHAPE.replace(
        "{ASSERT}",
        'assert_snapshot_unchanged same "$after" "$before" && pass same || fail same',
    )
    result = _bash(tmp_path, body, env={**os.environ, "TARGETED": "0"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: same" in result.stdout


# --- require_helpers --------------------------------------------------------


def test_require_helpers_fails_on_undefined(tmp_path):
    result = _bash(
        tmp_path,
        """
        present() { :; }
        require_helpers present absent_helper && echo OK || echo REJECTED
        """,
    )
    assert "REJECTED" in result.stdout
    assert "absent_helper" in result.stderr
    assert "present" not in result.stderr.replace("absent_helper", "")


def test_require_helpers_passes_when_all_defined(tmp_path):
    result = _bash(
        tmp_path,
        """
        one() { :; }; two() { :; }
        require_helpers one two && echo OK
        """,
    )
    assert result.stdout.strip() == "OK"
    assert result.stderr == ""


def test_require_helpers_rejects_external_command_of_same_name(tmp_path):
    """`command -v` would accept an executable; a helper must be a function."""
    result = _bash(tmp_path, "require_helpers ls && echo OK || echo REJECTED\n")
    assert "REJECTED" in result.stdout


def test_require_helpers_with_no_names_is_a_usage_error(tmp_path):
    result = _bash(tmp_path, "require_helpers; echo rc=$?\n")
    assert "rc=2" in result.stdout


# --- require_nonempty / assert_snapshot_unchanged ---------------------------


@pytest.mark.parametrize("value", ["", "   ", "\\n\\t"])
def test_require_nonempty_rejects_blank(tmp_path, value):
    result = _bash(
        tmp_path,
        f'require_nonempty rec "$(printf "{value}")" && echo OK || echo REJECTED\n',
    )
    assert "REJECTED" in result.stdout
    assert "rec" in result.stderr


def test_require_nonempty_accepts_record(tmp_path):
    result = _bash(tmp_path, 'require_nonempty rec "abc 123" && echo OK\n')
    assert result.stdout.strip() == "OK"


def test_snapshot_unchanged_rejects_one_side_empty(tmp_path):
    result = _bash(
        tmp_path,
        'assert_snapshot_unchanged s "" "id-1" && echo OK || echo REJECTED\n',
    )
    assert "REJECTED" in result.stdout


def test_snapshot_unchanged_rejects_difference(tmp_path):
    result = _bash(
        tmp_path,
        'assert_snapshot_unchanged s "id-2" "id-1" && echo OK || echo REJECTED\n',
    )
    assert "REJECTED" in result.stdout
    assert "changed" in result.stderr


def test_snapshot_unchanged_accepts_equal_populated(tmp_path):
    result = _bash(tmp_path, 'assert_snapshot_unchanged s "id-1" "id-1" && echo OK\n')
    assert result.stdout.strip() == "OK"


# --- guard_mark / require_executed (survives command substitution) ----------


def test_executed_marker_survives_command_substitution(tmp_path):
    result = _bash(
        tmp_path,
        """
        guard_init || exit 1
        snapshot() { guard_mark snapshot; printf 'id\\n'; }
        out="$(snapshot)"
        require_executed snapshot && echo RAN
        guard_cleanup
        """,
    )
    assert result.stdout.strip() == "RAN", result.stderr


def test_require_executed_fails_when_helper_never_ran(tmp_path):
    result = _bash(
        tmp_path,
        """
        guard_init || exit 1
        snapshot() { guard_mark snapshot; printf 'id\\n'; }
        require_executed snapshot && echo RAN || echo NOT_RUN
        guard_cleanup
        """,
    )
    assert "NOT_RUN" in result.stdout
    assert "snapshot" in result.stderr


def test_guard_mark_without_init_fails_loudly(tmp_path):
    result = _bash(tmp_path, "guard_mark x && echo OK || echo REJECTED\n")
    assert "REJECTED" in result.stdout
    assert "guard_init" in result.stderr


def test_guard_cleanup_removes_marker_dir(tmp_path):
    result = _bash(
        tmp_path,
        """
        guard_init || exit 1
        dir="$GUARD_MARK_DIR"
        guard_cleanup
        [[ -e "$dir" ]] && echo LEFT || echo GONE
        """,
    )
    assert result.stdout.strip() == "GONE"


# --- run_step: each prerequisite's exit code is captured and kept -----------


def test_run_step_propagates_failure_masked_by_later_success(tmp_path):
    """A later successful command must not hide an earlier failed step."""
    result = _bash(
        tmp_path,
        """
        run_step render bash -c 'exit 2'; r1=$?
        run_step verify true; r2=$?
        echo "r1=$r1 r2=$r2 last=$GUARD_LAST_RC"
        """,
    )
    assert "r1=2 r2=0 last=0" in result.stdout
    assert "render" in result.stderr and "rc=2" in result.stderr


def test_run_step_receipt_retains_failures_across_runs(tmp_path):
    receipt = tmp_path / "receipt.log"
    body = f"""
    GUARD_RECEIPT='{receipt.as_posix()}'
    run_step render bash -c 'exit 2'
    run_step render true
    """
    _bash(tmp_path, body)
    _bash(tmp_path, body)
    lines = receipt.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4
    assert sum("rc=2" in line for line in lines) == 2
    assert all("render" in line for line in lines)


def test_run_step_records_failure_under_errexit(tmp_path):
    """Under `set -e` the failed step must still be recorded before exit."""
    receipt = tmp_path / "receipt.log"
    result = _bash(
        tmp_path,
        f"""
        set -e
        GUARD_RECEIPT='{receipt.as_posix()}'
        run_step render bash -c 'exit 3'
        echo UNREACHABLE
        """,
    )
    assert result.returncode == 3
    assert "UNREACHABLE" not in result.stdout
    assert "rc=3" in receipt.read_text(encoding="utf-8")


def test_run_step_fails_when_receipt_cannot_be_written(tmp_path):
    result = _bash(
        tmp_path,
        """
        GUARD_RECEIPT=/nonexistent-dir-3876/receipt.log
        run_step ok true; echo rc=$?
        """,
    )
    assert "rc=3" in result.stdout
    assert "receipt" in result.stderr


def test_require_helpers_rejects_option_like_names(tmp_path):
    result = _bash(tmp_path, "require_helpers -p && echo OK || echo REJECTED\n")
    assert "REJECTED" in result.stdout


def test_guard_mark_without_name_is_a_usage_error(tmp_path):
    result = _bash(tmp_path, "guard_init; guard_mark; echo rc=$?; guard_cleanup\n")
    assert "rc=2" in result.stdout


def test_guard_init_twice_removes_first_dir(tmp_path):
    result = _bash(
        tmp_path,
        """
        guard_init; first="$GUARD_MARK_DIR"
        guard_init; [[ -e "$first" ]] && echo LEFT || echo GONE
        guard_cleanup
        """,
    )
    assert result.stdout.strip() == "GONE"


def test_run_step_with_no_command_is_a_usage_error(tmp_path):
    result = _bash(tmp_path, "run_step label; echo rc=$?\n")
    assert "rc=2" in result.stdout
