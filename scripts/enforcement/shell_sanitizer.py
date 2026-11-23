"""Shell line sanitizer for shell_scope_parser.py (#3876)."""

from __future__ import annotations


class Sanitizer:
    """Blank out quoted literals and comments, keep command substitutions."""

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
        elif raw.startswith("$((", i):
            return self._arith(raw, i + 3, out)
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
        if raw.startswith("$((", i) or (
            raw.startswith("((", i) and (i == 0 or raw[i - 1] in " \t;&|(!")
        ):
            out.append(" A ")
            return self._arith(raw, i + (3 if ch == "$" else 2), out)
        if ch in "'\"":
            self.stack.append(["sq" if ch == "'" else "dq", 0])
            out.append("S")
        elif ch == "`":
            self._backtick(out)
        elif ch == "#" and (i == 0 or raw[i - 1] in " \t;&|("):
            return None
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

    def _arith(self, raw: str, i: int, out: list[str]) -> int:
        depth = 0
        while i < len(raw):
            if raw.startswith("))", i) and depth == 0:
                return i + 2
            if raw.startswith("$((", i):
                i = self._arith(raw, i + 3, out)
                continue
            if raw.startswith("$(", i):
                inner, i = self._extract_command_substitution(raw, i + 2)
                out.append(" ( ")
                out.append(Sanitizer().line(inner))
                out.append(" ) ")
                continue
            if raw[i] == "`":
                inner, i = self._extract_backtick(raw, i + 1)
                out.append(" ( ")
                out.append(inner)
                out.append(" ) ")
                continue
            if raw[i] in ("'", '"'):
                i = self._skip_quoted(raw, i)
                continue
            depth += {"(": 1, ")": -1}.get(raw[i], 0)
            i += 1
        return i

    def _extract_command_substitution(self, raw: str, i: int) -> tuple[str, int]:
        start, depth = i, 0
        while i < len(raw):
            if raw[i] == "\\":
                i += 2
                continue
            if raw.startswith("$(", i):
                depth += 1
                i += 2
                continue
            if raw[i] in ("'", '"'):
                i = self._skip_quoted(raw, i)
                continue
            if raw[i] == ")":
                if depth == 0:
                    return raw[start:i], i + 1
                depth -= 1
            i += 1
        return raw[start:], i

    @staticmethod
    def _extract_backtick(raw: str, i: int) -> tuple[str, int]:
        start = i
        while i < len(raw):
            if raw[i] == "\\":
                i += 2
                continue
            if raw[i] == "`":
                return raw[start:i], i + 1
            i += 1
        return raw[start:], i

    @staticmethod
    def _skip_quoted(raw: str, i: int) -> int:
        quote = raw[i]
        i += 1
        while i < len(raw):
            if raw[i] == "\\":
                i += 2
                continue
            if raw[i] == quote:
                return i + 1
            i += 1
        return i

    @staticmethod
    def _skip_param(raw: str, i: int) -> int:
        depth = 1
        while i < len(raw) and depth:
            depth += {"{": 1, "}": -1}.get(raw[i], 0)
            i += 1
        return i
