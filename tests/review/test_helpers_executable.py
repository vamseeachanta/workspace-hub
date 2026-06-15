"""Regression guard for #3142 — review helpers invoked DIRECTLY must be executable.

scripts/review/submit-to-codex.sh and submit-to-gemini.sh invoke the validator by
path (`"$VALIDATOR" "$rendered_file"`), NOT via `bash`. Tracked non-executable
(git mode 100644), a fresh clone/worktree fails with `Permission denied` and review
rendering breaks (Codex exit 6 / Gemini "no renderable output"). This test asserts
the directly-invoked helper is tracked mode 100755 so the bug cannot regress.

NOTE: render-structured-review.py is invoked as `uv run --no-project python "$RENDERER"`
(an argument to python), so its executable bit is NOT required — it is intentionally
excluded here. Only path-invoked helpers belong in this guard.

Level-2 enforcement of the prose rule "scripts invoked directly must be executable"
(.claude/rules/patterns.md enforcement gradient).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Helpers that submit-to-*.sh invoke DIRECTLY by path (not as an arg to bash/python).
# Invocation site: `"$VALIDATOR" "$rendered_file"` in submit-to-codex.sh / submit-to-gemini.sh.
DIRECTLY_INVOKED_HELPERS = [
    "scripts/review/validate-review-output.sh",
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
        f"{helper} is tracked {mode}; must be 100755 — submit-to-*.sh invokes it "
        f"directly, so a non-executable bit breaks review rendering on fresh clones (#3142)"
    )
