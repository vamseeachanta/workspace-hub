from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = REPO_ROOT / "config/drive-index-registry.yml"


def load_alias_map(registry_path: str | Path = DEFAULT_REGISTRY) -> dict[str, str]:
    registry = yaml.safe_load(Path(registry_path).read_text()) or {}
    aliases = registry.get("canonical_aliases", {})
    if not isinstance(aliases, dict):
        raise ValueError("canonical_aliases must be a mapping")

    normalized: dict[str, str] = {}
    for alias, canonical in aliases.items():
        if not isinstance(alias, str) or not isinstance(canonical, str):
            raise ValueError("canonical_aliases entries must be strings")
        if not canonical.startswith("/mnt/") or "/remote/" in canonical:  # abs-path-allowed
            raise ValueError(f"non-canonical alias value for {alias}: {canonical}")
        normalized[alias.rstrip("/")] = canonical.rstrip("/")
    return dict(sorted(normalized.items(), key=lambda item: len(item[0]), reverse=True))


def canonicalize_path(path: str, alias_map: dict[str, str]) -> str:
    for alias, canonical in sorted(alias_map.items(), key=lambda item: len(item[0]), reverse=True):
        if path == alias:
            return canonical
        if path.startswith(alias + "/"):
            return canonical + path[len(alias) :]
    return path


def canonicalize(path: str, alias_map: dict[str, str] | None = None) -> str:
    return canonicalize_path(path, alias_map or load_alias_map())


def is_canonical(path: str, alias_map: dict[str, str] | None = None) -> bool:
    aliases = alias_map or load_alias_map()
    return canonicalize_path(path, aliases) == path and not path.startswith("/mnt/remote/")  # abs-path-allowed


def canonicalize_tree(value: Any, alias_map: dict[str, str]) -> Any:
    if isinstance(value, str):
        normalized = canonicalize_path(value, alias_map)
        return "ace-linux-2" if normalized == "dev-secondary" else normalized
    if isinstance(value, list):
        return [canonicalize_tree(item, alias_map) for item in value]
    if isinstance(value, dict):
        return {key: canonicalize_tree(item, alias_map) for key, item in value.items()}
    return value
