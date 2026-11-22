#!/usr/bin/env python3
"""Seed accessibility YAML from one explicit inventory-row adapter.

Input is a YAML mapping with exactly one key, ``rows``, containing a nonempty
list of mappings. Each row declares the existing registry's required fields:
asset_key, title, asset_type, layer, canonical_path, machine_scope,
source_of_truth_tier and durability. It also supplies nonempty ``source_ref``
(an inventory reference identifying the source row) and ``provenance`` (a
reference or statement explaining that declaration). References are retained
verbatim; this adapter does not authenticate them or infer missing metadata.

Asset keys follow the existing validator's naming convention. Canonical paths
are explicitly declared, relative to the supplied root, without parent traversal.
Other supplied registry metadata is retained as YAML scalars, lists and mappings
with string keys; cyclic metadata is rejected. Rows are sorted by asset_key and
mapping keys are sorted for repeatable UTF-8 YAML. List order within each row is
preserved. No sources, sibling repositories or undeclared assets are discovered.
Duplicate YAML mapping keys are rejected; YAML merge keys are unsupported.

CLI (PyYAML required)::

    uv run --no-project --with pyyaml python \
        scripts/knowledge/seed_accessibility_registry.py \
        --inventory supplied-rows.yaml --repo-root synthetic-root \
        --generated 2026-01-01T00:00:00Z --output seeded.yaml

``--generated`` is required: supply an ISO calendar date (as in the existing
registry) or a timezone-aware ISO timestamp. ``--repo-root`` is also required.
The existing validator is loaded with that root injected into its private module
instance; generated YAML is validated in temporary storage before output is
written. The API ``seed_registry(rows, generated=..., repo_root=...)`` returns
that same validated YAML string and raises ValueError for rejected declarations.
The caller chooses the output; this utility neither updates real registries
automatically nor establishes complete authoritative-inventory coverage.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
import importlib.util
from pathlib import Path
import sys
import tempfile

import yaml

# Header compatibility: data/document-index/intelligence-accessibility-registry.yaml.
SCHEMA_VERSION = "1.1.3"


class ValueDumper(yaml.SafeDumper):
    """Serialize validated acyclic metadata independently of shared identity."""

    def ignore_aliases(self, data):
        return True


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(loader, node):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ValueError("inventory mapping keys must be scalar") from exc
        if duplicate:
            raise ValueError("duplicate inventory mapping key")
        mapping[key] = loader.construct_object(value_node, deep=True)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def _load_validator(repo_root):
    # scripts/knowledge is one parent level below scripts.
    path = Path(__file__).resolve().parents[1] / "data/document-index/validate-accessibility-registry.py"
    spec = importlib.util.spec_from_file_location("accessibility_validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO_ROOT = repo_root
    return module


def _require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")


def _validate_generated(generated):
    _require_text(generated, "generated")
    try:
        if "T" in generated:
            timestamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
            if timestamp.utcoffset() is None:
                raise ValueError("timezone required")
        else:
            date.fromisoformat(generated)
    except ValueError as exc:
        raise ValueError("generated must be an ISO date or timezone-aware timestamp") from exc


def _validate_metadata(value, ancestors):
    if isinstance(value, (dict, list)):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("metadata must not contain cycles")
        ancestors.add(identity)
        if isinstance(value, dict):
            if any(not isinstance(key, str) for key in value):
                raise ValueError("metadata mappings must have string keys")
            children = value.values()
        else:
            children = value
        for child in children:
            _validate_metadata(child, ancestors)
        ancestors.remove(identity)
    elif value is not None and not isinstance(value, (str, bool, int, float, date)):
        raise ValueError("metadata must contain YAML scalars, lists or mappings")


def seed_registry(rows: list[dict], *, generated: str, repo_root: Path) -> str:
    _validate_generated(generated)
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a nonempty list of mappings")
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValueError("repo_root must be an existing directory")
    validator = _load_validator(root)
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("rows must contain mappings")
        for field in [*validator.REQUIRED_FIELDS, "source_ref", "provenance"]:
            value = row.get(field)
            if field == "machine_scope":
                if not isinstance(value, list) or not value:
                    raise ValueError("machine_scope must be a nonempty list of strings")
                for scope in value:
                    _require_text(scope, field)
            else:
                _require_text(value, field)
        key = row["asset_key"]
        if not validator.ASSET_KEY_PATTERN.fullmatch(key):
            raise ValueError("asset_key does not match the registry naming convention")
        if key in seen:
            raise ValueError("duplicate asset_key")
        seen.add(key)
        canonical = row["canonical_path"]
        if Path(canonical).is_absolute() or ".." in Path(canonical).parts or "\\" in canonical:
            raise ValueError("canonical_path must be relative without parent traversal")
        if row.get("discoverability") is not None:
            _require_text(row["discoverability"], "discoverability")
        _validate_metadata(row, set())

    document = {
        "generated": generated,
        "schema_version": SCHEMA_VERSION,
        "assets": sorted(rows, key=lambda row: row["asset_key"]),
    }
    try:
        text = yaml.dump(document, Dumper=ValueDumper, sort_keys=True, allow_unicode=True)
    except yaml.YAMLError as exc:
        raise ValueError("rows must contain YAML-compatible metadata") from exc
    with tempfile.TemporaryDirectory(prefix="accessibility-seed-") as temporary:
        path = Path(temporary) / "registry.yaml"
        path.write_text(text, encoding="utf-8", newline="\n")
        errors = validator.validate(path)
    if errors:
        raise ValueError("; ".join(errors))
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--generated", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.inventory.resolve() == args.output.resolve() or (
            args.output.exists() and args.output.samefile(args.inventory)
        ):
            raise ValueError("output must differ from inventory")
        with args.inventory.open(encoding="utf-8") as stream:
            inventory = yaml.load(stream, Loader=UniqueKeyLoader)
        if not isinstance(inventory, dict) or set(inventory) != {"rows"}:
            raise ValueError("inventory must be a mapping containing only rows")
        text = seed_registry(
            inventory["rows"], generated=args.generated, repo_root=args.repo_root
        )
        args.output.write_text(text, encoding="utf-8", newline="\n")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Cannot seed registry: {exc}", file=sys.stderr)
        return 1  # CLI failure status, matching the existing validator.
    return 0  # CLI success status, matching the existing validator.


if __name__ == "__main__":
    sys.exit(main())
