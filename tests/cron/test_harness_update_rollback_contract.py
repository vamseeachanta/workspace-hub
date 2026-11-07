"""Isolated rollback contracts for scripts/cron/harness-update.sh.

Basis: issue #1680 specifies exact previous-version restoration and a mocked
major bump. Its npm example supplies version 2.1.88. The literal comparison
examples below are independently calculated: 3 - 2 = 1 changes the major;
2 - 2 = 0 preserves it, even when the minor increases from 1 to 2.
Shell status expectations follow Bash's convention: zero succeeds and one fails.
No updater initialization or main loop is sourced or executed.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "cron" / "harness-update.sh"
)
PACKAGE = "rollback-contract-tool"
PREVIOUS = "2.1.88"
# Deliberately distinct from the rollback function's failure status of one.
# This synthetic command failure is arbitrary; only its nonzero value matters.
INSTALL_FAILURE = "23"


@pytest.fixture
def shell(tmp_path):
    """Load only named definitions; all package/notification calls are doubles."""
    bash = shutil.which("bash")
    assert bash is not None
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    # These text filters are the only real external commands reachable by PATH.
    for name in ("cut", "grep", "tee"):
        executable = shutil.which(name)
        assert executable is not None
        (tool_dir / name).symlink_to(executable)

    npm = tool_dir / "npm"
    npm.write_text(
        f"#!{bash}\n"
        r'''printf '%s\0' "$@" >> "$CALLS"
printf '\0' >> "$CALLS"
case "$*" in
  "install -g $PACKAGE@$PREVIOUS")
    printf '%s\n' 'simulated install output'
    if [[ "$INSTALL_STATUS" != 0 ]]; then
      printf '%s\n' 'simulated package failure' >&2
    fi
    exit "$INSTALL_STATUS"
    ;;
  "list -g $PACKAGE --depth=0") printf '%s\n' "$PACKAGE@$RESTORED" ;;
  "view $PACKAGE version") printf '%s\n' "$LATEST" ;;
  *) printf '%s\n' "unexpected npm invocation: $*" >> "$UNEXPECTED"; exit 1 ;;
esac
'''
    )
    npm.chmod(0o700)
    # Notifications must never escape the disposable tool directory.
    for name in ("notify", "notify-send", "curl"):
        double = tool_dir / name
        double.write_text(
            f"#!{bash}\n"
            'printf "%s\\n" "unexpected notification" >> "$UNEXPECTED"\n'
            "exit 1\n"
        )
        double.chmod(0o700)

    source = SCRIPT.read_text()
    definitions = []
    for name in ("is_major_bump", "rollback_npm", "update_npm_tool"):
        # Fail closed if a definition disappears or its top-level layout changes.
        matches = re.findall(rf"(?ms)^{name}\(\) \{{\n.*?^\}}$", source)
        assert len(matches) == 1, f"expected one complete {name} definition"
        definitions.append(matches[0])

    calls = tmp_path / "calls"
    log = tmp_path / "rollback.log"
    unexpected = tmp_path / "unexpected"
    records = tmp_path / "records"
    transactions = tmp_path / "transactions"
    # Do not inherit shell startup files, exported functions, provider paths or
    # user configuration. The fixture's environment contains only test inputs.
    env = {
        "PATH": str(tool_dir),
        "HOME": str(tmp_path),
        "TMPDIR": str(tmp_path),
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "PACKAGE": PACKAGE,
        "PREVIOUS": PREVIOUS,
        "RESTORED": PREVIOUS,
        "LATEST": "3.0.0",
        "INSTALL_STATUS": "0",
        "LOG_FILE": str(log),
        "CALLS": str(calls),
        "UNEXPECTED": str(unexpected),
        "RECORDS": str(records),
        "TRANSACTIONS": str(transactions),
        "DRY_RUN": "false",
    }
    preamble = r'''
set -uo pipefail
log() { printf '%s\n' "$*" >> "$LOG_FILE"; }
record() { printf '%s\n' "$*" >> "$RECORDS"; }
write_transaction() { printf '%s\n' "$*" >> "$TRANSACTIONS"; }
command_not_found_handle() {
  printf '%s\n' "unexpected command: $*" >> "$UNEXPECTED"
  return 1
}
'''

    def invoke(command, **overrides):
        program = "\n".join([preamble, *definitions, command])
        result = subprocess.run(
            [bash, "--noprofile", "--norc", "-c", program],
            cwd=tmp_path,
            env={**env, **overrides},
            capture_output=True,
            text=True,
            # A bounded wait protects the test from a hung command double.
            timeout=10,
        )
        assert not unexpected.exists(), (
            unexpected.read_text() if unexpected.exists() else ""
        )
        return result

    class Harness:
        run = staticmethod(invoke)

        @staticmethod
        def arguments():
            if not calls.exists():
                return []
            return [
                invocation.decode().split("\0")
                for invocation in calls.read_bytes().split(b"\0\0")
                if invocation
            ]

        @staticmethod
        def logged():
            return log.read_text() if log.exists() else ""

        @staticmethod
        def recorded():
            return records.read_text(), transactions.read_text()

    return Harness()


def test_major_bump_is_skipped(shell):
    result = shell.run('is_major_bump "2.1.88" "3.0.0"')
    assert result.returncode == 0, result.stderr
    assert shell.arguments() == []


def test_minor_update_is_not_major(shell):
    result = shell.run('is_major_bump "2.1.88" "2.2.0"')
    assert result.returncode == 1, result.stderr
    assert shell.arguments() == []


def test_major_bump_records_skip_without_install(shell):
    result = shell.run('update_npm_tool "test-tool" "$PACKAGE" forbidden_health_check')
    assert result.returncode == 0, result.stderr
    assert shell.arguments() == [
        ["list", "-g", PACKAGE, "--depth=0"],
        ["view", PACKAGE, "version"],
    ]
    record, transaction = shell.recorded()
    assert record == "test-tool 2.1.88 3.0.0 major-bump-skipped\n"
    assert transaction == (
        "test-tool 2.1.88 3.0.0 2.1.88 major-bump-skipped false healthy\n"
    )
    assert "major bump 2.1.88 -> 3.0.0 — skipping" in shell.logged()


def test_rollback_restores_exact_previous_version(shell):
    result = shell.run('rollback_npm "$PACKAGE" "$PREVIOUS"')
    assert result.returncode == 0, result.stderr
    assert shell.arguments() == [
        ["install", "-g", f"{PACKAGE}@2.1.88"],
        ["list", "-g", PACKAGE, "--depth=0"],
    ]
    assert f"{PACKAGE} restored to 2.1.88 — verified" in shell.logged()
    assert "rollback FAILED" not in shell.logged()


def test_rollback_failure_is_recorded(shell):
    result = shell.run(
        'rollback_npm "$PACKAGE" "$PREVIOUS"', INSTALL_STATUS=INSTALL_FAILURE
    )
    assert result.returncode == 1, result.stderr
    assert shell.arguments() == [["install", "-g", f"{PACKAGE}@2.1.88"]]
    assert "simulated package failure" in shell.logged()
    assert f"CRITICAL {PACKAGE} rollback FAILED" in shell.logged()
    assert "— verified" not in shell.logged()


def test_rollback_rejects_mismatched_restored_version(shell):
    # Independent mismatch: 2.1.89 differs from the recorded 2.1.88 by one patch.
    result = shell.run('rollback_npm "$PACKAGE" "$PREVIOUS"', RESTORED="2.1.89")
    assert result.returncode == 1, result.stderr
    assert shell.arguments() == [
        ["install", "-g", f"{PACKAGE}@2.1.88"],
        ["list", "-g", PACKAGE, "--depth=0"],
    ]
    assert f"CRITICAL {PACKAGE} rollback FAILED" in shell.logged()
    assert "— verified" not in shell.logged()


@pytest.mark.parametrize("previous", ["", "not-installed", "unknown"])
def test_rollback_without_previous_version_never_installs(shell, previous):
    result = shell.run('rollback_npm "$PACKAGE" "$PREVIOUS"', PREVIOUS=previous)
    assert result.returncode == 1, result.stderr
    assert shell.arguments() == []
    assert "no previous version recorded" in shell.logged()
