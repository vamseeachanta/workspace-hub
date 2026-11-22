"""Check a coordinator's complete roster before admitting repository work.

Policy source: issue 3829 (2026), repository write serialization. This pure
preflight does not reserve work or authenticate roster completeness/freshness.
The coordinator must serialize evaluation, registration, and writer startup.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Repository identifiers are canonical keys, never checkout paths or URLs.
_REPOSITORY = re.compile(r"[a-z0-9][a-z0-9_.-]*/[a-z0-9][a-z0-9_.-]*")
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]*")
_PROVIDERS = {"codex", "claude", "agy", "gemini", "hermes", "other"}
_TASK_FIELDS = {"task", "repository", "provider", "access"}


def validate_task(task: dict) -> None:
    """Reject ambiguous records instead of treating them as inactive work."""
    if not isinstance(task, dict) or set(task) != _TASK_FIELDS:
        raise ValueError("invalid task fields")
    if not all(isinstance(value, str) for value in task.values()):
        raise ValueError("task fields must be strings")
    repository = task["repository"]
    if not _REPOSITORY.fullmatch(repository) or repository.endswith(".git"):
        raise ValueError("repository must be a canonical lowercase key")
    if not _TOKEN.fullmatch(task["task"]) or not _TOKEN.fullmatch(task["provider"]):
        raise ValueError("invalid task or provider token")
    if task["provider"] not in _PROVIDERS:
        raise ValueError("provider must use a recognized canonical token")
    if task["access"] not in {"read", "write"}:
        raise ValueError("access must be read or write")


def evaluate(candidate: dict, roster: dict) -> dict:
    """Apply issue 3829's Boolean conflict rule to validated input records.

    Non-Codex writers still require the existing path-ownership controls.
    Reusing a task token does not exempt an active writer from exclusion.
    """
    validate_task(candidate)
    if not isinstance(roster, dict) or set(roster) != {"complete", "active"}:
        raise ValueError("invalid roster fields")
    if type(roster["complete"]) is not bool or not isinstance(roster["active"], list):
        raise ValueError("invalid roster types")
    for active in roster["active"]:
        validate_task(active)
    if not roster["complete"]:
        return {"allowed": False, "status": "NOT_EVALUATED", "blockers": []}
    blockers = [
        active["task"]
        for active in roster["active"]
        if candidate["repository"] == active["repository"]
        and candidate["access"] == active["access"] == "write"
        and "codex" in {candidate["provider"], active["provider"]}
    ]
    return {
        "allowed": not blockers,
        "status": "BLOCKED" if blockers else "ALLOWED",
        "blockers": blockers,
    }


def unique_object(pairs: list) -> dict:
    """Reject duplicate keys before JSON parsing can discard evidence."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main() -> int:
    """Return zero for admission, one for conflict, two for missing evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--roster", type=Path, required=True)
    args = parser.parse_args()
    try:
        candidate = json.loads(
            args.candidate.read_text(encoding="utf-8"), object_pairs_hook=unique_object
        )
        roster = json.loads(
            args.roster.read_text(encoding="utf-8"), object_pairs_hook=unique_object
        )
        result = evaluate(candidate, roster)
    except (OSError, ValueError, RecursionError):
        # Input paths and parser excerpts may contain private information.
        result = {"allowed": False, "status": "NOT_EVALUATED", "blockers": []}
    print(json.dumps(result, sort_keys=True))
    return {"ALLOWED": 0, "BLOCKED": 1, "NOT_EVALUATED": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
