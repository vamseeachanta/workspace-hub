"""Scope-aware shell parser for check-shell-conditional-helpers.py (#3876).

Tracks where shell functions are defined (if/case/loop bodies, && / || lists,
function bodies, subshells), where guards for them sit, and which words are
called in command position. Line-oriented and deliberately small: it is a
lint for test harnesses, not a full shell grammar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

try:
    from shell_sanitizer import Sanitizer
except ModuleNotFoundError:
    from scripts.enforcement.shell_sanitizer import Sanitizer

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.-]*$")
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^]]*\])?\+?=")
TOKEN_RE = re.compile(r";;|&&|\|\||[;&|(){}]|[^\s;&|(){}]+")
HEREDOC_RE = re.compile(
    r"(?<!<)<<(?!<)(-?)\s*(?:'([^']*)'|\"([^\"]*)\"|\\?([^\s;&|<>()'\"]+))"
)
TRAILING_OP_RE = re.compile(r"(&&|\|\||\|)\s*$")
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
    "command",
}
CLOSERS = {"fi", "esac", "done"}
GUARD_WORDS = {"require_helpers"}
BRACE_KINDS = {"brace", "function", "list"}
NO_OP_ACTIONS = {"true", ":"}


def strip_shell_comment(raw: str) -> str:
    """Remove lexical shell comments for continuation detection."""
    quote: str | None = None
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\":
            i += 2
            continue
        if quote:
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote = ch
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t;&|("):
            return raw[:i].rstrip()
        i += 1
    return raw.rstrip()


@dataclass
class Frame:
    kind: str  # if | case | loop | function | list | subshell | brace
    start: int
    end: int | None = None
    start_order: int = 0
    end_order: int | None = None
    branch: int = 0
    has_else: bool = False
    ensures: str | None = None  # name from ``if ! declare -F <name>``
    parent: Frame | None = None  # nearest enclosing scope (never a plain brace)
    defs: dict[str, set[int]] = field(default_factory=dict)  # name -> branches
    branch_starts: dict[int, tuple[int, int]] = field(default_factory=dict)
    branch_ends: dict[int, tuple[int, int]] = field(default_factory=dict)

    @property
    def transparent(self) -> bool:
        """A plain ``{ ...; }`` group does not make its contents conditional."""
        return self.kind == "brace"


@dataclass
class Definition:
    name: str
    line: int
    order: int
    frame: Frame | None  # None = unconditional


@dataclass
class Guard:
    line: int
    order: int
    frame: Frame | None
    acted: bool
    branch: int | None = None


class Analyser:
    """Collect helper definitions, guards and command-position references."""

    def __init__(self) -> None:
        self.sanitizer = Sanitizer()
        self.stack: list[Frame] = []
        self.frames: list[Frame] = []
        self.defs: list[Definition] = []
        self.guards: dict[str, list[Guard]] = {}
        self.refs: list[tuple[str, int, int]] = []
        self.heredoc: tuple[str, bool] | None = None
        self.in_list = False  # after && / || on the current command line
        self.pending_body = False  # a definition's body has not opened yet
        self.command_order = 0
        self.current_order = 0

    def run(self, text: str) -> Analyser:
        lines = text.splitlines()
        pending, first = "", 0
        for lineno, raw in enumerate(lines, start=1):
            if self.heredoc is not None:
                self._heredoc_line(raw)
                continue
            code = strip_shell_comment(raw)
            if pending and not code.strip():
                continue
            if code.endswith("\\") and not code.endswith("\\\\"):
                pending, first = pending + code[:-1] + " ", first or lineno
                continue
            if TRAILING_OP_RE.search(code):
                # A line ending in && / || / | continues the command list.
                pending, first = pending + code + " ", first or lineno
                continue
            self._line(first or lineno, pending + raw)
            pending, first = "", 0
        if pending:
            self._line(first, pending)
        for frame in self.frames:
            if frame.end is None:
                frame.end = len(lines)
            if frame.end_order is None:
                frame.end_order = self.command_order
        return self

    def _heredoc_line(self, raw: str) -> None:
        term, strip_tabs = self.heredoc
        if (raw.lstrip("\t") if strip_tabs else raw).strip() == term:
            self.heredoc = None

    def _line(self, lineno: int, raw: str) -> None:
        top_level = self.sanitizer.at_top_level
        clean = self.sanitizer.line(raw)
        if top_level and "<<" in clean:
            # The terminator word may be quoted, so read it from the raw line.
            match = HEREDOC_RE.search(raw)
            if match:
                term = next(g for g in match.groups()[1:] if g is not None)
                self.heredoc = (term, match.group(1) == "-")
        tokens = TOKEN_RE.findall(clean)
        cmd_start, i, self.in_list = True, 0, False
        while i < len(tokens):
            if tokens[i] in SEPARATORS:
                self._separator(tokens[i], lineno)
                cmd_start, i = True, i + 1
            elif not cmd_start:
                i += 1
            else:
                cmd_start, i = self._command_word(tokens, i, lineno)

    def _separator(self, tok: str, lineno: int) -> None:
        if tok in ("&&", "||"):
            self.in_list = True
        elif tok in (";", ";;", "&", "|"):
            self.in_list = False
        elif tok == "{":
            kind = (
                "function" if self.pending_body else "list" if self.in_list else "brace"
            )
            self._push(kind, lineno)
        elif tok == "(":
            self._push("subshell", lineno)
        elif tok in ("}", ")") and self.stack:
            closes = BRACE_KINDS if tok == "}" else {"subshell"}
            if self.stack[-1].kind in closes:
                self._close(lineno)
        if tok in ("{", "("):
            self.pending_body = False

    def _command_word(self, tokens: list[str], i: int, lineno: int) -> tuple[bool, int]:
        """Handle the word at command position; return (cmd_start, next index)."""
        self.command_order += 1
        self.current_order = self.command_order
        tok = tokens[i]
        if tok in ("if", "case", "do"):
            self._open(tok, tokens[i + 1 : i + 5], lineno)
            return tok != "case", i + 1
        if tok in CLOSERS:
            self._close(lineno)
            return False, i + 1
        if tok in ("else", "elif"):
            if self.stack and self.stack[-1].kind == "if":
                frame = self.stack[-1]
                frame.branch_ends[frame.branch] = (lineno, self.current_order)
                frame.branch += 1
                frame.branch_starts[frame.branch] = (lineno, self.current_order)
                frame.has_else |= tok == "else"
            return True, i + 1
        if tok in COMMAND_PREFIX_WORDS or ASSIGN_RE.match(tok):
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
                self._guard(tokens[i + 2], tokens, i, lineno)
        elif tok in GUARD_WORDS:
            for name in tokens[i + 1 :]:
                if name in SEPARATORS:
                    break
                self._guard(name, tokens, i, lineno)
        elif NAME_RE.match(tok):
            self.refs.append((tok, lineno, self.current_order))
            if (
                tok == "run_step"
                and i + 2 < len(tokens)
                and NAME_RE.match(tokens[i + 2])
            ):
                self.refs.append((tokens[i + 2], lineno, self.current_order))

    def _guard(self, name: str, tokens: list[str], i: int, lineno: int) -> None:
        in_skipped_list = self.in_list
        acted = i > 0 and tokens[i - 1] in ("if", "elif")
        scope = self._scope()
        acted = acted and not (scope is not None and scope.branch != 0)
        if in_skipped_list:
            acted = False
        for j in range(i + 1, len(tokens) - 1):
            if in_skipped_list:
                break
            if tokens[j] in (";", ";;", "&", "|"):
                break
            if tokens[j] == "||" and tokens[j + 1] not in NO_OP_ACTIONS:
                acted = True
                break
        branch = scope.branch if scope is not None and scope.kind == "if" else None
        self.guards.setdefault(name, []).append(
            Guard(lineno, self.current_order, scope, acted, branch)
        )

    def _scope(self) -> Frame | None:
        for frame in reversed(self.stack):
            if not frame.transparent:
                return frame
        return None

    def _push(self, kind: str, lineno: int) -> Frame:
        frame = Frame(
            kind, lineno, start_order=self.current_order, parent=self._scope()
        )
        if kind == "if":
            frame.branch_starts[0] = (lineno, self.current_order)
        self.stack.append(frame)
        self.frames.append(frame)
        return frame

    def _open(self, tok: str, cond: list[str], lineno: int) -> None:
        frame = self._push("loop" if tok == "do" else tok, lineno)
        if (
            tok == "if"
            and len(cond) == 4
            and cond[:3] in (["!", "declare", "-F"], ["!", "declare", "-f"])
        ):
            frame.ensures = cond[3]

    def _close(self, lineno: int) -> None:
        if not self.stack:
            return
        frame = self.stack.pop()
        frame.end = lineno
        frame.end_order = self.current_order
        if frame.kind == "if":
            frame.branch_ends[frame.branch] = (lineno, self.current_order)
        self._promote(frame)

    def _define(self, name: str, lineno: int) -> None:
        frame = self._scope()
        if self.in_list:
            # `[[ x ]] && f() {...}` defines f only when the test succeeds.
            frame = Frame(
                "list",
                lineno,
                lineno,
                start_order=self.current_order,
                end_order=self.current_order,
                parent=frame,
            )
            self.frames.append(frame)
        self.defs.append(Definition(name, lineno, self.current_order, frame))
        if frame is not None:
            frame.defs.setdefault(name, set()).add(frame.branch)
        self.pending_body = True

    def _promote(self, frame: Frame) -> None:
        """Promote names an if-block guarantees to its enclosing scope."""
        if frame.kind != "if":
            return
        branches = set(range(frame.branch + 1))
        for name, seen in frame.defs.items():
            covered = frame.has_else and seen == branches
            if not covered and not (name == frame.ensures and 0 in seen):
                continue
            parent = frame.parent
            promoted_line = frame.end or frame.start
            promoted_order = frame.end_order or frame.start_order
            self.defs.append(Definition(name, promoted_line, promoted_order, parent))
            if parent is not None:
                parent.defs.setdefault(name, set()).add(parent.branch)


def analyse(
    text: str,
) -> tuple[list[Definition], dict[str, list[Guard]], list[tuple[str, int, int]]]:
    """Return (definitions, guards per name, command-position references)."""
    result = Analyser().run(text)
    return result.defs, result.guards, result.refs
