"""Fail-closed client-wiki bootstrap registry schema."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
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
_GITHUB_OWNER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", re.ASCII)
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
        name = _validate_legacy_row(mapping, f"wikis[{index}]")
        if name in names:
            raise RegistryValidationError(f"duplicate short_name: {name}")
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


def _validate_legacy_row(mapping: Mapping[str, Any], label: str) -> str:
    for field in ("raw_source_status", "ingestion_enabled"):
        if field in mapping:
            raise RegistryValidationError(f"{label}.{field} is invalid for a legacy registry")
    short_name = _string(mapping, "short_name", label)
    _string(mapping, "repo", label)
    visibility = _string(mapping, "visibility", label)
    posture = _string(mapping, "posture", label)
    status = _string(mapping, "status", label)
    roots = mapping.get("raw_roots")
    if visibility != "PRIVATE" or posture != "client-private" or status not in _STATUSES:
        raise RegistryValidationError(f"{label} has invalid historical posture/state")
    if (
        not isinstance(roots, list)
        or not roots
        or any(not isinstance(root, str) or not root for root in roots)
    ):
        raise RegistryValidationError(f"{label}.raw_roots must be a non-empty string sequence")
    return short_name


def validate_repo_slug(repo_slug: str) -> str:
    """Return the client short name from an exact GitHub repository slug."""
    if not isinstance(repo_slug, str):
        raise RegistryValidationError("repository slug must be a string")
    parts = repo_slug.split("/")
    owner = parts[0] if len(parts) == 2 else ""
    if _GITHUB_OWNER.fullmatch(owner) is None or "--" in owner:
        raise RegistryValidationError("repository owner is not GitHub-safe")
    basename = parts[1]
    prefix = "llm-wiki-"
    short_name = basename.removeprefix(prefix)
    if not basename.startswith(prefix) or _SLUG.fullmatch(short_name) is None:
        raise RegistryValidationError("repository basename must be llm-wiki-<short-name>")
    return short_name


def _validate_identity(mapping: Mapping[str, Any], label: str) -> tuple[str, str]:
    short_name = _string(mapping, "short_name", label)
    repo = _string(mapping, "repo", label)
    if _SLUG.fullmatch(short_name) is None:
        raise RegistryValidationError(f"{label}.short_name must be an ASCII slug")
    try:
        repo_short_name = validate_repo_slug(repo)
    except RegistryValidationError as exc:
        raise RegistryValidationError(f"{label}.repo is invalid: {exc}") from exc
    if repo_short_name != short_name:
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


def _classify_disabled(roots: tuple[str, ...], source_status: str, enabled: bool, label: str) -> BootstrapMode:
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
        short_name,
        repo,
        visibility,
        posture,
        status,
        roots,
        source_status,
        enabled,
        mode,
    )


def _current_registry(document: Mapping[str, Any]) -> Registry:
    rows = document.get("wikis")
    if not isinstance(rows, list) or not rows:
        raise RegistryValidationError("current registry wikis must be a non-empty sequence")
    if "relocated" in document and document.get("relocated") is not False:
        raise RegistryValidationError("authoritative registry relocated must be false or absent")
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
    registry = parse_registry(text, source=str(source))
    if registry.kind is RegistryKind.CURRENT:
        template, canonical = _module_checkout_roots()
        for entry in registry.entries:
            validate_root_disjointness(
                entry,
                (
                    str(template),
                    str(canonical),
                    str(canonical.parent / f"llm-wiki-{entry.short_name}"),
                ),
            )
    return registry


def _module_checkout_roots() -> tuple[Path, Path]:
    """Return active and canonical checkouts from module-anchored Git metadata."""
    active = Path(__file__).absolute().parents[2]
    dot_git = active / ".git"
    if _is_real_kind(dot_git, directory=True):
        return active, active
    try:
        marker = _metadata_line(dot_git)
        if not marker.startswith("gitdir: "):
            raise ValueError("invalid linked-worktree .git marker")
        git_dir = Path(marker.removeprefix("gitdir: "))
        if not git_dir.is_absolute():
            git_dir = Path(os.path.abspath(active / git_dir))
        if not _is_real_kind(git_dir, directory=True):
            raise ValueError("Git directory is not a real directory")
        common_text = _metadata_line(git_dir / "commondir")
        common = Path(common_text)
        if not common.is_absolute():
            common = Path(os.path.abspath(git_dir / common))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RegistryValidationError("module Git layout is invalid") from exc
    if common.name != ".git" or not _is_real_kind(common, directory=True):
        raise RegistryValidationError("module Git common directory must be .git")
    return active, common.parent


def _is_real_kind(path: Path, *, directory: bool) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    return expected(info.st_mode) and not stat.S_ISLNK(info.st_mode)


def _metadata_line(path: Path) -> str:
    if not _is_real_kind(path, directory=False):
        raise ValueError("Git metadata is not a real regular file")
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1 or not lines[0] or any(ord(char) < 32 or ord(char) == 127 for char in lines[0]):
        raise ValueError("Git metadata must contain one safe line")
    return lines[0]


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


def validate_root_disjointness(entry: WikiEntry, protected_paths: list[str] | tuple[str, ...]) -> None:
    for root in entry.raw_roots:
        for protected in protected_paths:
            if _paths_overlap(root, os.fspath(protected)):
                raise RegistryValidationError(f"raw root overlaps protected path for {entry.short_name}")


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
    "validate_repo_slug",
    "validate_root_disjointness",
]
