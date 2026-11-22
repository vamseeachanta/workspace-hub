"""Offline regressions for shell submitter invocation (issue #3820).

Basis: issue #3820 and the existing cross-review.sh dispatch branches.
Tracked modes come from Git, then clearing octal 111 removes all execute bits:
755 & ~111 = 644. Fixtures preserve the remaining tracked permission bits.
Hand count: five routes times two input shapes = ten success cases per matrix;
five routes times two shapes = ten failure cases, plus two standalone checks.
Policy values are read from the existing dispatch declarations, not copied.
Exit 42 is a synthetic ordinary failure; zero is shell success, one is the
existing dispatch failure contract. Direct Claude errors produce a failure
artifact with exit zero; Codex errors block with exit one (cross-review.sh).
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "scripts/review"
ROUTES = ("claude", "codex", "agy", "limit-substitute", "quota-substitute")
SHAPES = ("file", "commit")
PROMPT = 'Synthetic prompt with spaces, "quotes", $literal and\na second line.'
VERDICT = """### Verdict: APPROVE
### Summary
Synthetic review.
### Issues Found
None.
### Suggestions
None.
### Questions for Author
None.
"""
SUBMITTER = r'''#!/usr/bin/env bash
set -euo pipefail
printf '%s\0' "${0##*/}" "${CLAUDE_MODEL-}" "$@" >> "$CAPTURE"
if [[ "${0##*/}" == submit-to-codex.sh && -n "${QUOTA_EXIT:-}" ]]; then
  exit "$QUOTA_EXIT"
fi
if [[ "${FAIL_SUBMITTER:-}" == "${0##*/}" ]]; then
  echo 'Synthetic submitter failure' >&2
  exit 42
fi
printf '%s\n' "$FIXTURE_VERDICT"
'''


def _git(*args):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", *args], cwd=ROOT, env=env, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _tracked_permissions(relative):
    mode = _git("ls-tree", "HEAD", "--", relative).split()[0]
    return int(mode, 8) & 0o777


@pytest.fixture
def dispatch(tmp_path):
    # The caller supplies --basetemp outside the checkout; no runtime output is
    # written beside production scripts. Copy helpers, never real submitters.
    review = tmp_path / "checkout with spaces" / "scripts/review"
    review.mkdir(parents=True)
    for name in ("cross-review.sh", "validate-review-output.sh"):
        shutil.copyfile(REVIEW / name, review / name)
        (review / name).chmod(_tracked_permissions(f"scripts/review/{name}"))
    lib = review.parent / "lib"
    lib.mkdir()
    shutil.copyfile(ROOT / "scripts/lib/model-registry.sh", lib / "model-registry.sh")
    prompts = review / "prompts"
    prompts.mkdir()
    for kind in ("implementation", "commit"):
        (prompts / f"{kind}-review.md").write_text(PROMPT)
    for name in ("claude", "codex", "agy", "gemini"):
        path = review / f"submit-to-{name}.sh"
        path.write_text(SUBMITTER)
        path.chmod(_tracked_permissions(f"scripts/review/{path.name}") & ~0o111)
        assert path.stat().st_mode & 0o111 == 0

    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "CODEX_", "CLAUDE_", "AGY_"))
           and key not in ("BASH_ENV", "ENV", "CDPATH")}
    # Isolate controls from the invoking environment. The synthetic model
    # value tests forwarding only; no model or provider CLI is launched.
    env.update(
        CAPTURE=str(tmp_path / "calls.bin"),
        FIXTURE_VERDICT=VERDICT,
        FAIL_SUBMITTER="",
        QUOTA_EXIT="",
        CODEX_OPUS_MODEL="synthetic-review-model",
        MODEL_REGISTRY_FILE=str(ROOT / "config/agents/model-registry.yaml"),
        TMPDIR=str(tmp_path),
    )
    content = tmp_path / 'input with spaces and "quotes".md'
    content.write_text("Synthetic input.\n")
    source = (review / "cross-review.sh").read_text()

    def run(route, shape, *, fail=False, tracked_mode=False):
        if tracked_mode:
            for path in review.glob("submit-to-*.sh"):
                path.chmod(_tracked_permissions(f"scripts/review/{path.name}"))
        reviewer = route if route in ("claude", "codex", "agy") else "codex"
        provider = reviewer if route in ("claude", "codex", "agy") else "claude"
        if route == "limit-substitute":
            # No work identifier means the existing review count is zero.
            # A synthetic zero budget reaches the existing limit branch.
            env["CODEX_MAX_REVIEWS_PER_WRK"] = "0"
        if route == "quota-substitute":
            quota = re.search(r'\[\[ \$codex_exit -eq (\d+) \]\].*QUOTA', source)
            assert quota, "quota branch declaration changed"
            env["QUOTA_EXIT"] = quota.group(1)
        if fail:
            env["FAIL_SUBMITTER"] = f"submit-to-{provider}.sh"
        target = str(content) if shape == "file" else _git("rev-parse", "HEAD")
        kind = "implementation" if shape == "file" else "commit"
        result = subprocess.run(
            ["bash", str(review / "cross-review.sh"), target, reviewer, "--type", kind],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False,
        )
        capture = Path(env["CAPTURE"])
        assert capture.exists(), (result.returncode, result.stdout, result.stderr)
        fields = capture.read_bytes().decode().split("\0")[:-1]
        expected_calls = []
        if route == "quota-substitute":
            expected_calls.extend(["submit-to-codex.sh", "", f"--{shape}", target,
                                   "--prompt", PROMPT])
        model = env["CODEX_OPUS_MODEL"] if route.endswith("substitute") else ""
        expected_calls.extend([f"submit-to-{provider}.sh", model, f"--{shape}", target,
                               "--prompt", PROMPT])
        assert fields == expected_calls
        artifacts = list((review / "results").glob(f"*-{reviewer}.md"))
        artifact, = artifacts
        return result, artifact.read_text()

    return run


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("route", ROUTES)
def test_nonexecutable_submitter_runs_via_bash(dispatch, route, shape):
    result, artifact = dispatch(route, shape)
    assert result.returncode == 0, result.stderr
    assert VERDICT in artifact


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("route", ROUTES)
def test_spaced_path_preserves_arguments(dispatch, route, shape):
    # dispatch compares the entire NUL-delimited vector, including the prompt,
    # file path or commit hash, plus the substitute's model environment value.
    # Retain tracked modes here as well as testing cleared execute bits above.
    result, artifact = dispatch(route, shape, tracked_mode=True)
    assert result.returncode == 0, result.stderr
    assert VERDICT in artifact


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("route", ROUTES)
def test_submitter_failure_propagates(dispatch, route, shape):
    result, artifact = dispatch(route, shape, fail=True)
    if route in ("claude", "agy"):
        assert result.returncode == 0  # Existing artifact-based error handling.
        name = "Claude" if route == "claude" else "Agy"
        assert f"# {name} returned NO_OUTPUT" in artifact
    else:
        assert result.returncode == 1
        assert "CODEX HARD GATE FAILED" in result.stderr
        if route == "codex":
            assert "# Codex review failed (exit 42)" in artifact
        else:
            assert "Synthetic submitter failure" in artifact
    assert VERDICT not in artifact


def test_direct_nonexecutable_fixture_reproduces_permission_failure(dispatch, tmp_path):
    submitter, = tmp_path.glob("checkout with spaces/scripts/review/submit-to-codex.sh")
    # Bash reports command-found-but-not-executable as 126 (issue #3820).
    result = subprocess.run(["bash", "-c", '"$1"', "fixture", str(submitter)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 126


def test_all_shell_submitter_sites_use_bash():
    calls = [line.strip() for line in (REVIEW / "cross-review.sh").read_text().splitlines()
             if '"${SCRIPT_DIR}/submit-to-' in line]
    # Hand audit: Claude direct + substitute, Codex, Agy; commit + file each.
    expected = {"claude": 4, "codex": 2, "agy": 2}
    assert len(calls) == sum(expected.values())
    for provider, count in expected.items():
        selected = [line for line in calls if f"submit-to-{provider}.sh" in line]
        assert len(selected) == count
        assert all(f'bash "${{SCRIPT_DIR}}/submit-to-{provider}.sh"' in line
                   for line in selected)
