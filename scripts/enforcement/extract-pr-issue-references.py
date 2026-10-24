#!/usr/bin/env python3
"""Extract issue references from a pull request event.

Bare ``#N`` references are resolved against the current repository. Qualified
``owner/repo#N`` references and full GitHub issue URLs carry their own
repository. Pull request URLs are deliberately ignored.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.safe_cli import SafeArgumentParser

ISSUE_URL_RE = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)"
    r"(?=$|[/?#)\s.,;:])"
)
QUALIFIED_RE = re.compile(
    r"(?<![\w/.-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)\b"
)
BARE_RE = re.compile(r"(?<![\w/-])#([1-9][0-9]*)\b")


def _read_event(path: str | None) -> str:
    if path == "-":
        return sys.stdin.read()
    if path:
        return Path(path).read_text()
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("ERROR: GITHUB_EVENT_PATH is not set and no event file was supplied")
    return Path(event_path).read_text()


def _event_text(raw: str) -> str:
    event = json.loads(raw)
    pr = event.get("pull_request", {})
    return "\n".join(str(pr.get(key) or "") for key in ("title", "body"))


def extract_references(text: str, default_repo: str) -> list[str]:
    if not default_repo:
        raise ValueError("default repository is required for bare #N references")

    matches: list[tuple[int, str, str]] = []
    for match in ISSUE_URL_RE.finditer(text):
        matches.append((match.start(), match.group(1), match.group(2)))
    for match in QUALIFIED_RE.finditer(text):
        matches.append((match.start(), match.group(1), match.group(2)))
    for match in BARE_RE.finditer(text):
        matches.append((match.start(), default_repo, match.group(1)))

    seen: set[tuple[str, str]] = set()
    references: list[str] = []
    for _, repo, number in sorted(matches, key=lambda item: item[0]):
        key = (repo, number)
        if key in seen:
            continue
        seen.add(key)
        references.append(f"{repo}#{number}")
    return references


def main(argv: list[str] | None = None) -> int:
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument("event_file", nargs="?", help="GitHub event JSON file, or '-' for stdin")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="repository for bare #N references (default: GITHUB_REPOSITORY)",
    )
    args = parser.parse_args(argv)

    try:
        references = extract_references(_event_text(_read_event(args.event_file)), args.repo)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not extract issue references: {exc}", file=sys.stderr)
        return 1

    print(" ".join(references))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
