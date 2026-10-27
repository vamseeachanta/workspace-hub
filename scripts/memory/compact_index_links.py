#!/usr/bin/env python3
"""Shorten index annotations without evicting entries or writing files.

Policy basis: issue #3366 requires keeping all entries while shortening hooks.
The caller supplies a UTF-8 byte budget; this module sets no policy threshold.
Existing declarations remain in compact-memory.py (_triggers_met, line counts)
and scripts/enforcement/check-memory-index-size.sh (byte-size guard).

Recognized entries are Markdown list items beginning with an inline link and
followed by `` — ``. Link spelling, separator and line ending are mandatory;
only the subsequent annotation can shrink. Balanced or escaped brackets and
parentheses are accepted. Metadata, HTML blocks, fenced/indented code and annotations
with further link-like syntax are immutable. A cannot-fit result retains the
entire original input, even when it exceeds the requested budget.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Literal, NamedTuple

# CommonMark list/fence indentation is at most three spaces; ordered markers
# contain one to nine digits. See https://spec.commonmark.org/0.31.2/#list-items
# and https://spec.commonmark.org/0.31.2/#fenced-code-blocks for these grammar
# bounds. These patterns recognize a conservative subset, not all Markdown.
_LIST = re.compile(r" {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]+(?=\[)")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)$")
_HTML_LITERAL = re.compile(r" {0,3}<(script|pre|style|textarea)(?:[ \t>]|$)", re.I)
_SEPARATOR = " — "


class ShortenResult(NamedTuple):
    """Pure result; minimum_bytes includes all immutable syntax and content."""

    text: str
    status: Literal["unchanged", "shortened", "cannot-fit"]
    original_bytes: int
    output_bytes: int
    minimum_bytes: int


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    """Find the position after a balanced group, respecting backslash escapes."""
    depth = 0
    escaped = False
    quote = ""
    angle = False
    for position in range(start, len(text)):
        char = text[position]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote:
            if char == quote:
                quote = ""
        elif angle:
            if char == ">":
                angle = False
        elif opening == "(" and char in ("'", '"'):
            quote = char
        elif opening == "(" and char == "<":
            angle = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return position + 1
    return None


def _entry_parts(line: str) -> tuple[str, str, str]:
    """Return immutable prefix, removable annotation and immutable line ending."""
    body = line.rstrip("\r\n")
    ending = line[len(body):]
    match = _LIST.match(body)
    if match:
        label_end = _balanced_end(body, match.end(), "[", "]")
        if label_end is not None and body[label_end:label_end + 1] == "(":
            link_end = _balanced_end(body, label_end, "(", ")")
            if link_end is not None and body.startswith(_SEPARATOR, link_end):
                annotation_start = link_end + len(_SEPARATOR)
                annotation = body[annotation_start:]
                # Preserve reference links, images, autolinks and bare URLs too.
                # Ambiguity costs compaction capacity, never discoverability.
                if not any(token in annotation for token in ("[", "]", "<", ">", "://")):
                    return body[:annotation_start], annotation, ending
    return line, "", ""


def _parts(text: str) -> list[tuple[str, str, str]]:
    parts = []
    fence_char = ""
    fence_length = 0
    metadata = text.startswith(("---\n", "---\r\n"))
    html_until = ""
    html_block = False
    for position, line in enumerate(text.splitlines(keepends=True)):
        body = line.rstrip("\r\n")
        if metadata:
            parts.append((line, "", ""))
            if position and body in ("---", "..."):
                metadata = False
            continue
        if html_until:
            parts.append((line, "", ""))
            if html_until in body.lower():
                html_until = ""
            continue
        if html_block:
            parts.append((line, "", ""))
            if not body.strip():
                html_block = False
            continue
        fence = _FENCE.fullmatch(body)
        if fence_char:
            parts.append((line, "", ""))
            if (fence and fence[1][0] == fence_char
                    and len(fence[1]) >= fence_length and not fence[2].strip()):
                fence_char = ""
        elif fence:
            fence_char = fence[1][0]
            fence_length = len(fence[1])
            parts.append((line, "", ""))
        elif body.lstrip().startswith("<"):
            # Conservatively retain HTML blocks (CommonMark, #html-blocks).
            # Literal blocks can contain blank lines; other tags end at a blank.
            literal = _HTML_LITERAL.match(body)
            if body.lstrip().startswith("<!--"):
                html_until = "-->"
            elif literal:
                html_until = "</" + literal[1].lower() + ">"
            else:
                html_block = True
            if html_until in body.lower():
                html_until = ""
            parts.append((line, "", ""))
        else:
            parts.append(_entry_parts(line))
    return parts


def _prefix(annotation: bytes, cap: int) -> str:
    # The input was encoded from valid text. Only a final partial UTF-8 character
    # can be discarded by ignore; complete characters retain their exact bytes.
    return annotation[:cap].decode("utf-8", errors="ignore")


def shorten_index(text: str, byte_budget: int) -> ShortenResult:
    """Fit annotation prefixes to a byte budget, or return the original intact.

    A shared annotation byte cap is chosen by binary search. Short annotations
    retain their text, while longer ones receive the same cap. Prefixes end on
    Unicode character boundaries; a few bytes may remain unused. No ellipsis is
    inserted. UTF-8 encoding must be valid; the budget must be a nonnegative int.
    This function performs no I/O and never changes its input.
    """
    if isinstance(byte_budget, bool) or not isinstance(byte_budget, int):
        raise TypeError("byte_budget must be a nonnegative integer")
    if byte_budget < 0:
        raise ValueError("byte_budget must be a nonnegative integer")

    original_bytes = len(text.encode("utf-8"))
    parts = _parts(text)
    annotations = [annotation.encode("utf-8") for _, annotation, _ in parts]
    minimum_bytes = original_bytes - sum(map(len, annotations))
    if original_bytes <= byte_budget:
        return ShortenResult(text, "unchanged", original_bytes, original_bytes, minimum_bytes)
    if minimum_bytes > byte_budget:
        return ShortenResult(text, "cannot-fit", original_bytes, original_bytes, minimum_bytes)

    available = byte_budget - minimum_bytes
    low = 0
    high = max(map(len, annotations), default=0)
    while low < high:
        # Upper midpoint ensures progress when the bounds differ by one.
        midpoint = (low + high + 1) // 2
        used = sum(len(_prefix(annotation, midpoint).encode("utf-8"))
                   for annotation in annotations)
        if used <= available:
            low = midpoint
        else:
            high = midpoint - 1
    shortened = "".join(prefix + _prefix(annotation, low) + ending
                        for (prefix, _, ending), annotation in zip(parts, annotations))
    return ShortenResult(shortened, "shortened", original_bytes,
                         len(shortened.encode("utf-8")), minimum_bytes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path, help="UTF-8 index to preview")
    parser.add_argument("--byte-budget", type=int, required=True, help="Maximum UTF-8 bytes")
    parser.add_argument("--dry-run", action="store_true", required=True,
                        help="Print a JSON preview; no files are written")
    args = parser.parse_args(argv)
    if args.byte_budget < 0:
        parser.error("--byte-budget must be nonnegative")
    try:
        # read_bytes avoids universal-newline conversion of preserved CRLF text.
        text = args.index.read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        parser.error("cannot read index as UTF-8")
    result = shorten_index(text, args.byte_budget)
    print(json.dumps(result._asdict(), ensure_ascii=False))
    return 1 if result.status == "cannot-fit" else 0


if __name__ == "__main__":
    sys.exit(main())
