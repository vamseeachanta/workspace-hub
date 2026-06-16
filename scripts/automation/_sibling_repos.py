"""Per-host sibling-repo list loader.

The full ecosystem repo list carried client repo names, so it is no longer
hardcoded in this public repo (epic #3095, sub-issue #3098). Scripts that need
the list call ``load_sibling_repos()``, which reads the gitignored, per-host
``config/.sibling-repos.local`` (one repo name per line; ``#`` comments allowed)
and falls back to a non-client public default when that file is absent.

Provision ``config/.sibling-repos.local`` per host from the private
``aceengineer-strategy`` archive.
"""
from __future__ import annotations

from pathlib import Path

# Non-client public repos — the safe fallback when config/.sibling-repos.local
# is not provisioned. Contains NO client identifiers.
PUBLIC_DEFAULT_REPOS = [
    "aceengineer-admin",
    "aceengineercode",
    "aceengineer-website",
    "achantas-data",
    "achantas-media",
    "ai-native-traditional-eng",
    "assethold",
    "assetutilities",
    "digitalmodel",
    "energy",
    "hobbies",
    "investments",
    "pyproject-starter",
    "sabithaandkrishnaestates",
    "sd-work",
    "teamresumes",
    "worldenergydata",
]


def load_sibling_repos() -> list[str]:
    """Return the per-host sibling-repo list, or the public default if unprovisioned."""
    # scripts/automation/_sibling_repos.py -> workspace-hub root is two parents up.
    repos_file = Path(__file__).resolve().parents[2] / "config" / ".sibling-repos.local"
    try:
        names = [
            line.split("#", 1)[0].strip()
            for line in repos_file.read_text(encoding="utf-8").splitlines()
        ]
        names = [n for n in names if n]
        if names:
            return names
    except OSError:
        pass
    return list(PUBLIC_DEFAULT_REPOS)
