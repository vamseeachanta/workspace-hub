#!/usr/bin/env python3
"""Flag shell test helpers that a selector can leave undefined (#3876).

Defect class: a helper function is defined only inside a conditional block
(``if``/``case``/loop body) and called after that block. A targeted run that
skips the block calls an undefined function; inside ``$(...)`` the failure is
easy to lose and the harness reports green without checking anything.

A finding is a call to such a helper outside its defining block with no
earlier ``declare -F <fn>`` / ``declare -f <fn>`` / ``require_helpers <fn>``
guard outside that block. A helper is treated as defined after its block when
it is defined in every branch of an ``if ... else ... fi``, or by the
``if ! declare -F <fn>; then <fn>() {...}; fi`` idiom.

Usage:
  check-shell-conditional-helpers.py [PATH...]

With no PATH, scans every tracked shell test harness in this repository
(``*.sh`` under a ``test``/``tests`` directory, or named ``test_*``/``test-*``).
Exit 0 = clean, 1 = findings, 2 = usage or I/O error.

Rule: .claude/rules/shell-test-helper-guards.md
Runtime guards: scripts/lib/shell-test-guards.sh
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.-]*$")
TOKEN_RE = re.compile(r";;|&&|\|\||[;&|(){}]|[^\s;&|(){}]+")
HEREDOC_RE = re.compile(r"(?<!<)<<(?!<)(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
SEPARATORS = {";", ";;", "&&", "||", "|", "&", "(", ")", "{", "}"}
COMMAND_PREFIX_WORDS = {
    "then",
    "do",
    "else",
    "elif",
    "if",
    "while",
    "until",
    "!",
    "time",
}
CLOSERS = {"fi", "esac", "done"}
GUARD_WORDS = {"require_helpers"}


@dataclass
class Frame:
    kind: str  # if | case | loop
    start: int
    end: int | None = None
    branch: int = 0
    has_else: bool = False
    ensures: str | None = None  # name from ``if ! declare -F <name>``
    parent: Frame | None = None
    defs: dict[str, set[int]] = field(default_factory=dict)  # name -> branches


@dataclass
class Definition:
    name: str
    line: int
    frame: Frame | None  # None = unconditional


class Sanitizer:
    """Blank out quoted literals and comments, keep command substitutions.

    The context stack persists across lines so multi-line strings and
    substitutions are handled. Each entry is ``[kind, paren_depth]``.
    """

    def __init__(self) -> None:
        self.stack: list[list] = [["code", 0]]

    @property
    def at_top_level(self) -> bool:
        return len(self.stack) == 1

    def line(self, raw: str) -> str:
        out: list[str] = []
        i = 0
        while i is not None and i < len(raw):
            kind = self.stack[-1][0]
            if kind == "sq":
                i = self._single(raw, i)
            elif kind == "dq":
                i = self._double(raw, i, out)
            else:
                i = self._code(raw, i, out)
        return "".join(out)

    def _single(self, raw: str, i: int) -> int:
        if raw[i] == "'":
            self.stack.pop()
        return i + 1

    def _double(self, raw: str, i: int, out: list[str]) -> int:
        ch, nxt = raw[i], raw[i + 1 : i + 2]
        if ch == "\\":
            return i + 2
        if ch == '"':
            self.stack.pop()
        elif ch == "$" and nxt == "(":
            self.stack.append(["code", 0])
            out.append(" ( ")
            return i + 2
        elif ch == "$" and nxt == "{":
            return self._skip_param(raw, i + 2)
        return i + 1

    def _code(self, raw: str, i: int, out: list[str]) -> int | None:
        ch, nxt = raw[i], raw[i + 1 : i + 2]
        ctx = self.stack[-1]
        if ch == "\\":
            return i + 2
        if ch in "'\"":
            self.stack.append(["sq" if ch == "'" else "dq", 0])
            out.append("S")
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t;&|("):
            return None  # comment runs to end of line
        elif ch == "$" and nxt == "{":
            out.append("V")
            return self._skip_param(raw, i + 2)
        elif ch == "$" and nxt == "(":
            self.stack.append(["code", 0])
            out.append(" ( ")
            return i + 2
        elif ch == "(" and not self.at_top_level:
            ctx[1] += 1
            out.append(" ( ")
        elif ch == ")" and not self.at_top_level:
            if ctx[1] == 0:
                self.stack.pop()
            else:
                ctx[1] -= 1
            out.append(" ) ")
        elif ch in "()":
            out.append(f" {ch} ")
        else:
            out.append(ch)
        return i + 1

    @staticmethod
    def _skip_param(raw: str, i: int) -> int:
        depth = 1
        while i < len(raw) and depth:
            depth += {"{": 1, "}": -1}.get(raw[i], 0)
            i += 1
        return i


class Analyser:
    """Collect helper definitions, guards and command-position references."""

    def __init__(self) -> None:
        self.sanitizer = Sanitizer()
        self.stack: list[Frame] = []
        self.frames: list[Frame] = []
        self.defs: list[Definition] = []
        self.guards: dict[str, list[int]] = {}
        self.refs: list[tuple[str, int]] = []
        self.heredoc: tuple[str, bool] | None = None

    def run(self, text: str) -> Analyser:
        lines = text.splitlines()
        for lineno, raw in enumerate(lines, start=1):
            self._line(lineno, raw)
        for frame in self.frames:
            if frame.end is None:
                frame.end = len(lines)
        return self

    def _line(self, lineno: int, raw: str) -> None:
        if self.heredoc is not None:
            term, strip_tabs = self.heredoc
            if (raw.lstrip("\t") if strip_tabs else raw).strip() == term:
                self.heredoc = None
            return
        top_level = self.sanitizer.at_top_level
        clean = self.sanitizer.line(raw)
        if top_level and "<<" in clean:
            # The terminator word may be quoted, so read it from the raw line.
            match = HEREDOC_RE.search(raw)
            if match:
                self.heredoc = (match.group(3), match.group(1) == "-")
        tokens = TOKEN_RE.findall(clean)
        cmd_start, i = True, 0
        while i < len(tokens):
            if tokens[i] in SEPARATORS:
                cmd_start, i = True, i + 1
            elif not cmd_start:
                i += 1
            else:
                cmd_start, i = self._command_word(tokens, i, lineno)

    def _command_word(self, tokens: list[str], i: int, lineno: int) -> tuple[bool, int]:
        """Handle the word at command position; return (cmd_start, next index)."""
        tok = tokens[i]
        if tok in ("if", "case", "do"):
            self._open(tok, tokens[i + 1 : i + 5], lineno)
            return tok != "case", i + 1
        if tok in CLOSERS:
            self._close(lineno)
            return False, i + 1
        if tok in ("else", "elif"):
            if self.stack and self.stack[-1].kind == "if":
                self.stack[-1].branch += 1
                self.stack[-1].has_else |= tok == "else"
            return True, i + 1
        if tok in COMMAND_PREFIX_WORDS:
            return True, i + 1
        if tok == "function" and i + 1 < len(tokens) and NAME_RE.match(tokens[i + 1]):
            self._define(tokens[i + 1], lineno)
            i += 2
            return True, i + 2 if tokens[i : i + 2] == ["(", ")"] else i
        if NAME_RE.match(tok) and tokens[i + 1 : i + 3] == ["(", ")"]:
            self._define(tok, lineno)
            return True, i + 3
        self._simple_command(tokens, i, lineno)
        return False, i + 1

    def _simple_command(self, tokens: list[str], i: int, lineno: int) -> None:
        tok = tokens[i]
        if tok in ("declare", "typeset") and tokens[i + 1 : i + 2] in (["-F"], ["-f"]):
            if i + 2 < len(tokens):
                self.guards.setdefault(tokens[i + 2], []).append(lineno)
        elif tok in GUARD_WORDS:
            for name in tokens[i + 1 :]:
                if name in SEPARATORS:
                    break
                self.guards.setdefault(name, []).append(lineno)
        elif NAME_RE.match(tok):
            self.refs.append((tok, lineno))

    def _open(self, tok: str, cond: list[str], lineno: int) -> None:
        kind = "loop" if tok == "do" else tok
        frame = Frame(kind, lineno, parent=self.stack[-1] if self.stack else None)
        if (
            kind == "if"
            and len(cond) == 4
            and cond[:3] in (["!", "declare", "-F"], ["!", "declare", "-f"])
        ):
            frame.ensures = cond[3]
        self.stack.append(frame)
        self.frames.append(frame)

    def _close(self, lineno: int) -> None:
        if not self.stack:
            return
        frame = self.stack.pop()
        frame.end = lineno
        self._promote(frame)

    def _define(self, name: str, lineno: int) -> None:
        frame = self.stack[-1] if self.stack else None
        self.defs.append(Definition(name, lineno, frame))
        if frame is not None:
            frame.defs.setdefault(name, set()).add(frame.branch)

    def _promote(self, frame: Frame) -> None:
        """Promote names an if-block guarantees to its parent block."""
        if frame.kind != "if":
            return
        branches = set(range(frame.branch + 1))
        for name, seen in frame.defs.items():
            covered = frame.has_else and seen == branches
            if not covered and not (name == frame.ensures and 0 in seen):
                continue
            parent = frame.parent
            self.defs.append(Definition(name, frame.end or frame.start, parent))
            if parent is not None:
                parent.defs.setdefault(name, set()).add(parent.branch)


def analyse(
    text: str,
) -> tuple[list[Definition], dict[str, list[int]], list[tuple[str, int]]]:
    """Return (definitions, guard lines per name, command-position references)."""
    result = Analyser().run(text)
    return result.defs, result.guards, result.refs


def _inside(line: int, frame: Frame) -> bool:
    return frame.start <= line <= (frame.end or frame.start)


def find_issues(text: str) -> list[tuple[int, str, Frame]]:
    defs, guards, refs = analyse(text)
    unconditional = {d.name for d in defs if d.frame is None}
    regions: dict[str, list[Frame]] = {}
    for d in defs:
        if d.frame is not None and d.name not in unconditional:
            regions.setdefault(d.name, []).append(d.frame)
    issues = []
    for name, line in refs:
        frames = regions.get(name)
        if not frames or any(_inside(line, f) for f in frames):
            continue
        guarded = any(
            g < line and not any(_inside(g, f) for f in frames)
            for g in guards.get(name, [])
        )
        if not guarded:
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
                f"{frame.kind} block at lines {frame.start}-{frame.end} and is called here "
                f"without an earlier `declare -F {name}` or `require_helpers {name}` guard"
            )
    print(
        f"check-shell-conditional-helpers: scanned {len(targets)} file(s), {total} finding(s)"
    )
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
