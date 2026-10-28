#!/usr/bin/env python3
"""Normalize an existing repository snapshot; see ecosystem_doctor.md for v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Version and count semantics: ecosystem_doctor.md, Schema and Inventory input.
SCHEMA_VERSION = 1
COUNT_FIELDS = (
    "declared", "configured", "present", "missing", "non_git",
    "contract_complete", "unexpected_count",
)
OTHER_GROUPS = (
    "providers", "machines", "schedules", "skills", "memory", "privacy",
    "business_outcomes",
)


def _unavailable(reason_code: str) -> dict:
    return {
        "group": "repositories", "status": "unavailable",
        "reason_code": reason_code, "counts": {},
    }


def _is_count(value: object) -> bool:
    return type(value) is int and value >= 0


def normalize_repository_inventory(snapshot: object) -> dict:
    """Return aggregate repository coverage without inspecting repository rows.

    This function never reads files, collects facts, or modifies its input.
    Unknown fields are discarded, including names and diagnostic text.
    """
    if snapshot is None:
        return _unavailable("snapshot_missing")
    if not isinstance(snapshot, dict):
        return _unavailable("snapshot_malformed")
    version = snapshot.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        return _unavailable("snapshot_unsupported")
    summary = snapshot.get("summary")
    if not isinstance(summary, dict):
        return _unavailable("snapshot_malformed")
    coverage = summary.get("adapter_coverage")
    if not isinstance(coverage, dict):
        return _unavailable("snapshot_malformed")
    required = (*COUNT_FIELDS, "observed_declared", "unknown")
    if not all(_is_count(summary.get(key)) for key in required):
        return _unavailable("snapshot_malformed")
    if not all(_is_count(coverage.get(key)) for key in ("complete", "incomplete")):
        return _unavailable("snapshot_malformed")
    if (
        summary["declared"] != summary["present"] + summary["missing"] + summary["non_git"]
        or summary["observed_declared"] != summary["present"]
        or summary["unknown"] != summary["unexpected_count"]
        or coverage["complete"] != summary["contract_complete"]
        or coverage["complete"] + coverage["incomplete"] != summary["declared"]
        or summary["contract_complete"] > summary["present"]
    ):
        return _unavailable("snapshot_malformed")
    if not summary["declared"]:
        return _unavailable("inventory_empty")
    counts = {key: summary[key] for key in COUNT_FIELDS}
    counts["contract_incomplete"] = coverage["incomplete"]
    incomplete = any(counts[key] for key in (
        "missing", "non_git", "contract_incomplete", "unexpected_count",
    ))
    return {
        "group": "repositories",
        "status": "degraded" if incomplete else "healthy",
        "reason_code": "inventory_incomplete" if incomplete else "inventory_complete",
        "counts": counts,
    }


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite value")


def _load_inventory(path: Path | None) -> dict:
    if path is None:
        return _unavailable("snapshot_missing")
    try:
        text = path.read_text(encoding="utf-8")
        snapshot = json.loads(
            text, object_pairs_hook=_unique_object, parse_constant=_reject_constant,
        )
    except FileNotFoundError:
        return _unavailable("snapshot_missing")
    except OSError:
        return _unavailable("snapshot_unreadable")
    except (ValueError, UnicodeError, RecursionError):
        return _unavailable("snapshot_malformed")
    return normalize_repository_inventory(snapshot)


def _result(repository_probe: dict) -> dict:
    probes = [repository_probe]
    probes.extend({
        "group": group, "status": "unavailable",
        "reason_code": "adapter_not_implemented", "counts": {},
    } for group in OTHER_GROUPS)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "unavailable",  # Remaining adapters have no evidence in this slice.
        "probes": probes,
    }


def render_human(result: dict) -> str:
    """Render the same status, reason and count fields as the JSON report."""
    lines = [f"Ecosystem doctor v{result['schema_version']}", f"overall: {result['status']}"]
    for probe in result["probes"]:
        lines.append(f"{probe['group']}: {probe['status']} ({probe['reason_code']})")
        if probe["counts"]:
            lines.append("  " + ", ".join(
                f"{key}={value}" for key, value in sorted(probe["counts"].items())
            ))
    return "\n".join(lines) + "\n"


class _Parser(argparse.ArgumentParser):
    def error(self, _message: str) -> None:
        # argparse diagnostics can otherwise echo arbitrary command-line values.
        self.exit(2, "Invalid arguments; use --help for usage.\n")


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__)
    parser.add_argument("--inventory", type=Path, help="Existing inventory JSON snapshot")
    parser.add_argument("--json", action="store_true", help="Emit the versioned JSON result")
    args = parser.parse_args(argv)
    result = _result(_load_inventory(args.inventory))
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else render_human(result),
          end="\n" if args.json else "")
    # Exit contract is documented beside the schema; this slice is unavailable.
    return 0 if result["status"] == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
