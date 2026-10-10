#!/usr/bin/env python3
"""Flag shell test helpers that a selector can leave undefined (#3876).

Defect class: a helper function is defined only in a conditional scope and
called outside it. A targeted run that skips the scope calls an undefined
function; inside ``$(...)`` the failure is easy to lose and the harness
reports green without checking anything.

Conditional scopes: ``if``/``case``/loop bodies, a definition behind ``&&`` or
``||`` (including a brace group there), another function's body, and a
subshell ``( ... )``. A helper is treated as defined after an ``if`` block when
it is defined in every branch of ``if ... else ... fi``, or by the
``if ! declare -F <fn>; then <fn>() {...}; fi`` idiom.

A finding is a call outside the defining scope with no earlier guard. A guard
is ``declare -F <fn>`` / ``declare -f <fn>`` / ``require_helpers <fn>`` that
(a) is acted on — followed on its command line by ``||`` other than
``|| true`` / ``|| :``, or used as an ``if``/``elif`` condition — and (b) sits
at top level or in a scope that encloses the call, outside the defining scope.

Calls are words in command position, including inside ``$(...)``, backticks,
after ``NAME=value`` prefixes and ``command``, and the command argument of
``run_step``. Known limitations: calls inside unquoted heredoc bodies, names
passed to other wrappers, and nested quotes inside ``${...}`` are not parsed;
a ``case`` defining the helper in every arm is still reported.

Usage:
  check-shell-conditional-helpers.py [PATH...]

With no PATH, scans every tracked shell test harness in this repository
(``*.sh`` under a ``test``/``tests`` directory, or named ``test_*``/``test-*``).
Exit 0 = clean, 1 = findings, 2 = usage or I/O error.

Rule: .claude/rules/shell-test-helper-guards.md
Runtime guards: scripts/lib/shell-test-guards.sh
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from shell_scope_parser import Frame, Guard, analyse

REPO_ROOT = Path(__file__).resolve().parents[2]


def _inside(line: int, order: int, frame: Frame) -> bool:
    start = (frame.start, frame.start_order)
    end = (frame.end or frame.start, frame.end_order or frame.start_order)
    return start <= (line, order) <= end


def _inside_branch(line: int, order: int, frame: Frame, branch: int) -> bool:
    start = frame.branch_starts.get(branch, (frame.start, frame.start_order))
    default_end = (frame.end or frame.start, frame.end_order or frame.start_order)
    end = frame.branch_ends.get(branch, default_end)
    return start <= (line, order) <= end


def _guarded(line: int, order: int, guards: list[Guard], regions: list[Frame]) -> bool:
    return any(
        g.acted
        and (g.line, g.order) < (line, order)
        and not any(_inside(g.line, g.order, f) for f in regions)
        and (g.frame is None or _inside(line, order, g.frame))
        and (
            g.branch is None
            or g.frame is None
            or _inside_branch(line, order, g.frame, g.branch)
        )
        for g in guards
    )


def find_issues(text: str) -> list[tuple[int, str, Frame]]:
    defs, guards, refs = analyse(text)
    unconditional = {d.name for d in defs if d.frame is None}
    regions: dict[str, list[Frame]] = {}
    for d in defs:
        if d.frame is not None and d.name not in unconditional:
            regions.setdefault(d.name, []).append(d.frame)
    issues = []
    for name, line, order in refs:
        frames = regions.get(name)
        if not frames or any(_inside(line, order, f) for f in frames):
            continue
        if not _guarded(line, order, guards.get(name, []), frames):
            issues.append((line, name, frames[0]))
    return issues


def tracked_harnesses() -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", "*.sh"],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8", "replace")
    paths = []
    for rel in filter(None, out.split("\0")):
        parts = Path(rel).parts
        if any(p in ("test", "tests") for p in parts[:-1]) or parts[-1].startswith(
            ("test_", "test-")
        ):
            paths.append(Path(rel))
    return paths


def _targets(argv: list[str]) -> tuple[list[Path], Path | None]:
    if argv:
        return [Path(a) for a in argv], None
    return tracked_harnesses(), REPO_ROOT


def main(argv: list[str]) -> int:
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    try:
        targets, base = _targets(argv)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(
            f"check-shell-conditional-helpers: git ls-files failed: {exc}",
            file=sys.stderr,
        )
        return 2
    total = 0
    for target in targets:
        try:
            text = ((base / target) if base else target).read_text(
                encoding="utf-8", errors="replace"
            )
        except OSError as exc:
            print(
                f"check-shell-conditional-helpers: cannot read {target}: {exc}",
                file=sys.stderr,
            )
            return 2
        for line, name, frame in find_issues(text):
            total += 1
            print(
                f"{target.as_posix()}:{line}: helper '{name}' is defined only inside the "
                f"{frame.kind} scope at lines {frame.start}-{frame.end} and is called here "
                f"without an earlier, reachable `declare -F {name} || ...` or "
                f"`require_helpers {name} || ...` guard"
            )
    print(
        f"check-shell-conditional-helpers: scanned {len(targets)} file(s), {total} finding(s)"
    )
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
