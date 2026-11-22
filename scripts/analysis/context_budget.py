#!/usr/bin/env python3
"""Account for explicitly selected UTF-8 snapshots offline.

Usage: python scripts/analysis/context_budget.py manifest.json

Manifest shape (the budget is an example input, not a provider limit):
    {"budget_lexical_units": 6,
     "components": [{"id": "instructions", "path": "snapshot.txt"}]}

Relative component paths are relative to the manifest directory; absolute paths
are accepted when explicitly listed. No configuration or transcript discovery
occurs. Every component entry is counted once, even if paths refer to the same
file. Identifiers must be unique. Empty selections and zero budgets are valid.

Bytes are counted before decoding, preserving original line endings. A lexical
unit is a maximal non-whitespace run using Python's Unicode whitespace rules
(str.split with no separator). This is an estimate, not provider tokens or live
context usage. Remaining units equal the supplied budget minus the total; a
negative result is over budget. Model-token percentages, recommendations and
slash-command wiring are deferred.

Input failures emit only an incomplete JSON error, never partial totals or file
contents. A complete report, including an over-budget report, exits successfully.

Plan-lite
---------
Scope: a standalone standard-library CLI for explicit UTF-8 snapshot manifests,
strict validation, byte and lexical-unit counts, and supplied-budget subtraction.
Validation command (with an isolated pytest temporary directory when needed):
    uv run --no-project --with pytest python -m pytest tests/analysis/test_context_budget.py -q -rA -p no:cacheprovider
The tests check literal hand counts, input failures, and CLI output independently
of the implementation's calculations.
Deferred: provider-token accounting, live context discovery, model-token
percentages, recommendations, and slash-command integration.
"""

import argparse
import json
from pathlib import Path


class ContextBudgetError(ValueError):
    """Invalid or unavailable inputs prevent a complete snapshot report."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContextBudgetError("duplicate manifest key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ContextBudgetError("non-finite manifest value")


def _read_manifest(path):
    try:
        if not path.is_file():
            raise ContextBudgetError("manifest cannot be read as UTF-8 JSON")
        data = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except ContextBudgetError:
        raise
    except (OSError, ValueError, RecursionError) as from_error:
        raise ContextBudgetError("manifest cannot be read as UTF-8 JSON") from from_error

    if not isinstance(data, dict) or set(data) != {"budget_lexical_units", "components"}:
        raise ContextBudgetError("manifest requires only budget_lexical_units and components")
    budget = data["budget_lexical_units"]
    # Zero is the minimum count; bool is excluded despite being an int subtype.
    if type(budget) is not int or budget < 0:
        raise ContextBudgetError("budget_lexical_units must be a nonnegative integer")
    components = data["components"]
    if not isinstance(components, list):
        raise ContextBudgetError("components must be a list")

    identifiers = set()
    for component in components:
        if not isinstance(component, dict) or set(component) != {"id", "path"}:
            raise ContextBudgetError("each component requires only id and path")
        if any(not isinstance(value, str) or not value.strip() for value in component.values()):
            raise ContextBudgetError("component id and path must be nonempty strings")
        if component["id"] in identifiers:
            raise ContextBudgetError("duplicate component identifier")
        identifiers.add(component["id"])
    return data


def audit_manifest(manifest_path):
    """Return a complete JSON-compatible report or raise ContextBudgetError."""
    path = Path(manifest_path).absolute()
    data = _read_manifest(path)
    components = []
    for component in data["components"]:
        component_path = path.parent / component["path"]
        try:
            # Refuse directories and special files rather than reading a stream.
            if not component_path.is_file():
                raise ContextBudgetError("component cannot be read as UTF-8")
            raw = component_path.read_bytes()
            text = raw.decode("utf-8")
        except ContextBudgetError:
            raise
        except (OSError, ValueError) as from_error:
            raise ContextBudgetError("component cannot be read as UTF-8") from from_error
        components.append({
            "id": component["id"],
            "bytes": len(raw),
            "lexical_units": len(text.split()),
        })

    totals = {
        "bytes": sum(component["bytes"] for component in components),
        "lexical_units": sum(component["lexical_units"] for component in components),
    }
    remaining = data["budget_lexical_units"] - totals["lexical_units"]
    return {
        "complete": True,
        "method": "lexical-unit estimate: maximal non-whitespace runs",
        "limitations": "Not provider tokens or live context usage.",
        "components": components,
        "totals": totals,
        "budget": {
            "lexical_units": data["budget_lexical_units"],
            "remaining_lexical_units": remaining,
            # Negative remaining units indicate the supplied budget is exceeded.
            "over_budget": remaining < 0,
        },
    }


def main(argv=None):
    """Print a JSON report; follow CLI convention of zero success, one failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="explicit snapshot manifest (JSON)")
    args = parser.parse_args(argv)
    try:
        report = audit_manifest(args.manifest)
    except ContextBudgetError as error:
        print(json.dumps({"complete": False, "error": str(error)}))
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
