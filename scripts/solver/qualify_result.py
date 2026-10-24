"""Check declared solver-result evidence in JSON without loading any solver."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Support direct execution from a source checkout without installing the hub.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.solvers.base import SolverResult
from src.solvers.qualification import Assumption, Criterion, Status


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError("Non-finite JSON constant")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON result, criteria, units and assumptions")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
        if not isinstance(payload, dict) or set(payload) != {
            "result", "criteria", "output_units", "assumptions",
        }:
            raise ValueError("Invalid input fields")
        raw = payload["result"]
        if not isinstance(raw, dict) or set(raw) != {"success", "solver_name", "result_data"}:
            raise ValueError("Invalid result fields")
        if not isinstance(raw["solver_name"], str) or not raw["solver_name"].strip():
            raise ValueError("Missing solver name")
        if not isinstance(payload["criteria"], list) or not isinstance(payload["assumptions"], list):
            raise TypeError("Criteria and assumptions must be arrays")
        # Zero denotes unavailable timing here; timing is not acceptance evidence.
        result = SolverResult(execution_time_ms=0, **raw)
        report = result.qualify(
            [Criterion(**item) for item in payload["criteria"]],
            output_units=payload["output_units"],
            assumptions=[Assumption(**item) for item in payload["assumptions"]],
        )
        encoded = json.dumps(asdict(report), sort_keys=True, indent=2, allow_nan=False)
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError):
        # Do not echo input content or local filesystem details into reports.
        print("Invalid qualification input", file=sys.stderr)
        return 2
    print(encoded)
    # Conventional CLI exit codes, not engineering acceptance limits.
    return {Status.PASS: 0, Status.FAIL: 1, Status.NOT_EVALUATED: 2}[report.status]


if __name__ == "__main__":
    raise SystemExit(main())
