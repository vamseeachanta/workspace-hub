"""Single source of truth reader for the tier-1 Python repo list (#3023).

Read ``config/tier1-python-repos.txt`` instead of hardcoding the repo list.

    from scripts.lib.tier1_repos import tier1_python_repos
    for slug in tier1_python_repos():
        ...

Resolution order for the canonical file:
    1. explicit ``path`` argument
    2. ``$TIER1_REPOS_FILE`` (test override)
    3. ``$REPO_ROOT/config/tier1-python-repos.txt``
    4. derived from this file's location (scripts/lib -> repo root)
"""
from __future__ import annotations

import os
from pathlib import Path

_REL = "config/tier1-python-repos.txt"


def _resolve(path: str | os.PathLike[str] | None) -> Path:
    if path is not None:
        return Path(path)
    env = os.environ.get("TIER1_REPOS_FILE")
    if env:
        return Path(env)
    repo_root = os.environ.get("REPO_ROOT")
    if repo_root and (Path(repo_root) / _REL).is_file():
        return Path(repo_root) / _REL
    # scripts/lib/tier1_repos.py -> repo root is two parents up
    return Path(__file__).resolve().parents[2] / _REL


def tier1_python_repos(path: str | os.PathLike[str] | None = None) -> list[str]:
    """Return the tier-1 Python repo slugs, in file order.

    Raises ``RuntimeError`` on a missing/empty list — a silent empty list would
    make gates that iterate it become no-ops.
    """
    f = _resolve(path)
    if not f.is_file():
        raise RuntimeError(f"tier-1 repo list not found: {f}")
    slugs: list[str] = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            slugs.append(line)
    if not slugs:
        raise RuntimeError(f"tier-1 repo list is empty: {f}")
    return slugs


if __name__ == "__main__":  # pragma: no cover - manual probe
    print("\n".join(tier1_python_repos()))
