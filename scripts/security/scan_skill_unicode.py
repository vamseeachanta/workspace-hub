#!/usr/bin/env python3
"""Opt-in, read-only reports of named hidden controls in explicit UTF-8 files.

Usage: python scripts/security/scan_skill_unicode.py [--] FILE [FILE ...]

The character-name basis is Python unicodedata (Unicode Character Database):
Bidi_Control characters and the selected zero-width Cf (Other, Format) names
listed below. This is a bounded character report, not a maliciousness or
severity classification. Joiners and directional marks can be intentional.
Other invisible characters and other security heuristics are outside its scope.

Each occurrence yields one JSON line containing only path, line, and rule.
Paths are JSON-escaped; source text and exception details are never emitted.
Lines count physical LF, CRLF, or CR terminators, starting at one; Unicode line
separators do not increment the locator. Findings go to stdout; input errors go
to stderr with a null line. Arguments and character occurrences retain order.
No directories are traversed and no files are written.

Exit status contract: 0 = report complete (including findings), 1 = at least
one unreadable/non-UTF-8 input, 2 = invalid arguments. Findings are report only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import TextIO
import unicodedata


# Unicode character names from unicodedata; these bidi controls have the
# Unicode Bidi_Control property. No numerical range or severity threshold is
# used. The zero-width set is explicitly selected rather than all Cf characters.
CONTROL_NAMES = {
    "BIDI_CONTROL": (
        "ARABIC LETTER MARK",
        "LEFT-TO-RIGHT MARK",
        "RIGHT-TO-LEFT MARK",
        "LEFT-TO-RIGHT EMBEDDING",
        "RIGHT-TO-LEFT EMBEDDING",
        "POP DIRECTIONAL FORMATTING",
        "LEFT-TO-RIGHT OVERRIDE",
        "RIGHT-TO-LEFT OVERRIDE",
        "LEFT-TO-RIGHT ISOLATE",
        "RIGHT-TO-LEFT ISOLATE",
        "FIRST STRONG ISOLATE",
        "POP DIRECTIONAL ISOLATE",
    ),
    "ZERO_WIDTH_FORMAT": (
        "ZERO WIDTH SPACE",
        "ZERO WIDTH NON-JOINER",
        "ZERO WIDTH JOINER",
        "WORD JOINER",
        "ZERO WIDTH NO-BREAK SPACE",
    ),
}
CONTROL_RULES = {
    unicodedata.lookup(name): f"{group}:{name}"
    for group, names in CONTROL_NAMES.items()
    for name in names
}


def report(path: str | None, line: int | None, rule: str, stream: TextIO) -> None:
    """Emit only locator/rule information, escaping untrusted path characters."""
    print(json.dumps({"path": path, "line": line, "rule": rule}, ensure_ascii=True), file=stream)


class ReportArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        """Do not reflect untrusted arguments in parser diagnostics."""
        report(None, None, "INVALID_ARGUMENTS", sys.stderr)
        # CLI contract: two denotes a usage error, following argparse.
        raise SystemExit(2)


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Read an explicit regular file; return one finding per named control."""
    if not path.is_file():
        raise OSError
    findings = []
    # Strict UTF-8 preserves a BOM as ZERO WIDTH NO-BREAK SPACE. Default universal
    # newline handling maps LF/CRLF/CR to physical lines without treating Unicode
    # LINE SEPARATOR or PARAGRAPH SEPARATOR as an extra source line.
    with path.open(encoding="utf-8") as source:
        # Physical line locators start at one, as documented in the CLI contract.
        for line_number, line in enumerate(source, start=1):
            for character in line:
                rule = CONTROL_RULES.get(character)
                if rule is not None:
                    findings.append((line_number, rule))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = ReportArgumentParser(
        prog="scan_skill_unicode.py",
        description="Scan explicit UTF-8 files for named hidden Unicode controls; report only.",
        epilog="Exit status: 0 report complete; 1 input failure; 2 invalid arguments.",
        allow_abbrev=False,
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="explicit file paths; use -- before option-like paths")
    arguments = parser.parse_args(argv)
    # Exit statuses follow the documented CLI contract; findings alone succeed.
    status = 0
    for filename in arguments.files:
        try:
            findings = scan_file(Path(filename))
        except UnicodeError:
            report(filename, None, "INPUT_NOT_UTF8", sys.stderr)
            status = 1
        except OSError:
            report(filename, None, "INPUT_UNREADABLE", sys.stderr)
            status = 1
        else:
            for line, rule in findings:
                report(filename, line, rule, sys.stdout)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
