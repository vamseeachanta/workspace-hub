"""Deterministic checkpoint teaching example; see the autonomous-loop guide.

Only the supplied JSON input is read. Progress stays in memory and the summary
goes to stdout; no workflow engine, external action or durable checkpoint exists.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BUDGET_ERROR = "budget must be a positive integer"
OUTCOME_ERROR = "input must be a nonempty JSON array of retry or success"


def run_checkpoint(outcomes: list[str], budget: int) -> dict:
    """Observe literal actions, verify success, and retain the attempted prefix."""
    # Positive budget and zero boundary: guide, "Local CLI contract".
    if type(budget) is not int or budget <= 0:
        raise ValueError(BUDGET_ERROR)
    if (not isinstance(outcomes, list) or not outcomes
            or any(not isinstance(item, str) or item not in {"retry", "success"}
                   for item in outcomes)):
        raise ValueError(OUTCOME_ERROR)

    checkpoint: list[str] = []
    status = "input_exhausted"
    for outcome in outcomes[:budget]:
        # Each literal is an in-memory action result. Appending records progress;
        # only the explicit success outcome passes the verification checkpoint.
        checkpoint.append(outcome)
        if outcome == "success":
            status = "success"
            break
    else:
        if len(checkpoint) == budget:
            status = "budget_exhausted"

    return {"attempts": len(checkpoint), "budget": budget,
            "history": checkpoint, "status": status}


def positive_budget(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(BUDGET_ERROR) from None
    if value <= 0:
        raise argparse.ArgumentTypeError(BUDGET_ERROR)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="read a JSON array containing retry and success")
    parser.add_argument("--budget", type=positive_budget, required=True,
                        help="maximum number of literal outcomes to attempt")
    args = parser.parse_args(argv)
    try:
        outcomes = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        parser.error("input must be readable UTF-8 JSON")
    try:
        summary = run_checkpoint(outcomes, args.budget)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    # Exit values cite the guide's local CLI contract: success / unverified result.
    return 0 if summary["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
