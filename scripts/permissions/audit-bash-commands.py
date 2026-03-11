"""
audit-bash-commands.py — WRK-1119 Phase 1

Read historical Claude session JSONL files, extract every Bash tool-use command,
normalise to a prefix token, count frequency, and emit a ranked YAML allow-list.

Usage:
    uv run --no-project python audit-bash-commands.py [--sessions-dir PATH] [--output PATH]

Defaults:
    --sessions-dir  ~/.claude/projects/
    --output        stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Multi-word prefix table — order matters: longest match wins
# ---------------------------------------------------------------------------
_MULTI_WORD_PREFIXES: tuple[tuple[str, ...], ...] = (
    ("git", "diff"),
    ("git", "log"),
    ("git", "add"),
    ("git", "commit"),
    ("git", "push"),
    ("git", "pull"),
    ("git", "fetch"),
    ("git", "checkout"),
    ("git", "status"),
    ("git", "rebase"),
    ("git", "merge"),
    ("git", "stash"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "reset"),
    ("git", "tag"),
    ("git", "cherry-pick"),
    ("git", "rev-parse"),
    ("git", "rev-list"),
    ("git", "hash-object"),
    ("git", "update-index"),
    ("git", "write-tree"),
    ("git", "commit-tree"),
    ("git", "update-ref"),
    ("uv", "run"),
    ("uv", "tool"),
    ("uv", "add"),
    ("uv", "sync"),
    ("python", "-m"),
    ("python3", "-m"),
)

# Commands that never take positional arguments — omit the wildcard suffix
_NO_ARG_COMMANDS: frozenset[str] = frozenset({"pwd"})


# ---------------------------------------------------------------------------
# Core functions (imported by tests)
# ---------------------------------------------------------------------------


def _iter_tool_use_items(obj: object) -> Iterator[dict]:
    """Yield every tool_use item reachable from an arbitrary parsed JSON object."""
    if not isinstance(obj, dict):
        return
    # Flat format: the object itself is a tool_use
    if obj.get("type") == "tool_use":
        yield obj
        return
    # Nested inside message.content
    message = obj.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    yield item


def extract_bash_commands(session_file: Path) -> list[str]:
    """Return all Bash tool-use command strings found in *session_file* (JSONL)."""
    commands: list[str] = []
    try:
        with session_file.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for item in _iter_tool_use_items(obj):
                    if item.get("name") == "Bash":
                        cmd = (item.get("input") or {}).get("command")
                        if cmd and isinstance(cmd, str):
                            commands.append(cmd)
    except OSError:
        pass
    return commands


def normalize_command_to_prefix(command: str) -> str:
    """Normalise a raw Bash command string to a canonical prefix token."""
    command = command.strip()
    if not command:
        return command

    tokens = command.split()
    # Absolute or relative paths — keep the path token up to first space
    first_token = tokens[0]
    if first_token.startswith("./") or first_token.startswith("/"):
        return first_token

    # Check multi-word prefix table (longest match wins; table is pre-sorted longest first)
    for prefix_words in _MULTI_WORD_PREFIXES:
        n = len(prefix_words)
        if len(tokens) >= n and tuple(tokens[:n]) == prefix_words:
            return " ".join(prefix_words)

    # Fallback: single first word
    return tokens[0]


def suggest_allow_pattern(prefix: str) -> str:
    """Return the Claude settings allow pattern for *prefix*."""
    if not prefix:
        raise ValueError("prefix cannot be empty")

    # Relative-path scripts map to a wildcard pattern
    if prefix.startswith("./scripts/") or prefix.startswith("./"):
        # Use the directory glob: ./scripts/*:*
        parts = prefix.split("/")
        if len(parts) >= 2:
            wildcard = "/".join(parts[:-1]) + "/*"
            return f"Bash({wildcard}:*)"

    # Commands that take no positional arguments
    if prefix in _NO_ARG_COMMANDS:
        return f"Bash({prefix})"

    return f"Bash({prefix}:*)"


# ---------------------------------------------------------------------------
# YAML output helpers (stdlib only — no PyYAML required)
# ---------------------------------------------------------------------------


def _yaml_str(value: str) -> str:
    """Minimally safe YAML scalar: quote if it contains special chars.

    Multi-line values (heredocs, embedded newlines) are truncated at the first
    newline so the scalar stays on a single YAML line.
    """
    # Truncate at first newline/carriage-return/null — keeps YAML valid
    for sep in ("\n", "\r", "\0"):
        idx = value.find(sep)
        if idx != -1:
            value = value[:idx]
    need_quote = any(c in value for c in ('"', "'", ":", "#", "{", "}", "[", "]", ","))
    if need_quote:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def _emit_yaml(records: list[dict]) -> str:
    """Format *records* as a YAML list (stdlib, no PyYAML dependency)."""
    lines: list[str] = []
    for rec in records:
        lines.append(f"- prefix: {_yaml_str(rec['prefix'])}")
        lines.append(f"  count: {rec['count']}")
        lines.append(f"  example_command: {_yaml_str(rec['example_command'])}")
        lines.append(f"  suggested_allow_pattern: {_yaml_str(rec['suggested_allow_pattern'])}")
    return "\n".join(lines) + ("\n" if lines else "")


# ---------------------------------------------------------------------------
# Main audit logic
# ---------------------------------------------------------------------------


def run_audit(sessions_dir: Path) -> list[dict]:
    """Scan *sessions_dir* recursively; return sorted records (highest count first)."""
    prefix_counts: dict[str, int] = defaultdict(int)
    prefix_examples: dict[str, str] = {}

    for jsonl_file in sessions_dir.rglob("*.jsonl"):
        for cmd in extract_bash_commands(jsonl_file):
            prefix = normalize_command_to_prefix(cmd)
            if not prefix:
                continue
            prefix_counts[prefix] += 1
            if prefix not in prefix_examples:
                prefix_examples[prefix] = cmd

    records = [
        {
            "prefix": prefix,
            "count": count,
            "example_command": prefix_examples[prefix],
            "suggested_allow_pattern": suggest_allow_pattern(prefix),
        }
        for prefix, count in sorted(prefix_counts.items(), key=lambda x: -x[1])
    ]
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit Bash commands from Claude session JSONL files."
    )
    parser.add_argument(
        "--sessions-dir",
        type=Path,
        default=Path.home() / ".claude" / "projects",
        help="Root directory containing session JSONL files (recursive scan).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write YAML output to this file (default: stdout).",
    )
    args = parser.parse_args(argv)

    sessions_dir: Path = args.sessions_dir
    if not sessions_dir.exists():
        print(f"ERROR: sessions-dir does not exist: {sessions_dir}", file=sys.stderr)
        return 1

    records = run_audit(sessions_dir)
    yaml_output = _emit_yaml(records)

    if args.output:
        args.output.write_text(yaml_output, encoding="utf-8")
    else:
        sys.stdout.write(yaml_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
