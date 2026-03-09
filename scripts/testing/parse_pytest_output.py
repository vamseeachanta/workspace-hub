"""Parse pytest stdout + exit code into a structured JSONL record.

Called by run-all-tests.sh for each repo. Reads raw pytest output from stdin
(or a file), combines with the process exit code, and emits one JSON record.

Pytest exit codes:
  0 = all tests passed (or no failures)
  1 = some tests failed
  2 = interrupted (Ctrl-C, timeout, collection error)
  3 = internal error
  4 = CLI usage error
  5 = no tests collected

Usage (from shell):
  python parse_pytest_output.py <repo> <exit_code> [<expected-failures-file>] < output.txt

Output: one JSON line to stdout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ── public API ────────────────────────────────────────────────────────────────

def parse_summary(raw_output: str) -> dict[str, int]:
    """Extract passed/failed/error/skipped counts from pytest summary line.

    Returns a dict with zero-defaulted counts when no summary line is found
    (e.g. collection errors, import errors, or interrupted runs).
    """
    counts: dict[str, int] = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
    # Match the final summary line: "N passed, M failed, ..." (order varies)
    # Each token is optional; only the number before the keyword is captured.
    pattern = re.compile(
        r"(\d+)\s+(passed|failed|error|skipped|warning|xfailed|xpassed)"
    )
    for line in reversed(raw_output.splitlines()):
        # The summary line always ends with " in X.XXs"
        if re.search(r"\bin\s+[\d.]+s\b", line):
            for m in pattern.finditer(line):
                n, label = int(m.group(1)), m.group(2)
                if label in counts:
                    counts[label] = n
            return counts
    return counts


def parse_failed_node_ids(raw_output: str) -> set[str]:
    """Extract failed/errored test node IDs from verbose pytest output.

    Matches lines like:
      FAILED tests/test_foo.py::TestBar::test_baz - AssertionError
      FAILED tests/test_foo.py::test_baz[a-b]
      ERROR  tests/test_foo.py::TestBar::test_setup - TypeError

    Preserves full node IDs including parameterized suffixes (e.g. [a-b]).
    """
    node_ids: set[str] = set()
    # Match FAILED or ERROR; capture up to the first " - " separator or EOL
    pattern = re.compile(r"^(?:FAILED|ERROR)\s+([^\s].*?)(?:\s+-\s+|\s*$)", re.MULTILINE)
    for m in pattern.finditer(raw_output):
        node_id = m.group(1).strip()
        if node_id:
            node_ids.add(node_id)
    return node_ids


def load_expected_failures(path: Path | None) -> set[str]:
    """Load exact node IDs from expected-failures.txt (one per line, # comments)."""
    if path is None or not path.exists():
        return set()
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            result.add(stripped)
    return result


def build_record(
    repo: str,
    exit_code: int,
    raw_output: str,
    failed_node_ids: set[str],
    expected_failures: set[str],
) -> dict:
    """Build a structured result dict for one repo run."""
    counts = parse_summary(raw_output)

    # Determine status from exit code first
    if exit_code == 5:
        status = "no_tests"
    elif exit_code in (2, 3, 4):
        status = "error"
    elif exit_code == 0:
        status = "ok"
    else:
        # exit_code == 1 (or any other): classify by unexpected failures
        unexpected = failed_node_ids - expected_failures
        expected_hit = failed_node_ids & expected_failures
        status = "unexpected_failures" if unexpected else "ok"
        return {
            "repo": repo,
            "exit_code": exit_code,
            "status": status,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "error": counts["error"],
            "skipped": counts["skipped"],
            "unexpected": len(unexpected),
            "expected_fail": len(expected_hit),
            "unexpected_ids": sorted(unexpected),
        }

    unexpected = failed_node_ids - expected_failures
    expected_hit = failed_node_ids & expected_failures

    return {
        "repo": repo,
        "exit_code": exit_code,
        "status": status,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "error": counts["error"],
        "skipped": counts["skipped"],
        "unexpected": len(unexpected),
        "expected_fail": len(expected_hit),
        "unexpected_ids": sorted(unexpected),
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: parse_pytest_output.py <repo> <exit_code> [<expected-failures-file>]",
            file=sys.stderr,
        )
        return 1

    repo = sys.argv[1]
    try:
        exit_code = int(sys.argv[2])
    except ValueError:
        print(f"Error: exit_code must be integer, got {sys.argv[2]!r}", file=sys.stderr)
        return 1

    ef_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else None
    expected_failures = load_expected_failures(ef_path)

    raw_output = sys.stdin.read()
    failed_node_ids = parse_failed_node_ids(raw_output)

    record = build_record(
        repo=repo,
        exit_code=exit_code,
        raw_output=raw_output,
        failed_node_ids=failed_node_ids,
        expected_failures=expected_failures,
    )
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
