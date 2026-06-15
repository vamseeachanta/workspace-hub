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
import sys
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


def _has_repo_marker(path: Path) -> bool:
    return (path / ".git").is_dir() or (path / "pyproject.toml").is_file()


def resolve_tier1_repo_path(
    slug: str,
    repo_root: str | os.PathLike[str] | None = None,
    base: str | os.PathLike[str] | None = None,
) -> Path:
    """Resolve a tier-1 repo slug for nested or sibling checkout layouts.

    Probe order matches ``scripts/lib/tier1-repos.sh``:
    explicit base / ``$TIER1_REPOS_BASE``, then ``repo_root/slug``, then the
    sibling ``dirname(repo_root)/slug``. A path counts only if it has a repo
    marker (``.git`` directory or ``pyproject.toml``). Missing repos fail closed.
    """
    if not slug:
        raise FileNotFoundError("empty tier-1 repo slug")

    root_value = repo_root or os.environ.get("REPO_ROOT") or Path(__file__).resolve().parents[2]
    root = Path(root_value).resolve()
    base_value = base or os.environ.get("TIER1_REPOS_BASE")

    candidates: list[Path] = []
    if base_value:
        candidates.append(Path(base_value).expanduser() / slug)
    candidates.extend([root / slug, root.parent / slug])

    seen: set[str] = set()
    found: list[Path] = []
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if _has_repo_marker(candidate):
            found.append(candidate)

    if not found:
        raise FileNotFoundError(
            f"could not resolve tier-1 repo {slug!r} from base/nested/sibling layouts"
        )
    if len(found) > 1:
        print(
            f"tier1_repos.py: WARN {slug} resolves at multiple layouts: "
            f"{' '.join(str(p) for p in found)}; using {found[0]}",
            file=sys.stderr,
        )
    return found[0]


if __name__ == "__main__":  # pragma: no cover - manual probe
    print("\n".join(tier1_python_repos()))
