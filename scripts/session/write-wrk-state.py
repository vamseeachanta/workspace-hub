"""
ABOUTME: Update WRK item YAML frontmatter with session_state block
ABOUTME: Reads WRK file, parses frontmatter, writes session_state, preserves body
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter from a Markdown file.

    Returns (frontmatter_dict, body_text). If no frontmatter is found,
    returns ({}, full content).
    """
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    raw_yaml = match.group(1)
    body = content[match.end():]
    try:
        data = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as exc:
        print(f"WARNING: Could not parse frontmatter YAML: {exc}", file=sys.stderr)
        data = {}
    return data, body


def render_frontmatter(data: dict) -> str:
    """Serialize a dict back to YAML frontmatter block."""
    return "---\n" + yaml.dump(data, default_flow_style=False, allow_unicode=True) + "---\n"


def build_session_state(
    last_updated: str,
    progress_notes: str,
    modified_files: list[str],
    next_steps: list[str],
    recent_commits: str,
) -> dict[str, Any]:
    """Construct the session_state mapping to embed in frontmatter."""
    return {
        "last_updated": last_updated,
        "progress_notes": progress_notes.strip() or "No notes captured.",
        "modified_files": [f for f in modified_files if f],
        "next_steps": [s for s in next_steps if s],
        "recent_commits": recent_commits.strip(),
    }


def write_state(
    wrk_path: str,
    last_updated: str,
    progress_notes: str,
    modified_files: list[str],
    next_steps: list[str],
    recent_commits: str,
) -> None:
    """
    Read a WRK item file, update its session_state frontmatter block, write back.

    Preserves all existing frontmatter keys. The session_state block is
    replaced entirely on each call so it stays current.
    """
    path = Path(wrk_path)
    if not path.exists():
        raise FileNotFoundError(f"WRK file not found: {wrk_path}")

    content = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    session_state = build_session_state(
        last_updated=last_updated,
        progress_notes=progress_notes,
        modified_files=modified_files,
        next_steps=next_steps,
        recent_commits=recent_commits,
    )
    frontmatter["session_state"] = session_state

    new_content = render_frontmatter(frontmatter) + body
    path.write_text(new_content, encoding="utf-8")
    print(f"session_state written to {wrk_path}")


def parse_csv_arg(value: str) -> list[str]:
    """Split a comma-separated argument into a stripped list, ignoring blanks."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_newline_arg(value: str) -> list[str]:
    """Split a newline-separated argument into a stripped list, ignoring blanks."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update WRK item YAML frontmatter with session_state."
    )
    parser.add_argument("--wrk-path", required=True, help="Path to the WRK .md file")
    parser.add_argument(
        "--last-updated",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        help="ISO-8601 timestamp (default: now UTC)",
    )
    parser.add_argument(
        "--progress-notes",
        default="",
        help="Free-form progress notes for this session",
    )
    parser.add_argument(
        "--modified-files",
        default="",
        help="Comma-separated list of modified file paths",
    )
    parser.add_argument(
        "--next-steps",
        default="",
        help="Newline-separated list of next action items",
    )
    parser.add_argument(
        "--recent-commits",
        default="",
        help="Recent git log lines (informational)",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    modified_files = parse_csv_arg(args.modified_files)
    next_steps = parse_newline_arg(args.next_steps)

    write_state(
        wrk_path=args.wrk_path,
        last_updated=args.last_updated,
        progress_notes=args.progress_notes,
        modified_files=modified_files,
        next_steps=next_steps,
        recent_commits=args.recent_commits,
    )


if __name__ == "__main__":
    main()
