"""Regression guard — the canonical merge babysitter must be executable.

Same defect class as #3142 (review helpers), re-appearing on a different script.

`.claude/rules/merge-authorization.md` rule 8 makes this helper MANDATORY for an
authorized agent-run merge ("must use `scripts/operations/merge-when-clean.sh
--merge`"), and `.claude/rules/model-routing.md` corollary 5 documents the same
path invocation. Tracked non-executable (git mode 100644), that documented
command fails with `Permission denied`.

Measured 2026-08-03: an authorized merge of #3797 invoked the helper exactly as
the rule documents and it died instantly. The failure was near-silent — the
invocation was piped (`... | tail`), so the shell reported the exit status of
`tail`, and the run looked successful while nothing had been merged. A rule that
mandates a command the repo ships non-executable is a rule that cannot be
followed on a fresh clone.

Only PATH-INVOKED scripts belong here. A script passed as an ARGUMENT
(`bash foo.sh`, `uv run python foo.py`) does not need the bit, and adding one
would be noise — see the same carve-out in
tests/review/test_helpers_executable.py.

Level-2 enforcement of the prose rule "scripts invoked directly must be
executable" (.claude/rules/patterns.md enforcement gradient).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Scripts the .claude/rules/ contract tells an agent to invoke BY PATH.
DIRECTLY_INVOKED_HELPERS = [
    "scripts/operations/merge-when-clean.sh",
]


def _git_mode(path: str) -> str:
    out = subprocess.run(
        ["git", "ls-files", "-s", path],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert out, f"{path} is not tracked by git"
    return out.split()[0]  # e.g. "100755"


@pytest.mark.parametrize("helper", DIRECTLY_INVOKED_HELPERS)
def test_directly_invoked_helper_is_executable(helper):
    assert (REPO_ROOT / helper).exists(), f"missing helper {helper}"
    mode = _git_mode(helper)
    assert mode == "100755", (
        f"{helper} is tracked {mode}; must be 100755 — .claude/rules/ documents "
        f"invoking it by path, so a non-executable bit makes the documented "
        f"command fail with Permission denied on any fresh clone"
    )
