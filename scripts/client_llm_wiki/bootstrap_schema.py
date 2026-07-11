"""Fail-closed client-wiki bootstrap registry schema."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
from typing import Any, Mapping

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


class BootstrapSchemaError(ValueError):
    """Base error for registry parsing, validation, and denied operations."""


class RegistryParseError(BootstrapSchemaError):
    """The registry is not valid duplicate-safe YAML."""


class RegistryValidationError(BootstrapSchemaError):
    """The parsed registry violates the bootstrap schema."""


class RegistryOperationError(BootstrapSchemaError):
    """The registry cannot authorize the requested operation."""


class RegistryKind(StrEnum):
    CURRENT = "current"
    LEGACY_AUDIT = "legacy-audit"
    PUBLIC_STUB = "public-stub"


class BootstrapMode(StrEnum):
    METADATA_ONLY = "metadata-only"
    SOURCE_REGISTERED_DISABLED = "source-registered-disabled"


@dataclass(frozen=True, slots=True)
class WikiEntry:
    short_name: str
    repo: str
    visibility: str
    posture: str
    status: str
    raw_roots: tuple[str, ...]
    raw_source_status: str
    ingestion_enabled: bool
    mode: BootstrapMode


@dataclass(frozen=True, slots=True)
class Registry:
    kind: RegistryKind
    registry_version: str
    entries: tuple[WikiEntry, ...]
    warnings: tuple[str, ...] = ()


_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.ASCII)
_REPO_COMPONENT = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?", re.ASCII)
_STATUSES = frozenset({"planned", "bootstrapped", "live", "retired"})
_REQUIRED = (
    "short_name",
    "repo",
    "visibility",
    "posture",
    "status",
    "raw_roots",
    "raw_source_status",
    "ingestion_enabled",
)


def _yaml_load(text: str, source: str) -> Any:
    yaml = YAML(typ="safe")
    yaml.allow_duplicate_keys = False
    try:
        return yaml.load(text)
    except (YAMLError, ValueError, TypeError) as exc:
        detail = "duplicate key" if "duplicate" in str(exc).lower() else "invalid YAML"
        raise RegistryParseError(f"{source}: {detail}") from exc


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RegistryValidationError(f"{label} must be a mapping")
    return value


def _legacy_registry(document: Mapping[str, Any]) -> Registry:
    rows = document.get("wikis")
    if not isinstance(rows, list):
        raise RegistryValidationError("legacy registry wikis must be a sequence")
    names: set[str] = set()
    for index, row in enumerate(rows):
        mapping = _require_mapping(row, f"wikis[{index}]")
        name = mapping.get("short_name")
        if isinstance(name, str) and name in names:
            raise RegistryValidationError(f"duplicate short_name: {name}")
        if isinstance(name, str):
            names.add(name)
    warning = "legacy numeric registry_version 0.1 is audit-only; operations denied"
    return Registry(RegistryKind.LEGACY_AUDIT, "0.1", (), (warning,))


def _is_exact_stub(document: Mapping[str, Any]) -> bool:
    return (
        set(document) == {"registry_version", "relocated", "wikis"}
        and document.get("registry_version") == "0.2"
        and document.get("relocated") is True
        and document.get("wikis") == []
    )


def _string(mapping: Mapping[str, Any], field: str, label: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value:
        raise RegistryValidationError(f"{label}.{field} must be a non-empty string")
    return value


def _validate_identity(mapping: Mapping[str, Any], label: str) -> tuple[str, str]:
    short_name = _string(mapping, "short_name", label)
    repo = _string(mapping, "repo", label)
    if _SLUG.fullmatch(short_name) is None:
        raise RegistryValidationError(f"{label}.short_name must be an ASCII slug")
    parts = repo.split("/")
    if len(parts) != 2 or any(_REPO_COMPONENT.fullmatch(part) is None for part in parts):
        raise RegistryValidationError(f"{label}.repo must be an owner/repository slug")
    if parts[1] != f"llm-wiki-{short_name}":
        raise RegistryValidationError(f"{label}.repo basename must match short_name")
    return short_name, repo


def _validate_root(root: Any, label: str) -> str:
    if not isinstance(root, str):
        raise RegistryValidationError(f"{label} raw_roots entries must be strings")
    unsafe = any(ord(character) < 32 or ord(character) == 127 for character in root)
    segments = root.split("/")
    if (
        unsafe
        or not root.startswith("/")
        or root == "/"
        or root.endswith("/")
        or "//" in root
        or "\\" in root
        or any(segment in {".", ".."} for segment in segments)
        or posixpath.normpath(root) != root
    ):
        raise RegistryValidationError(f"{label} raw_roots must be normalized absolute paths")
    return root


def _validate_roots(mapping: Mapping[str, Any], label: str) -> tuple[str, ...]:
    raw = mapping.get("raw_roots")
    if not isinstance(raw, list):
        raise RegistryValidationError(f"{label}.raw_roots must be a sequence")
    roots = tuple(_validate_root(root, label) for root in raw)
    if len(set(roots)) != len(roots):
        raise RegistryValidationError(f"{label} has duplicate raw_roots")
    return roots


def _classify_disabled(
    roots: tuple[str, ...], source_status: str, enabled: bool, label: str
) -> BootstrapMode:
    if enabled:
        raise RegistryValidationError(f"{label}.ingestion_enabled true is unsupported")
    if not roots and source_status == "not-mounted":
        return BootstrapMode.METADATA_ONLY
    if roots and source_status == "mounted":
        return BootstrapMode.SOURCE_REGISTERED_DISABLED
    raise RegistryValidationError(f"{label}.raw_source_status does not match raw_roots")


def _validate_entry(row: Any, index: int) -> WikiEntry:
    label = f"wikis[{index}]"
    mapping = _require_mapping(row, label)
    for field in _REQUIRED:
        if field not in mapping:
            raise RegistryValidationError(f"{label} missing required field {field}")
    short_name, repo = _validate_identity(mapping, label)
    visibility = _string(mapping, "visibility", label)
    posture = _string(mapping, "posture", label)
    status = _string(mapping, "status", label)
    if visibility != "PRIVATE" or posture != "client-private" or status not in _STATUSES:
        raise RegistryValidationError(f"{label} has invalid visibility, posture, or status")
    roots = _validate_roots(mapping, label)
    source_status = _string(mapping, "raw_source_status", label)
    enabled = mapping.get("ingestion_enabled")
    if type(enabled) is not bool:
        raise RegistryValidationError(f"{label}.ingestion_enabled must be a boolean")
    mode = _classify_disabled(roots, source_status, enabled, label)
    return WikiEntry(
        short_name, repo, visibility, posture, status, roots, source_status, enabled, mode
    )


def _current_registry(document: Mapping[str, Any]) -> Registry:
    rows = document.get("wikis")
    if not isinstance(rows, list) or not rows:
        raise RegistryValidationError("current registry wikis must be a non-empty sequence")
    if document.get("relocated") is True:
        raise RegistryValidationError("non-empty registry cannot be relocated")
    entries = tuple(_validate_entry(row, index) for index, row in enumerate(rows))
    names = [entry.short_name for entry in entries]
    if len(set(names)) != len(names):
        duplicate = next(name for name in names if names.count(name) > 1)
        raise RegistryValidationError(f"duplicate short_name: {duplicate}")
    return Registry(RegistryKind.CURRENT, "0.2", entries)


def parse_registry(text: str, *, source: str = "<memory>") -> Registry:
    """Parse a registry without touching any registered filesystem root."""
    document = _require_mapping(_yaml_load(text, source), "registry")
    version = document.get("registry_version")
    if type(version) is float and version == 0.1:
        return _legacy_registry(document)
    if version != "0.2" or not isinstance(version, str):
        raise RegistryValidationError("registry_version must be numeric 0.1 or exact string 0.2")
    if _is_exact_stub(document):
        return Registry(RegistryKind.PUBLIC_STUB, "0.2", ())
    return _current_registry(document)


def load_registry(path: str | os.PathLike[str]) -> Registry:
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RegistryParseError(f"cannot read registry: {source}") from exc
    return parse_registry(text, source=str(source))


def classify_entry(entry: WikiEntry) -> BootstrapMode:
    return entry.mode


def get_entry(registry: Registry, short_name: str) -> WikiEntry:
    if registry.kind is not RegistryKind.CURRENT:
        raise RegistryOperationError(f"{registry.kind.value} registry cannot authorize operations")
    for entry in registry.entries:
        if entry.short_name == short_name:
            return entry
    raise RegistryOperationError(f"registry entry not found: {short_name}")


def _paths_overlap(first: str, second: str) -> bool:
    left = PurePosixPath(first)
    right = PurePosixPath(second)
    return left == right or left in right.parents or right in left.parents


def validate_root_disjointness(
    entry: WikiEntry, protected_paths: list[str] | tuple[str, ...]
) -> None:
    for root in entry.raw_roots:
        for protected in protected_paths:
            if _paths_overlap(root, os.fspath(protected)):
                raise RegistryValidationError(
                    f"raw root overlaps protected path for {entry.short_name}"
                )


__all__ = [
    "BootstrapMode",
    "BootstrapSchemaError",
    "Registry",
    "RegistryKind",
    "RegistryOperationError",
    "RegistryParseError",
    "RegistryValidationError",
    "WikiEntry",
    "classify_entry",
    "get_entry",
    "load_registry",
    "parse_registry",
    "validate_root_disjointness",
]
