from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from adapters import ADAPTER_TYPES


ALLOWED_TOP_LEVEL = {"version", "canonical_aliases", "defaults", "indexes"}


class RegistryError(Exception):
    pass


@dataclass
class IndexEntry:
    id: str
    adapter: str
    path: Path
    coverage: dict[str, Any]
    domains: list[str] | None
    adapter_params: dict[str, Any]
    freshness: dict[str, Any] | None = None
    builder: str | None = None


@dataclass
class Registry:
    indexes: list[IndexEntry]
    alias_map: dict[str, str]
    defaults: dict[str, Any]

    def get(self, index_id: str) -> IndexEntry:
        for index in self.indexes:
            if index.id == index_id:
                return index
        raise KeyError(index_id)


def load_registry(path: str | Path = "config/drive-index-registry.yml") -> Registry:
    registry_path = Path(path).resolve()
    repo_root = _repo_root()
    try:
        data = yaml.safe_load(registry_path.read_text()) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise RegistryError(f"failed to load registry {registry_path}: {exc}") from exc
    unknown = set(data).difference(ALLOWED_TOP_LEVEL)
    if unknown:
        raise RegistryError(f"unknown top-level key(s): {', '.join(sorted(unknown))}")
    if data.get("version") != 1:
        raise RegistryError("registry version must be 1")
    entries = data.get("indexes")
    if not isinstance(entries, list):
        raise RegistryError("indexes must be a list")
    seen = set()
    indexes = []
    for raw in entries:
        index_id = raw.get("id", "<missing>")
        for key in ("id", "adapter", "path", "coverage", "adapter_params"):
            if key not in raw:
                raise RegistryError(f"{index_id}: missing required key {key}")
        if index_id in seen:
            raise RegistryError(f"duplicate index id: {index_id}")
        seen.add(index_id)
        adapter = raw["adapter"]
        if adapter not in ADAPTER_TYPES:
            raise RegistryError(f"{index_id}: unknown adapter {adapter}")
        coverage = raw["coverage"]
        if not isinstance(coverage, dict) or not coverage.get("drives"):
            raise RegistryError(f"{index_id}: coverage.drives is required")
        raw_path = Path(raw["path"])
        index_path = raw_path
        if not index_path.is_absolute():
            if str(raw_path).startswith("fixtures/") and registry_path.parent.name == "fixtures":
                index_path = registry_path.parent / Path(*raw_path.parts[1:])
            elif (registry_path.parent / raw_path).exists():
                index_path = registry_path.parent / raw_path
            else:
                index_path = repo_root / raw_path
        indexes.append(
            IndexEntry(
                id=index_id,
                adapter=adapter,
                path=index_path.resolve(),
                coverage=coverage,
                domains=raw.get("domains"),
                adapter_params=raw.get("adapter_params") or {},
                freshness=raw.get("freshness"),
                builder=raw.get("builder"),
            )
        )
    return Registry(indexes=indexes, alias_map=data.get("canonical_aliases") or {}, defaults=data.get("defaults") or {})


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
