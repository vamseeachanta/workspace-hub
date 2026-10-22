"""Account for an explicit context observation without reading transcripts.

Basis: issue #3717, 'Measured, not estimated' (2026); schema and arithmetic
are documented in docs/standards/BOUNDED_TOOL_OUTPUT.md. No tokenizer estimate,
provider invocation, default window size or universal acceptance limit is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "source", "window_tokens", "harness_tokens", "message_tokens", "tool_output_tokens",
}
OPTIONAL = {"auto_loaded_prose_tokens"}


def _count(value: object) -> int:
    # The schema defines counts as nonnegative integers; booleans are not counts.
    if type(value) is not int or value < 0:
        raise ValueError("token counts must be nonnegative integers")
    return value


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _percent(part: int, whole: int) -> float:
    # Definition of percent: 100 parts per whole. One decimal is display only;
    # all consistency checks use unrounded counts. See the documented method.
    return round(part / whole * 100, 1)


def summarize(observation: object) -> dict:
    """Validate disjoint totals, then compute window shares and deletion bounds."""
    if not isinstance(observation, dict):
        raise TypeError("observation must be an object")
    if not REQUIRED <= observation.keys() or observation.keys() - REQUIRED - OPTIONAL:
        raise ValueError("missing or unknown observation fields")
    if not _text(observation["source"]):
        raise ValueError("source must be nonempty text")
    window = _count(observation["window_tokens"])
    if window == 0:
        raise ValueError("window must be positive")
    components = observation["harness_tokens"]
    if not isinstance(components, dict) or not components:
        raise ValueError("harness must be a nonempty component object")
    if not all(_text(name) for name in components):
        raise ValueError("component names must be nonempty text")
    harness = sum(_count(value) for value in components.values())
    messages = _count(observation["message_tokens"])
    tools = _count(observation["tool_output_tokens"])
    # #3717 nests Bash results within messages; never add them to messages again.
    if tools > messages or harness + messages > window:
        raise ValueError("inconsistent context totals")
    saving = {"status": "NOT_EVALUATED", "reason": "auto-loaded prose not measured"}
    if "auto_loaded_prose_tokens" in observation:
        prose = _count(observation["auto_loaded_prose_tokens"])
        if prose > harness:
            raise ValueError("auto-loaded prose exceeds harness total")
        saving = {"status": "EVALUATED", "upper_bound_window_pct": _percent(prose, window)}
    return {
        "source": observation["source"],
        "window_tokens": window,
        "harness_tokens": harness,
        "harness_window_pct": _percent(harness, window),
        "message_window_pct": _percent(messages, window),
        "tool_output_window_pct": _percent(tools, window),
        "tool_to_harness_ratio": round(tools / harness, 1) if harness else None,
        "accounted_tokens": harness + messages,
        "unaccounted_window_tokens": window - harness - messages,
        "prose_saving": saving,
    }


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate field")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation", type=Path, help="JSON observation, not a transcript")
    args = parser.parse_args(argv)
    try:
        raw = args.observation.read_text(encoding="utf-8")
    except OSError:
        parser.error("cannot read context observation")
    except UnicodeError:
        parser.error("invalid context observation; expected UTF-8 JSON")
    try:
        result = summarize(json.loads(raw, object_pairs_hook=_unique_object))
    except (TypeError, ValueError):
        # Do not echo payloads or filesystem locations in diagnostics.
        parser.error("invalid context observation; see the documented schema")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
