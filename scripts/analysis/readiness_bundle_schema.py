"""Validate readiness evidence structure and internal consistency; run no probes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT / "docs" / "modules" / "ai" / "readiness-evidence-bundle.schema.yaml"
)


class _UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys and merge overrides instead of losing evidence."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in mapping:
                    raise yaml.constructor.ConstructorError(
                        None, None, "duplicate key", node.start_mark
                    )
                mapping[key] = self.construct_object(value_node, deep=deep)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    None, None, "invalid mapping key", node.start_mark
                ) from error
        return mapping


def load_schema() -> dict[str, Any]:
    """Load the repository-owned readiness evidence schema."""
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def _consistency_errors(bundle: dict[str, Any]) -> list[str]:
    """Apply the companion readiness-evidence-validation contract, rev 1."""
    errors = []
    checks = bundle["checks"]
    ids = [check["id"] for check in checks]
    if len(set(ids)) != len(ids):
        errors.append("checks: duplicate check id")
    counts = Counter(check["status"] for check in checks)
    counts["total"] = len(checks)
    for field, value in bundle["overall"].get("counts", {}).items():
        if value != counts[field]:
            errors.append(f"overall/counts/{field}: count mismatch")
    for index, check in enumerate(checks):
        evidence = check.get("evidence", {})
        if (
            check["id"] == "access-mode"
            and evidence["transport"] != bundle["access"]["mode"]
        ):
            errors.append(f"checks/{index}/evidence: transport mismatch")
        if (
            check["id"] == "licensed-tools"
            and "seats_total" in evidence
            and evidence["seats_in_use"] > evidence["seats_total"]
        ):
            errors.append(f"checks/{index}/evidence: capacity exceeded")
    if bundle["overall"]["verdict"] == "ready" and (
        not bundle["access"]["reachable"]
        or any(counts[s] for s in ("warn", "fail", "error"))
    ):
        errors.append("overall/verdict: ready contradicts evidence")
    return errors


def validate_bundle(bundle: Any) -> list[str]:
    """Return structural errors, or consistency errors for a structured bundle.

    Detailed library errors may contain input values; keep them in private logs.
    Successful validation establishes consistency, not current readiness.
    """
    validator = Draft7Validator(load_schema(), format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(bundle), key=lambda item: tuple(map(str, item.path))
    ):
        path = "/".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{path}: {error.message}")
    return errors or _consistency_errors(bundle)


def validate_bundle_file(path: str | Path) -> list[str]:
    """Read UTF-8 YAML, rejecting unreadable, malformed or ambiguous input."""
    try:
        bundle = yaml.load(
            Path(path).read_text(encoding="utf-8"), Loader=_UniqueKeyLoader
        )
    except (OSError, UnicodeError):
        return ["$: input could not be read"]
    except (yaml.YAMLError, RecursionError, ValueError):
        return ["$: invalid or ambiguous input"]
    return validate_bundle(bundle)


class _PrivateArgumentParser(argparse.ArgumentParser):
    """Keep rejected argument values out of diagnostics."""

    def error(self, message):
        self.exit(2, "invalid command arguments\n")


def main(argv: list[str] | None = None) -> int:
    """Emit only a validity flag and error count, never bundle data or paths."""
    parser = _PrivateArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Local evidence YAML file")
    args = parser.parse_args(argv)
    errors = validate_bundle_file(args.bundle)
    print(json.dumps({"valid": not errors, "error_count": len(errors)}, sort_keys=True))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
