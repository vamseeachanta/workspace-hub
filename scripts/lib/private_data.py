"""Resolve data that must not live in this PUBLIC checkout (owner decision C20).

The archive-drive content index and the conference/document indexes are built
on a host from the private archive drive and carry client names. They live in
a private repository. Their builders and readers resolve them here, relative to
the private data directory named by ``WORKSPACE_HUB_PRIVATE_DATA_DIR`` -- set in
the host's private configuration, never committed.

Fail closed: an unset, relative or missing directory, or one inside this
repository, raises ``PrivateDataUnavailable``. Messages name the variable, never
the path, which can itself carry an identifier.

Load it by path::

    spec = importlib.util.spec_from_file_location("private_data", <repo>/scripts/lib/private_data.py)
"""
from __future__ import annotations

import os
from pathlib import Path

ENV = "WORKSPACE_HUB_PRIVATE_DATA_DIR"
REPO_ROOT = Path(__file__).resolve().parents[2]


class PrivateDataUnavailable(RuntimeError):
    """The private data location is not usable. Nothing may be written."""


def _inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def private_data_dir() -> Path:
    raw = os.environ.get(ENV, "").strip()
    if not raw:
        raise PrivateDataUnavailable(
            f"{ENV} is not set: this output carries client identifiers and is written "
            "only to the private data directory (C20)"
        )
    base = Path(raw).expanduser()
    if not base.is_absolute():
        raise PrivateDataUnavailable(f"{ENV} must be an absolute path")
    if not base.is_dir():
        raise PrivateDataUnavailable(f"the directory {ENV} names does not exist")
    if _inside_repo(base):
        raise PrivateDataUnavailable(
            f"{ENV} points inside the public workspace-hub checkout; refusing"
        )
    return base


def private_data_path(rel: str) -> Path:
    """``rel`` (repository-style, e.g. ``data/content_index.json``) under the
    private data directory."""
    return private_data_dir() / Path(rel)


def require_outside_repo(path: str | os.PathLike[str]) -> Path:
    """An explicitly given output path, refused when it is inside this public
    checkout."""
    p = Path(path)
    if _inside_repo(p if p.is_absolute() else Path.cwd() / p):
        raise PrivateDataUnavailable(
            "this output carries client identifiers and may not be written inside the "
            "public workspace-hub checkout (C20)"
        )
    return p


def resolve_output(explicit: str | os.PathLike[str] | None, rel: str) -> Path:
    """The explicit path when given (outside this checkout), else ``rel`` under
    the private data directory."""
    if explicit:
        return require_outside_repo(explicit)
    return private_data_path(rel)
