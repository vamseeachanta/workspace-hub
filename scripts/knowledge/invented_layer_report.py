#!/usr/bin/env python3
"""Report GUARD-1 vocabulary in explicitly supplied Markdown, without rewriting.

Authority: docs/document-intelligence/pyramid-conformance-checks.md Section 5.6
and its scoping note; parent operating model Section 2, Forbidden inventions.
Only the cited regex vocabulary is detected; semantic classification is manual.

API: scan_text(text, file="input.md") or scan_files(paths, root=...).
CLI: python scripts/knowledge/invented_layer_report.py --root . docs/example.md
Output is a JSON list of relative file, original one-based line and rule fields,
with one diagnostic per matching line. Files are sorted and deduplicated.
Exit success means the report was produced, including when findings exist;
usage and input errors use argparse's usage-error status. No implicit discovery.

This is a scoped Markdown scanner, not a general Markdown renderer. It handles
backtick spans, backtick/tilde fences, block quotes, paired inline quotations,
inline/reference links and URLs. Unmatched inline delimiters remain prose;
inline quotations are line-local so stray quotes cannot hide later prose.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath


POLICY_FILE = "docs/document-intelligence/pyramid-conformance-checks.md"
# Literal patterns and case from Section 5.6; do not extend the vocabulary here.
FORBIDDEN = re.compile(
    r"\bL[0-9]+-adjacent\b|\bbetween L[0-9]+ and L[0-9]+\b|\bhybrid layer\b"
)
# Markdown fence/indent syntax follows CommonMark, Fenced code blocks and
# Indented code blocks (https://spec.commonmark.org/0.31.2/).
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
REFERENCE = re.compile(
    r"^ {0,3}\[([^]\n]+)\]:[ \t]*(?:<[^<>\n]+>|[^\s<>]+)"
    r'''(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*$''', re.M
)
URL = re.compile(r"<https?://[^>\n]*>|(?:https?://|www\.)[^\s<>]+")
QUOTATION = re.compile(
    r'(?<!\w)"[^"\n]*"|(?<!\w)\'(?!\s)[^\'\n]*\'(?!\w)|“[^”\n]*”|‘[^’\n]*’'
)


def _blank(text: str) -> str:
    """Preserve newlines and token boundaries while suppressing examples."""
    return re.sub(r"[^\r\n]", " ", text)


def _relative_file(file: str) -> str:
    path = PurePosixPath(file)
    if (
        not file or path.is_absolute() or ".." in path.parts
        or "\\" in file or re.match(r"^[A-Za-z]:", file)
    ):
        raise ValueError("source must be a relative file path without parent traversal")
    return path.as_posix()


def _definition_row(line: str, file: str, section: str, subsection: str) -> bool:
    """Only the named policy's definition and relevant revision rows are exempt."""
    if file != POLICY_FILE or not line.lstrip().startswith("|"):
        return False
    # Cell indices follow the policy's pipe-delimited tables, including the
    # empty cell before the opening pipe. Labels are narrower than whole tables.
    cells = line.split("|")
    label = cells[1].strip()
    if subsection == "5.6 Child Guardrail Checks":
        return label == "GUARD-1"
    if section == "12. Revision History":
        if subsection == section:
            return (
                label == "2026-04-19" and len(cells) > 2
                and cells[2].strip().startswith("Parent amendment")
            )
        if subsection == "Amendment-driver detail (2026-04-19)":
            return label.startswith(("A — Remove invented", "B — Strengthen GUARD-1"))
    return False


def _blocks(text: str, file: str) -> str:
    fence = None
    section = subsection = ""
    lines = []
    for line in text.splitlines(keepends=True):
        marker = FENCE.match(line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                if not marker[2].strip():
                    fence = None
            lines.append(_blank(line))
            continue
        if marker and not (marker[1].startswith("`") and "`" in marker[2]):
            fence = marker[1]
            lines.append(_blank(line))
            continue
        if re.match(r"^ {0,3}>", line) or line.startswith(("    ", "\t")):
            lines.append(_blank(line))
            continue
        heading = HEADING.match(line)
        if heading:
            # ATX levels follow CommonMark; H2 sections contain H3 subsections.
            level = len(heading[1])
            if level <= 2:
                section = subsection = heading[2]
            elif level == 3:
                subsection = heading[2]
        lines.append(_blank(line) if _definition_row(line, file, section, subsection) else line)
    return "".join(lines)


def _inline_code(text: str) -> str:
    """Match exact backtick run lengths, including code spans across lines."""
    # A blank line ends a Markdown paragraph. Blanked fenced blocks therefore
    # cannot let unmatched backticks suppress a later paragraph's prose.
    return "".join(
        _code_spans(part) for part in re.split(r"(\n[ \t\r]*\n)", text)
    )


def _code_spans(text: str) -> str:
    runs = []
    cursor = 0
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2  # backslash and the escaped character (CommonMark escapes)
            continue
        run = re.match(r"`+", text[cursor:]) if text[cursor] == "`" else None
        if run:
            # Escapes have no meaning inside a code span. Its closing run may
            # therefore follow a backslash; search for it in the original text.
            opening_end = cursor + run.end()
            closing = next(
                (m for m in re.finditer(r"`+", text[opening_end:]) if m[0] == run[0]), None
            )
            if closing:
                end = opening_end + closing.end()
                runs.append((cursor, end))
                cursor = end
                continue
            cursor = opening_end
        else:
            cursor += 1
    parts = []
    cursor = 0
    for start, end in runs:
        parts.extend((text[cursor:start], _blank(text[start:end])))
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    """Return the end of a bracket/parenthesis span, respecting escapes."""
    depth = 0
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if char == "\n" and re.match(r"\n[ \t\r]*\n", text[cursor:]):
            return None
        if char == "\\":
            cursor += len(text[cursor:cursor + 2])  # escaped Markdown character
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if not depth:
                return cursor + 1
        cursor += 1
    return None


def _links(text: str) -> str:
    references = {" ".join(m[1].split()).casefold() for m in REFERENCE.finditer(text)}
    text = REFERENCE.sub(lambda match: _blank(match[0]), text)
    parts = []
    cursor = index = 0
    while index < len(text):
        if text[index] == "\\":
            index += len(text[index:index + 2])
            continue
        if text[index] != "[":
            index += 1
            continue
        label_end = _balanced_end(text, index, "[", "]")
        if label_end is None:
            index += 1
            continue
        end = None
        if text[label_end:label_end + 1] == "(":
            end = _balanced_end(text, label_end, "(", ")")
        elif text[label_end:label_end + 1] == "[":
            ref_end = _balanced_end(text, label_end, "[", "]")
            if ref_end is not None:
                ref = text[label_end + 1:ref_end - 1] or text[index + 1:label_end - 1]
                if " ".join(ref.split()).casefold() in references:
                    end = ref_end
        elif " ".join(text[index + 1:label_end - 1].split()).casefold() in references:
            end = label_end
        if end is None:
            index += 1
            continue
        parts.extend((text[cursor:index], _blank(text[index:end])))
        cursor = index = end
    parts.append(text[cursor:])
    return URL.sub(lambda match: _blank(match[0]), "".join(parts))


def scan_text(text: str, file: str = "input.md") -> list[dict]:
    """Return GUARD-1 findings in free prose with the original line numbers."""
    file = _relative_file(file)
    prose = _links(_inline_code(_blocks(text, file)))
    prose = QUOTATION.sub(lambda match: _blank(match[0]), prose)
    return [
        {"file": file, "line": number, "rule": "GUARD-1"}
        for number, line in enumerate(prose.splitlines(), start=1)
        if FORBIDDEN.search(line)
    ]


def scan_files(paths, *, root: Path) -> list[dict]:
    """Read only explicit Markdown files inside root; never recurse or rewrite."""
    root = Path(root).resolve()
    supplied = {}
    for supplied_path in paths:
        path = Path(supplied_path).resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            raise ValueError("input must be inside the explicit root") from None
        if path.suffix.lower() != ".md" or not path.is_file():
            raise ValueError("input must be a readable Markdown file")
        supplied[relative] = path
    return [
        finding
        for relative, path in sorted(supplied.items())
        for finding in scan_text(path.read_text(encoding="utf-8"), relative)
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="explicit Markdown files")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="relative-report root")
    args = parser.parse_args(argv)
    try:
        report = scan_files(args.paths, root=args.root)
    except (OSError, UnicodeError, ValueError):
        # Never expose absolute input paths or source content through errors.
        parser.error("inputs must be readable UTF-8 Markdown files inside the explicit root")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
