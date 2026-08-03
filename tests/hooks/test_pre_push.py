"""Tests for scripts/hooks/pre-push.sh — TDD written before implementation.

Run with:
    uv run --no-project python -m pytest tests/hooks/test_pre_push.py -v
"""

import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / "scripts" / "hooks" / "pre-push.sh"


def _tier1_repos() -> list[str]:
    """Read the tier-1 repo list from the #3023 single source of truth.

    Previously hardcoded here, which drifted: this list still carried
    ``OGManufacturing`` after it left ``config/tier1-python-repos.txt``, so the
    test failed against a correct hook. That file's own header says "do NOT
    hardcode the repo list anywhere else" -- a test is not an exception.
    """
    src = REPO_ROOT / "config" / "tier1-python-repos.txt"
    return [
        line.strip()
        for line in src.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


TIER1_REPOS = _tier1_repos()


def _run_hook(
    stdin_lines: list[str],
    env_extra: dict | None = None,
    extra_args: list[str] | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """Run pre-push.sh with given stdin and environment overrides."""
    env = os.environ.copy()
    # Ensure we don't accidentally invoke real check-all.sh / run-all-tests.sh
    env["PRE_PUSH_DRY_RUN"] = "1"
    # These tests exercise repo SCOPE DETECTION, not the enforcement gates. Once
    # the gates were re-wired above the terminal exit (#3781) they began running
    # here for real, and the stage-prompt drift gate failed on unrelated repo
    # state — a scope test reporting a drift failure. Disable enforcement so a
    # gate's verdict cannot masquerade as a scoping bug.
    #
    # Deliberately NOT applied to the reachability/ordering tests in
    # test_install_hooks_extension_point.py: those assert the gates are wired
    # and must not be able to pass with enforcement switched off.
    env.setdefault("DISABLE_ENFORCEMENT", "1")
    if env_extra:
        env.update(env_extra)

    cmd = ["bash", str(HOOK_SCRIPT)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd,
        input="\n".join(stdin_lines) + "\n",
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
        cwd=str(REPO_ROOT),
    )
    return result


ZERO_OID = "0" * 40
FAKE_OID_LOCAL = "a" * 40
FAKE_OID_REMOTE = "b" * 40


# ---------------------------------------------------------------------------
# Test A — changed-only: only runs affected repo(s)
# ---------------------------------------------------------------------------


class TestChangedOnly:
    """Hook detects which tier-1 repos changed and only runs those."""

    def test_changed_repo_subset_is_run(self, tmp_path):
        """When a push touches only assetutilities, only that repo is checked."""
        # We verify by injecting a fake check-all.sh that records calls
        fake_bin = tmp_path / "fake_bin"
        fake_bin.mkdir()

        calls_log = tmp_path / "calls.log"

        fake_check_all = fake_bin / "check-all.sh"
        fake_check_all.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                echo "check-all $@" >> "{calls_log}"
            """)
        )
        fake_check_all.chmod(0o755)

        fake_run_all = fake_bin / "run-all-tests.sh"
        fake_run_all.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                echo "run-all-tests $@" >> "{calls_log}"
            """)
        )
        fake_run_all.chmod(0o755)

        env = {
            "PRE_PUSH_DRY_RUN": "0",
            "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_check_all),
            "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_run_all),
            # Override git diff to return only assetutilities path
            "PRE_PUSH_CHANGED_FILES": "assetutilities/src/foo.py",
        }

        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env)

        assert result.returncode == 0, result.stderr
        log_content = calls_log.read_text() if calls_log.exists() else ""
        # Only assetutilities should appear in the calls log
        assert "assetutilities" in log_content
        for other in ["digitalmodel", "worldenergydata", "assethold", "OGManufacturing"]:
            assert other not in log_content


# ---------------------------------------------------------------------------
# Test B — --all mode: runs all 5 repos
# ---------------------------------------------------------------------------


class TestAllMode:
    """The --all flag forces all 5 repos to be checked."""

    def test_all_flag_runs_every_repo(self, tmp_path):
        calls_log = tmp_path / "calls.log"
        fake_bin = tmp_path / "fake_bin"
        fake_bin.mkdir()

        for script in ("check-all.sh", "run-all-tests.sh"):
            s = fake_bin / script
            s.write_text(
                textwrap.dedent(f"""\
                    #!/usr/bin/env bash
                    echo "{script} $@" >> "{calls_log}"
                """)
            )
            s.chmod(0o755)

        env = {
            "PRE_PUSH_DRY_RUN": "0",
            "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_bin / "check-all.sh"),
            "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_bin / "run-all-tests.sh"),
            "PRE_PUSH_CHANGED_FILES": "assetutilities/src/foo.py",
        }

        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env, extra_args=["--all"])

        assert result.returncode == 0, result.stderr
        log_content = calls_log.read_text() if calls_log.exists() else ""
        for repo in TIER1_REPOS:
            assert repo in log_content, f"Expected {repo} in calls but got:\n{log_content}"


# ---------------------------------------------------------------------------
# Test C — failure blocks push (exit code 1)
# ---------------------------------------------------------------------------


class TestFailureBlocks:
    """If any repo check fails, the push must be blocked (exit 1)."""

    def test_failing_check_all_blocks_push(self, tmp_path):
        calls_log = tmp_path / "calls.log"
        fake_bin = tmp_path / "fake_bin"
        fake_bin.mkdir()

        # check-all.sh exits 1 for assetutilities, 0 for others
        fake_check_all = fake_bin / "check-all.sh"
        fake_check_all.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                echo "check-all $@" >> "{calls_log}"
                if echo "$@" | grep -q assetutilities; then
                    exit 1
                fi
                exit 0
            """)
        )
        fake_check_all.chmod(0o755)

        fake_run_all = fake_bin / "run-all-tests.sh"
        fake_run_all.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                echo "run-all-tests $@" >> "{calls_log}"
                exit 0
            """)
        )
        fake_run_all.chmod(0o755)

        env = {
            "PRE_PUSH_DRY_RUN": "0",
            "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_check_all),
            "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_run_all),
            "PRE_PUSH_CHANGED_FILES": "assetutilities/src/foo.py",
        }

        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env)

        assert result.returncode == 1, (
            f"Expected exit 1 to block push, got {result.returncode}\n{result.stderr}"
        )

    def test_failing_run_tests_blocks_push(self, tmp_path):
        fake_bin = tmp_path / "fake_bin"
        fake_bin.mkdir()

        fake_check_all = fake_bin / "check-all.sh"
        fake_check_all.write_text("#!/usr/bin/env bash\nexit 0\n")
        fake_check_all.chmod(0o755)

        fake_run_all = fake_bin / "run-all-tests.sh"
        fake_run_all.write_text("#!/usr/bin/env bash\nexit 1\n")
        fake_run_all.chmod(0o755)

        env = {
            "PRE_PUSH_DRY_RUN": "0",
            "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_check_all),
            "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_run_all),
            "PRE_PUSH_CHANGED_FILES": "assetutilities/src/foo.py",
        }

        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env)
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# Test D — GIT_PRE_PUSH_SKIP=1 logs JSONL and exits 0
# ---------------------------------------------------------------------------


class TestSkipBypass:
    """GIT_PRE_PUSH_SKIP=1 must log a JSONL record and exit 0 (soft bypass)."""

    def test_skip_exits_zero(self, tmp_path):
        bypass_log = tmp_path / "bypass.jsonl"
        env = {
            "GIT_PRE_PUSH_SKIP": "1",
            "PRE_PUSH_BYPASS_LOG": str(bypass_log),
        }
        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env)
        assert result.returncode == 0, result.stderr

    def test_skip_writes_jsonl_record(self, tmp_path):
        bypass_log = tmp_path / "bypass.jsonl"
        env = {
            "GIT_PRE_PUSH_SKIP": "1",
            "PRE_PUSH_BYPASS_LOG": str(bypass_log),
        }
        stdin = [f"refs/heads/feature {FAKE_OID_LOCAL} refs/heads/feature {FAKE_OID_REMOTE}"]
        _run_hook(stdin, env_extra=env)

        assert bypass_log.exists(), "Bypass log file should be created"
        lines = [l for l in bypass_log.read_text().splitlines() if l.strip()]
        assert len(lines) >= 1, "Expected at least one JSONL line"
        record = json.loads(lines[0])

        required_keys = {
            "timestamp",
            "local_ref",
            "local_oid",
            "remote_ref",
            "remote_oid",
            "operator",
            "exit_code",
        }
        missing = required_keys - set(record.keys())
        assert not missing, f"Missing keys in bypass log: {missing}"
        assert record["operator"] == "GIT_PRE_PUSH_SKIP"
        assert record["exit_code"] == 0
        assert record["local_ref"] == "refs/heads/feature"

    def test_skip_does_not_run_checks(self, tmp_path):
        calls_log = tmp_path / "calls.log"
        fake_bin = tmp_path / "fake_bin"
        fake_bin.mkdir()
        bypass_log = tmp_path / "bypass.jsonl"

        for script in ("check-all.sh", "run-all-tests.sh"):
            s = fake_bin / script
            s.write_text(
                textwrap.dedent(f"""\
                    #!/usr/bin/env bash
                    echo "{script} $@" >> "{calls_log}"
                """)
            )
            s.chmod(0o755)

        env = {
            "GIT_PRE_PUSH_SKIP": "1",
            "PRE_PUSH_BYPASS_LOG": str(bypass_log),
            "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_bin / "check-all.sh"),
            "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_bin / "run-all-tests.sh"),
        }
        stdin = [f"refs/heads/main {FAKE_OID_LOCAL} refs/heads/main {FAKE_OID_REMOTE}"]
        _run_hook(stdin, env_extra=env)

        log_content = calls_log.read_text() if calls_log.exists() else ""
        assert log_content == "", f"No checks should run on skip, but got:\n{log_content}"


# ---------------------------------------------------------------------------
# Test E — new-branch push (remote_oid zeros) → all-repos mode
# ---------------------------------------------------------------------------


def _fake_check_scripts(tmp_path):
    """Build stub check-all/run-all-tests that log their invocations."""
    calls_log = tmp_path / "calls.log"
    fake_bin = tmp_path / "fake_bin"
    fake_bin.mkdir()
    for script in ("check-all.sh", "run-all-tests.sh"):
        s = fake_bin / script
        s.write_text(
            textwrap.dedent(f"""\
                #!/usr/bin/env bash
                echo "{script} $@" >> "{calls_log}"
            """)
        )
        s.chmod(0o755)
    env = {
        "PRE_PUSH_DRY_RUN": "0",
        "PRE_PUSH_CHECK_ALL_SCRIPT": str(fake_bin / "check-all.sh"),
        "PRE_PUSH_RUN_TESTS_SCRIPT": str(fake_bin / "run-all-tests.sh"),
    }
    return calls_log, env


class TestNewBranchFallback:
    """A new branch must be SCOPED by merge-base, not escalated to every repo.

    This class previously asserted the opposite -- ``test_new_branch_runs_all_repos``
    pinned the escalation as correct behaviour. It is the defect in #3780: because
    every feature branch is a new branch on its first push, the narrowest possible
    change got the widest possible gate, and since the gate chains to a suite that
    is red by baseline, the push could never pass. Measured: three stacked pushes
    hung 44+ minutes producing zero output.

    Scope is not unknowable on a new branch. A branch cut from main has a
    merge-base. Escalation is correct only for genuinely disjoint history.
    """

    def test_new_branch_scopes_by_merge_base(self, tmp_path):
        """A new branch touching one repo must not run the others."""
        calls_log, env = _fake_check_scripts(tmp_path)
        env["PRE_PUSH_CHANGED_FILES"] = "digitalmodel/src/foo.py"

        stdin = [f"refs/heads/new-feature {FAKE_OID_LOCAL} refs/heads/new-feature {ZERO_OID}"]
        result = _run_hook(stdin, env_extra=env)

        assert result.returncode == 0, result.stderr
        log_content = calls_log.read_text() if calls_log.exists() else ""
        assert "digitalmodel" in log_content, (
            f"the touched repo must still be checked, got:\n{log_content}"
        )
        for repo in TIER1_REPOS:
            if repo == "digitalmodel":
                continue
            assert repo not in log_content, (
                f"{repo} was untouched and must not be checked, got:\n{log_content}"
            )

    def test_new_branch_docs_only_skips_repo_gate(self, tmp_path):
        """A new branch touching no tier-1 path runs no suite at all.

        This is the case that hung for 44 minutes: a one-file change under
        docs/ops/ triggering every tier-1 repo's full test suite.
        """
        calls_log, env = _fake_check_scripts(tmp_path)
        env["PRE_PUSH_CHANGED_FILES"] = "docs/ops/machine-inventory.md"

        stdin = [f"refs/heads/docs-branch {FAKE_OID_LOCAL} refs/heads/docs-branch {ZERO_OID}"]
        result = _run_hook(stdin, env_extra=env)

        assert result.returncode == 0, result.stderr
        log_content = calls_log.read_text() if calls_log.exists() else ""
        assert log_content == "", f"no repo checks expected, got:\n{log_content}"

    def test_merge_base_failure_does_not_open_the_gate(self, tmp_path):
        """If scope cannot be determined, ESCALATE -- never check nothing.

        The dangerous failure direction is not "runs too much", it is "runs
        nothing and exits 0", which is silent and ships unchecked code. The
        original defect's own fix was nearly written this way: setting a
        merge-base variable the diff never consumed would leave CHANGED_FILES
        empty and pass every push unexamined.
        """
        calls_log, env = _fake_check_scripts(tmp_path)
        # A local OID that exists in no repo: merge-base against it cannot resolve.
        unknown_oid = "d" * 40
        stdin = [f"refs/heads/orphan {unknown_oid} refs/heads/orphan {ZERO_OID}"]
        result = _run_hook(stdin, env_extra=env)

        log_content = calls_log.read_text() if calls_log.exists() else ""
        assert log_content != "", (
            "unresolvable scope must escalate to all tier-1 repos, but NO checks "
            "ran -- the gate silently opened"
        )
        for repo in TIER1_REPOS:
            assert repo in log_content, (
                f"escalation must cover {repo}, got:\n{log_content}"
            )

    def test_delete_branch_skipped(self):
        """Deleting a branch (local_oid = zeros) should exit 0 without running checks."""
        env = {"PRE_PUSH_DRY_RUN": "0"}
        # local_oid is all zeros → delete push
        stdin = [f"refs/heads/old-feature {ZERO_OID} refs/heads/old-feature {FAKE_OID_REMOTE}"]
        result = _run_hook(stdin, env_extra=env)
        assert result.returncode == 0, f"Delete branch push should exit 0, got {result.returncode}"


# ---------------------------------------------------------------------------
# Test F — help / smoke test
# ---------------------------------------------------------------------------


class TestSmokeHelp:
    """Syntax check: --help should not error."""

    def test_help_exits_zero(self):
        result = subprocess.run(
            ["bash", str(HOOK_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        # --help should exit 0 and print usage
        assert result.returncode == 0, result.stderr
        assert "usage" in result.stdout.lower() or "pre-push" in result.stdout.lower()
