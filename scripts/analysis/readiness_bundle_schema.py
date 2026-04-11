"""Helpers for validating readiness evidence bundles against the schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "docs" / "modules" / "ai" / "readiness-evidence-bundle.schema.yaml"


def load_schema() -> dict[str, Any]:
    """Load the readiness evidence bundle schema."""
    return yaml.safe_load(SCHEMA_PATH.read_text())


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    """Validate a readiness evidence bundle and return normalized error strings."""
    validator = Draft7Validator(load_schema(), format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(bundle), key=lambda item: list(item.path)):
        path = "/".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors


def validate_bundle_file(path: str | Path) -> list[str]:
    """Load and validate a readiness evidence bundle file."""
    path = Path(path)
    bundle = yaml.safe_load(path.read_text())
    return validate_bundle(bundle)
