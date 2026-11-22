"""Read-only detection of Git working-tree roots, including linked worktrees."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def is_git_worktree_root(path: str | os.PathLike[str]) -> bool:
    """Validate a root without trusting marker shape or inherited Git bindings.

    Git reference: https://git-scm.com/docs/git-rev-parse (accessed 2026-10-22),
    --local-env-vars, --is-inside-work-tree and --show-prefix. Requiring a marker
    and an empty prefix prevents ancestor discovery from accepting child folders.
    This checks layout, not repository identity or permission to modify it.
    """
    candidate = Path(path)
    if not candidate.is_dir() or not (candidate / ".git").exists():
        return False
    try:
        bindings = subprocess.run(
            ["git", "rev-parse", "--local-env-vars"],
            check=True, capture_output=True, text=True,
        )
        env = os.environ.copy()
        for name in bindings.stdout.splitlines():
            env.pop(name, None)
        probe = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--is-inside-work-tree", "--show-prefix"],
            env=env, check=True, capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return probe.stdout == "true\n\n"
