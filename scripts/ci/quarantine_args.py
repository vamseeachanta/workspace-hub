"""Build the original workflow's quarantine arguments (issue #4227).

Preserve order, comments, xargs-style whitespace/quotes, and both prefix forms.
As with the original `while read` loop, an unterminated final line is ignored.
"""

import argparse
import shlex
import sys
from pathlib import Path


def build_args(path: Path) -> list[str]:
    if not path.is_file():
        return []
    args = []
    with path.open(encoding="utf-8", newline="") as source:
        for raw in source:
            if not raw.endswith("\n"):
                continue
            line = raw.partition("#")[0]
            try:
                lexer = shlex.shlex(line, posix=True)
                lexer.whitespace = " \t\n"  # xargs retains carriage returns in node-ids.
                # xargs treats backslashes literally inside either quote style.
                lexer.escapedquotes = ""
                lexer.whitespace_split = True
                lexer.commenters = ""
                line = " ".join(lexer)
            except ValueError:
                # The original xargs command fails to emit an unmatched quote.
                continue
            if not line:
                continue
            alternate = line.removeprefix("tests/") if line.startswith("tests/") else f"tests/{line}"
            args.extend(["--deselect", line, "--deselect", alternate])
    return args


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quarantine_file", type=Path)
    parser.add_argument("--null", action="store_true", help="Emit NUL-delimited array elements.")
    options = parser.parse_args()
    args = build_args(options.quarantine_file)
    if options.null:
        for argument in args:
            sys.stdout.write(argument + "\0")
    elif args:
        print(" ".join(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
