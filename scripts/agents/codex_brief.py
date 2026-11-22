"""Validate and render bounded briefs; never dispatch or execute their commands.

Contract source: issue 3828, Fix/workaround (explicit scope, non-destructive
constraints, owned paths). This is preparation, not an access-control boundary.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

FIELDS = {"objective", "scope", "owned_files", "checks", "stop_conditions"}
CONSTRAINTS = """## Preservation constraints
- Modify only the listed owned files within the assigned repository.
- Treat owned files as proposed scope, not authorization beyond the task request.
- Do not delete data, overwrite unrelated work, or clean unknown files.
- Do not rewrite history, reset branches, or change Git configuration.
- Do not publish, push, merge, deploy, or change access controls.
- Do not modify runtime permissions or approval settings.
- Inspect effective permissions and repository instructions before acting.
- Stop and report missing authority, conflicting work, or required scope expansion.
- Run the listed checks and report failures and unverified results explicitly.
- A brief is not a filesystem sandbox; independent runtime controls still apply.
"""


def _text(value: object) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and all(char.isprintable() for char in value))


def _owned_file(value: str) -> bool:
    """Allow exact portable relative file names, never traversal or glob scope."""
    path = PurePosixPath(value)
    return (not path.is_absolute() and value == path.as_posix()
            and not any(part.casefold() in {".", "..", ".git"}
                        or part.endswith((".", " ")) for part in path.parts)
            and bool(path.parts) and not value.startswith("~")
            and not re.search(r'[\\:*?\[\]<>"|]', value))


def validate_brief(value: object) -> dict:
    """Reject incomplete or ambiguous scope without echoing input values."""
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("expected exactly objective, scope, owned_files, checks, stop_conditions")
    if not _text(value["objective"]):
        raise ValueError("objective must be nonempty single-line text")
    for field in sorted(FIELDS - {"objective"}):
        items = value[field]
        if not isinstance(items, list) or not items or not all(_text(item) for item in items):
            raise ValueError(f"{field} must be a nonempty list of single-line text")
    paths = value["owned_files"]
    if len(set(paths)) != len(paths) or not all(_owned_file(path) for path in paths):
        raise ValueError("owned_files must contain unique exact repository-relative file names")
    return value


def render_brief(value: object) -> str:
    """Render only after complete validation; check commands remain literal text."""
    brief = validate_brief(value)
    sections = ["# Bounded Codex brief", "## Objective\n" + brief["objective"]]
    for field, heading in [("scope", "Scope"), ("owned_files", "Owned files"),
                           ("checks", "Verification"), ("stop_conditions", "Stop conditions")]:
        sections.append(f"## {heading}\n" + "\n".join(f"- {item}" for item in brief[field]))
    sections.append(CONSTRAINTS.rstrip())
    return "\n\n".join(sections) + "\n"


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path, help="JSON brief to validate and render to stdout")
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.brief.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        output = render_brief(value)
    except (OSError, UnicodeError, ValueError):
        print("Invalid brief: unreadable JSON or incomplete bounded-brief contract.", file=sys.stderr)
        return 1
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
