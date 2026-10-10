"""Scope-aware shell parser for check-shell-conditional-helpers.py (#3876).

Tracks where shell functions are defined (if/case/loop bodies, && / || lists,
function bodies, subshells), where guards for them sit, and which words are
called in command position. Line-oriented and deliberately small: it is a
lint for test harnesses, not a full shell grammar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.-]*$")
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^]]*\])?\+?=")
TOKEN_RE = re.compile(r";;|&&|\|\||[;&|(){}]|[^\s;&|(){}]+")
HEREDOC_RE = re.compile(
    r"(?<!<)<<(?!<)(-?)\s*(?:'([^']*)'|\"([^\"]*)\"|\\?([^\s;&|<>()'\"]+))"
)
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


@dataclass
class Frame:
    kind: str  # if | case | loop | function | list | subshell | brace
    start: int
    end: int | None = None
    branch: int = 0
    has_else: bool = False
    ensures: str | None = None  # name from ``if ! declare -F <name>``
    parent: Frame | None = None  # nearest enclosing scope (never a plain brace)
    defs: dict[str, set[int]] = field(default_factory=dict)  # name -> branches

    @property
    def transparent(self) -> bool:
        """A plain ``{ ...; }`` group does not make its contents conditional."""
        return self.kind == "brace"


@dataclass
class Definition:
    name: str
    line: int
    frame: Frame | None  # None = unconditional


@dataclass
class Guard:
    line: int
    frame: Frame | None
    acted: bool


class Sanitizer:
    """Blank out quoted literals and comments, keep command substitutions.

    The context stack persists across lines so multi-line strings and
    substitutions are handled. Each entry is ``[kind, paren_depth]``; kinds are
    ``code`` (top level or ``$(...)``), ``bt`` (backticks), ``sq``, ``ansi``
    (``$'...'``) and ``dq``.
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
            if kind in ("sq", "ansi"):
                i = self._single(raw, i, kind == "ansi")
            elif kind == "dq":
                i = self._double(raw, i, out)
            else:
                i = self._code(raw, i, out)
        return "".join(out)

    def _single(self, raw: str, i: int, ansi: bool) -> int:
        if ansi and raw[i] == "\\":
            return i + 2
        if raw[i] == "'":
            self.stack.pop()
        return i + 1

    def _double(self, raw: str, i: int, out: list[str]) -> int:
        ch, nxt = raw[i], raw[i + 1 : i + 2]
        if ch == "\\":
            return i + 2
        if ch == '"':
            self.stack.pop()
        elif ch == "`":
            self.stack.append(["bt", 0])
            out.append(" ( ")
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
        if ch == "$" and nxt == "'":
            self.stack.append(["ansi", 0])
            out.append("S")
            return i + 2
        if ch in "'\"":
            self.stack.append(["sq" if ch == "'" else "dq", 0])
            out.append("S")
        elif ch == "`":
            self._backtick(out)
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t;&|("):
            return None  # comment runs to end of line
        elif ch == "$" and nxt == "{":
            out.append("V")
            return self._skip_param(raw, i + 2)
        elif ch == "$" and nxt == "(":
            self.stack.append(["code", 0])
            out.append(" ( ")
            return i + 2
        elif ch in "()":
            self._paren(ch, ctx, out)
        else:
            out.append(ch)
        return i + 1

    def _backtick(self, out: list[str]) -> None:
        if self.stack[-1][0] == "bt":
            self.stack.pop()
            out.append(" ) ")
        else:
            self.stack.append(["bt", 0])
            out.append(" ( ")

    def _paren(self, ch: str, ctx: list, out: list[str]) -> None:
        if not self.at_top_level and ctx[0] == "code":
            if ch == "(":
                ctx[1] += 1
            elif ctx[1] == 0:
                self.stack.pop()
            else:
                ctx[1] -= 1
        out.append(f" {ch} ")

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
        self.guards: dict[str, list[Guard]] = {}
        self.refs: list[tuple[str, int]] = []
        self.heredoc: tuple[str, bool] | None = None
        self.in_list = False  # after && / || on the current command line
        self.pending_body = False  # a definition's body has not opened yet

    def run(self, text: str) -> Analyser:
        lines = text.splitlines()
        pending, first = "", 0
        for lineno, raw in enumerate(lines, start=1):
            if self.heredoc is not None:
                self._heredoc_line(raw)
                continue
            if raw.endswith("\\") and not raw.endswith("\\\\"):
                pending, first = pending + raw[:-1] + " ", first or lineno
                continue
            self._line(first or lineno, pending + raw)
            pending, first = "", 0
        if pending:
            self._line(first, pending)
        for frame in self.frames:
            if frame.end is None:
                frame.end = len(lines)
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
            self.refs.append((tok, lineno))
            if (
                tok == "run_step"
                and i + 2 < len(tokens)
                and NAME_RE.match(tokens[i + 2])
            ):
                self.refs.append((tokens[i + 2], lineno))

    def _guard(self, name: str, tokens: list[str], i: int, lineno: int) -> None:
        acted = i > 0 and tokens[i - 1] in ("if", "elif")
        for j in range(i + 1, len(tokens) - 1):
            if tokens[j] == "||" and tokens[j + 1] not in NO_OP_ACTIONS:
                acted = True
        self.guards.setdefault(name, []).append(Guard(lineno, self._scope(), acted))

    def _scope(self) -> Frame | None:
        for frame in reversed(self.stack):
            if not frame.transparent:
                return frame
        return None

    def _push(self, kind: str, lineno: int) -> Frame:
        frame = Frame(kind, lineno, parent=self._scope())
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
        self._promote(frame)

    def _define(self, name: str, lineno: int) -> None:
        frame = self._scope()
        if self.in_list:
            # `[[ x ]] && f() {...}` defines f only when the test succeeds.
            frame = Frame("list", lineno, lineno, parent=frame)
            self.frames.append(frame)
        self.defs.append(Definition(name, lineno, frame))
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
            self.defs.append(Definition(name, frame.end or frame.start, parent))
            if parent is not None:
                parent.defs.setdefault(name, set()).add(parent.branch)


def analyse(
    text: str,
) -> tuple[list[Definition], dict[str, list[Guard]], list[tuple[str, int]]]:
    """Return (definitions, guards per name, command-position references)."""
    result = Analyser().run(text)
    return result.defs, result.guards, result.refs
