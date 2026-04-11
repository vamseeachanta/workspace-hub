#!/usr/bin/env python3
"""Validate the intelligence accessibility registry.

Checks:
  - YAML loads without error
  - Schema header fields present (generated, schema_version)
  - Every entry has all required fields
  - asset_key values are unique and match naming convention
  - canonical_path values resolve to existing files or directories
  - Enum fields use valid values (asset_type, layer, source_of_truth_tier, durability, discoverability)

Exit codes:
  0 — all checks pass
  1 — one or more validation errors

Usage:
  uv run scripts/data/document-index/validate-accessibility-registry.py
  uv run scripts/data/document-index/validate-accessibility-registry.py --registry path/to/file.yaml
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_REGISTRY = REPO_ROOT / "data" / "document-index" / "intelligence-accessibility-registry.yaml"

REQUIRED_FIELDS = [
    "asset_key",
    "title",
    "asset_type",
    "layer",
    "canonical_path",
    "machine_scope",
    "source_of_truth_tier",
    "durability",
]

ASSET_TYPE_ENUM = {
    "wiki",
    "registry",
    "ledger",
    "map",
    "architecture-doc",
    "entry-point",
    "seed",
    "governance-doc",
    "operational-template",
}

LAYER_ENUM = {
    "L1",
    "L2",
    "L3",
    "L3-adjacent",
    "L4",
    "L5",
    "L6",
    "recurring-operational",
}

SOURCE_OF_TRUTH_TIER_ENUM = {
    "git-tracked",
    "shared-mount",
    "local-cache",
}

DURABILITY_ENUM = {
    "durable",
    "transient",
    "recurring-operational",
}

DISCOVERABILITY_ENUM = {
    "discoverable",
    "partially-discoverable",
    "hard-to-discover",
}

ASSET_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def validate(registry_path: Path) -> list[str]:
    """Return a list of error strings. Empty list means valid."""
    errors: list[str] = []

    if not registry_path.exists():
        errors.append(f"Registry file not found: {registry_path}")
        return errors

    with open(registry_path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            errors.append(f"YAML parse error: {exc}")
            return errors

    if not isinstance(data, dict):
        errors.append("Registry root must be a YAML mapping")
        return errors

    # Schema header
    if "generated" not in data:
        errors.append("Missing top-level field: generated")
    if "schema_version" not in data:
        errors.append("Missing top-level field: schema_version")

    assets = data.get("assets")
    if not isinstance(assets, list):
        errors.append("Missing or invalid 'assets' array")
        return errors

    if len(assets) == 0:
        errors.append("Registry has no entries")
        return errors

    seen_keys: set[str] = set()

    for i, entry in enumerate(assets):
        prefix = f"assets[{i}]"

        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry is not a mapping")
            continue

        key = entry.get("asset_key", f"<missing-key-{i}>")
        prefix = f"assets[{i}] ({key})"

        # Required fields
        for field in REQUIRED_FIELDS:
            val = entry.get(field)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                errors.append(f"{prefix}: missing required field '{field}'")

        # asset_key uniqueness
        if key in seen_keys:
            errors.append(f"{prefix}: duplicate asset_key '{key}'")
        seen_keys.add(key)

        # asset_key format
        if isinstance(key, str) and not ASSET_KEY_PATTERN.match(key):
            errors.append(
                f"{prefix}: asset_key '{key}' does not match pattern "
                f"^[a-z][a-z0-9]*(-[a-z0-9]+)*$"
            )

        # Enum validation
        asset_type = entry.get("asset_type")
        if asset_type and asset_type not in ASSET_TYPE_ENUM:
            errors.append(
                f"{prefix}: invalid asset_type '{asset_type}' "
                f"(valid: {sorted(ASSET_TYPE_ENUM)})"
            )

        layer = entry.get("layer")
        if layer and layer not in LAYER_ENUM:
            errors.append(
                f"{prefix}: invalid layer '{layer}' "
                f"(valid: {sorted(LAYER_ENUM)})"
            )

        sot_tier = entry.get("source_of_truth_tier")
        if sot_tier and sot_tier not in SOURCE_OF_TRUTH_TIER_ENUM:
            errors.append(
                f"{prefix}: invalid source_of_truth_tier '{sot_tier}' "
                f"(valid: {sorted(SOURCE_OF_TRUTH_TIER_ENUM)})"
            )

        dur = entry.get("durability")
        if dur and dur not in DURABILITY_ENUM:
            errors.append(
                f"{prefix}: invalid durability '{dur}' "
                f"(valid: {sorted(DURABILITY_ENUM)})"
            )

        disc = entry.get("discoverability")
        if disc and disc not in DISCOVERABILITY_ENUM:
            errors.append(
                f"{prefix}: invalid discoverability '{disc}' "
                f"(valid: {sorted(DISCOVERABILITY_ENUM)})"
            )

        # machine_scope must be a non-empty list
        scope = entry.get("machine_scope")
        if scope is not None:
            if not isinstance(scope, list) or len(scope) == 0:
                errors.append(f"{prefix}: machine_scope must be a non-empty list")

        # canonical_path existence
        cpath = entry.get("canonical_path")
        if isinstance(cpath, str) and cpath:
            resolved = REPO_ROOT / cpath
            if not resolved.exists():
                errors.append(
                    f"{prefix}: canonical_path does not exist: {cpath}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate intelligence accessibility registry"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="Path to the registry YAML file",
    )
    args = parser.parse_args()

    errors = validate(args.registry)

    if errors:
        print(f"FAIL — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    # Count entries for summary
    with open(args.registry) as f:
        data = yaml.safe_load(f)
    count = len(data.get("assets", []))
    print(f"OK — {count} entries validated, no errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
