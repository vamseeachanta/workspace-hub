#!/usr/bin/env python3
"""Aggregate explicit failure evidence from normalized JSONL records (issue #1880).

Input contract: each line is an object with a nonblank string ``session_id``.
``failure_category`` may be absent/null (unknown), or exactly ``tool_error``,
``git_conflict`` or ``timeout``. Other values/types reject the entire record.
Extra fields are ignored; transcript text is never used to infer a failure.
The category vocabulary follows the failure-mode requirement in issue #1880.
The session key follows the existing declaration in
``.claude/skills/coordination/session-corpus-audit/SKILL.md``.

Counts use record cardinality and distinct-session set cardinality, with no
policy thresholds. Each category counts affected sessions, not failure events;
categories can overlap. Duplicate input lines count as accepted records but
cannot inflate session or category totals. A session without any supported
explicit failure evidence stays unknown, even when Stop records are present.

Tool-call totals and TDD compliance remain null (unknown). Neither is inferred
from Stop events or accepted-record counts. Unlike the line-count approach in
``scripts/analysis/weekly-trends.py:compute_session_metrics``, repeated records
do not stand in for distinct sessions here. This does not modify that metric.

Only aggregate counts and unknown values are emitted. This bounded slice does
not discover logs, adapt native formats, establish global identity namespaces,
score TDD, apply churn thresholds or publish weekly reports. Callers must supply
normalized records with consistent identities across the input file.

Usage: python scripts/analysis/session_corpus_summary.py INPUT.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Iterator
from pathlib import Path


FAILURE_CATEGORIES = ("tool_error", "git_conflict", "timeout")


def summarize(records: Iterable[object]) -> dict[str, object]:
    """Return aggregates without mutating records or retaining source text.

    Invalid objects, missing/invalid identities and invalid categories each
    contribute one rejected record and no session or failure evidence. Missing
    failure evidence is valid input, not proof that no failure occurred.
    """
    sessions: set[str] = set()
    failures: dict[str, set[str]] = {category: set() for category in FAILURE_CATEGORIES}
    accepted = rejected = 0
    for record in records:
        if not isinstance(record, dict):
            rejected += 1
            continue
        identity = record.get("session_id")
        category = record.get("failure_category")
        if (
            not isinstance(identity, str)
            or not identity.strip()
            or (category is not None and (
                not isinstance(category, str) or category not in FAILURE_CATEGORIES
            ))
        ):
            rejected += 1
            continue
        accepted += 1
        sessions.add(identity)
        if category is not None:
            failures[category].add(identity)

    known_failures = set().union(*failures.values())
    return {
        "accepted_records": accepted,
        "rejected_records": rejected,
        "sessions": len(sessions),
        "failure_sessions_by_category": {
            category: len(identities) for category, identities in failures.items()
        },
        "sessions_without_failure_evidence": len(sessions - known_failures),
        "tool_calls": None,
        "tdd_compliance": None,
    }


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("nonstandard JSON constant")


def parse_jsonl(lines: Iterable[str | bytes]) -> Iterator[object]:
    """Decode each physical line; yield an invalid sentinel for decoding errors.

    Blank lines, invalid UTF-8, duplicate keys and nonstandard JSON constants
    are rejected individually. No source text or parse diagnostic is emitted.
    """
    for line in lines:
        try:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            yield json.loads(
                line, object_pairs_hook=_unique_object, parse_constant=_reject_constant,
            )
        except (ValueError, UnicodeError, RecursionError):
            yield None


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="session-corpus-summary",
        description="Summarize explicit failure categories as aggregate JSON counts.",
    )
    parser.add_argument("input", type=Path, help="normalized JSONL input file")
    args = parser.parse_args()
    try:
        with args.input.open("rb") as source:
            result = summarize(parse_jsonl(source))
    except OSError:
        parser.error("unable to read input")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
