#!/usr/bin/env python3
"""Merge two machine-specific permission audit YAMLs into a single ranked list.

Usage:
    uv run --no-project python scripts/permissions/merge-audit-results.py \\
        --dev-primary PATH --dev-secondary PATH --settings PATH \\
        --output PATH [--threshold N]
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML parsing (stdlib fallback when PyYAML is absent)
# ---------------------------------------------------------------------------

def _load_yaml_manual(path: Path) -> list[dict]:
    """Minimal parser for the known audit-YAML list-of-mappings format.

    Used instead of PyYAML when the file contains invalid YAML escape sequences
    (e.g. unescaped backslash-pipe ``\\|`` inside double-quoted strings).
    """
    records: list[dict] = []
    current: dict = {}
    with open(path) as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")
            # New record starts with "- prefix:"
            if line.startswith("- prefix:"):
                if current:
                    records.append(current)
                value = line[len("- prefix:"):].strip()
                current = {"prefix": value.strip("\"'")}
            elif line.startswith("  count:"):
                value = line[len("  count:"):].strip()
                try:
                    current["count"] = int(value)
                except ValueError:
                    current["count"] = 0
            elif line.startswith("  example_command:"):
                value = line[len("  example_command:"):].strip()
                current["example_command"] = value.strip("\"'")
            elif line.startswith("  suggested_allow_pattern:"):
                value = line[len("  suggested_allow_pattern:"):].strip()
                current["suggested_allow_pattern"] = value.strip("\"'")
    if current:
        records.append(current)
    return records


try:
    import yaml  # type: ignore

    def _load_yaml(path: Path) -> list[dict]:
        """Load audit YAML, falling back to manual parser on scan errors."""
        try:
            with open(path) as fh:
                return yaml.safe_load(fh) or []
        except yaml.YAMLError:
            # File likely contains invalid escape sequences in double-quoted
            # strings (e.g. \| from shell regexes). Use the manual parser.
            return _load_yaml_manual(path)

except ImportError:

    def _load_yaml(path: Path) -> list[dict]:  # type: ignore[misc]
        return _load_yaml_manual(path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Prefixes that are dangerous or noise regardless of count
_BLOCKED_PREFIXES = {"#", "sleep", "eval", "sudo"}

# Deny patterns from settings already cover these tools
_DENIED_TOOLS = {"curl", "wget", "rm -rf /", "chmod 777", "git push --force"}


def load_settings_patterns(settings_path: Path) -> tuple[set[str], set[str]]:
    """Return (allow_patterns, deny_patterns) from .claude/settings.json."""
    with open(settings_path) as fh:
        data = json.load(fh)
    perms = data.get("permissions", {})
    allows = set(perms.get("allow", []))
    denies = set(perms.get("deny", []))
    return allows, denies


def merge_records(
    records_1: list[dict], records_2: list[dict]
) -> dict[str, dict]:
    """Merge records from two machines, summing counts by prefix."""
    merged: dict[str, dict] = {}
    for record in records_1 + records_2:
        prefix = record.get("prefix", "").strip()
        if not prefix:
            continue
        count = record.get("count", 0)
        example = record.get("example_command", "")
        pattern = record.get("suggested_allow_pattern", f'Bash({prefix}:*)')
        if prefix not in merged:
            merged[prefix] = {
                "prefix": prefix,
                "count": count,
                "example_command": example,
                "suggested_allow_pattern": pattern,
            }
        else:
            merged[prefix]["count"] += count
            # Keep the longer / more descriptive example
            if len(example) > len(merged[prefix]["example_command"]):
                merged[prefix]["example_command"] = example
    return merged


def is_blocked(prefix: str, pattern: str) -> bool:
    """Return True if this prefix should be excluded from suggestions."""
    if prefix in _BLOCKED_PREFIXES:
        return True
    for denied_tool in _DENIED_TOOLS:
        if prefix.startswith(denied_tool):
            return True
    return False


def classify_records(
    merged: dict[str, dict],
    allow_patterns: set[str],
    deny_patterns: set[str],
    threshold: int,
) -> tuple[list[dict], list[dict]]:
    """Split merged records into already_covered and suggested_additions."""
    already_covered: list[dict] = []
    suggested_additions: list[dict] = []

    for record in sorted(merged.values(), key=lambda r: r["count"], reverse=True):
        prefix = record["prefix"]
        count = record["count"]
        pattern = record["suggested_allow_pattern"]

        if count < threshold:
            continue

        if is_blocked(prefix, pattern):
            continue

        if pattern in allow_patterns:
            already_covered.append({"prefix": prefix, "count": count, "pattern": pattern})
            continue

        if pattern in deny_patterns:
            # Explicitly denied — skip silently (dangerous)
            continue

        suggested_additions.append({
            "prefix": prefix,
            "count": count,
            "suggested_allow_pattern": pattern,
            "example_command": record["example_command"],
        })

    return already_covered, suggested_additions


def write_output(
    output_path: Path,
    already_covered: list[dict],
    suggested_additions: list[dict],
    threshold: int,
) -> None:
    """Write the two-section YAML output file."""
    lines: list[str] = []
    lines.append("# Permission audit merge — WRK-1119")
    lines.append(f"# threshold: {threshold} (minimum combined count)")
    lines.append("")

    lines.append(f"already_covered:  # {len(already_covered)} patterns")
    if already_covered:
        for item in already_covered:
            lines.append(f"  - prefix: {item['prefix']}")
            lines.append(f"    count: {item['count']}")
            lines.append(f"    pattern: \"{item['pattern']}\"")
    else:
        lines.append("  []")

    lines.append("")
    lines.append(f"suggested_additions:  # {len(suggested_additions)} patterns")
    if suggested_additions:
        for item in suggested_additions:
            example = item["example_command"].replace('"', "'")
            lines.append(f"  - prefix: {item['prefix']}")
            lines.append(f"    count: {item['count']}")
            lines.append(f"    suggested_allow_pattern: \"{item['suggested_allow_pattern']}\"")
            lines.append(f"    example_command: \"{example}\"")
    else:
        lines.append("  []")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev-primary", required=True, metavar="PATH")
    parser.add_argument("--dev-secondary", required=True, metavar="PATH")
    parser.add_argument("--settings", required=True, metavar="PATH")
    parser.add_argument("--output", required=True, metavar="PATH")
    parser.add_argument("--threshold", type=int, default=5, metavar="N")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    path_1 = Path(args.dev_primary)
    path_2 = Path(args.dev_secondary)
    settings_path = Path(args.settings)
    output_path = Path(args.output)

    for p in (path_1, path_2, settings_path):
        if not p.exists():
            print(f"ERROR: file not found: {p}", file=sys.stderr)
            return 1

    records_1 = _load_yaml(path_1)
    records_2 = _load_yaml(path_2)
    allow_patterns, deny_patterns = load_settings_patterns(settings_path)

    merged = merge_records(records_1, records_2)
    already_covered, suggested_additions = classify_records(
        merged, allow_patterns, deny_patterns, args.threshold
    )

    write_output(output_path, already_covered, suggested_additions, args.threshold)

    total_unique = len(merged)
    below_threshold = sum(
        1 for r in merged.values() if r["count"] < args.threshold
    )
    print(
        f"Merged {len(records_1)} + {len(records_2)} records → "
        f"{total_unique} unique prefixes"
    )
    print(f"  Below threshold ({args.threshold}): {below_threshold} skipped")
    print(f"  Already covered: {len(already_covered)}")
    print(f"  Suggested additions: {len(suggested_additions)}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
