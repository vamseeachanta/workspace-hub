"""Redact client identifiers from text before a generator writes a PUBLIC file.

Owner decision C20 (2026-09-26). Several generators write files of this public
repository from text nobody reviews first: the kanban reconciler and the
provider boards from GitHub issue titles and bodies, the learning-artifact
snapshot from host agent state. Each of them calls this module, which applies
the identifier gate's single ``Redactor`` (``scripts/legal/check_identifiers.py``)
-- the same rules, the same private list, the same marker -- so a generator
cannot publish what the gate would fail.

The private deny list (``WORKSPACE_HUB_DENY_LIST``, or the default private path
the gate reads) extends the redactor when the host has one. A host without it
runs with the public rules instead of stopping (owner decision S01, 2026-09-27).

``load_redactor`` raises ``RedactorUnavailable`` when:

* the gate module or its rules file cannot load, or the rules carry no names;
* ``WORKSPACE_HUB_DENY_LIST`` or ``LEGAL_CLIENT_MAP`` names a file that is
  missing or unreadable (a named file is a configuration, and a typo in it
  must not pass silently). When ``LEGAL_CLIENT_MAP`` is set, the map's patterns
  are added to the Redactor's private patterns.

A generator that catches ``RedactorUnavailable`` must stop without writing.

Colliding JSON/tree keys get deterministic alphabetic suffixes on their redacted
text. Exact string references use the same alias within that document; aliases
are not cross-document identities. Numeric JSON tokens and text outside string
literals are preserved exactly. Duplicate JSON keys, non-finite constants or
an unavailable safe alias raise ``RedactorUnavailable`` rather than lose data.

Command line (exit 0 success, 1 ``check`` found identifiers, 3 unavailable)::

    python scripts/legal/public_redaction.py self-check
    python scripts/legal/public_redaction.py copy SRC DEST
    python scripts/legal/public_redaction.py inplace FILE...
    python scripts/legal/public_redaction.py check FILE...

``copy`` writes the redacted content of SRC to DEST, and skips SRC -- writing
nothing -- when its file name carries an identifier. Nothing this module
prints quotes the text it redacted or a path it was given.
An ``inplace`` refusal leaves that file unchanged; earlier files in a multi-file
invocation may already have been rewritten. Existing file decoding removes a BOM.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
#: Environment variable naming the private client codename map (#3097).
MAP_ENV = "LEGAL_CLIENT_MAP"
EXIT_FOUND = 1
EXIT_UNAVAILABLE = 3


class RedactorUnavailable(RuntimeError):
    """The redactor could not be loaded completely. Never a pass."""


_GATE = None


def _gate():
    """The identifier gate module, loaded once by path."""
    global _GATE
    if _GATE is None:
        path = os.path.join(HERE, "check_identifiers.py")
        spec = importlib.util.spec_from_file_location("_c20_check_identifiers", path)
        if spec is None or spec.loader is None:
            raise RedactorUnavailable("public_redaction: the identifier gate module cannot load")
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            raise RedactorUnavailable(
                f"public_redaction: the identifier gate module cannot load ({type(exc).__name__})"
            ) from None
        _GATE = mod
    return _GATE


def _map_patterns() -> list[re.Pattern]:
    path = os.environ.get(MAP_ENV)
    if not path:
        return []
    if not os.path.isfile(path):
        raise RedactorUnavailable(
            f"public_redaction: the file {MAP_ENV} names does not exist; refusing to continue"
        )
    try:
        import yaml

        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        out = []
        for rule in doc["rules"]:
            pat = str(rule["pattern"])
            if rule.get("word_bound"):
                pat = rf"(?<![A-Za-z]){pat}(?![A-Za-z])"
            out.append(re.compile(pat, re.IGNORECASE))
    except Exception as exc:  # noqa: BLE001
        # The parser's message can quote the map: name the failure type only.
        raise RedactorUnavailable(
            f"public_redaction: the client codename map is unreadable ({type(exc).__name__})"
        ) from None
    if not out:
        raise RedactorUnavailable("public_redaction: the client codename map has no rules")
    return out


def load_redactor():
    """The gate's Redactor over its rules, the private list when this host has
    one and, when ``LEGAL_CLIENT_MAP`` is set, the client codename map. Raises
    ``RedactorUnavailable`` when the rules cannot load or a named file is
    missing; a host without the private list gets the public rules (S01)."""
    ci = _gate()
    try:
        rules = ci.load_rules()
    except SystemExit:
        # load_rules() reports through the gate's redacting sink and exits.
        raise RedactorUnavailable("public_redaction: the identifier gate rules cannot load") from None
    except Exception as exc:  # noqa: BLE001
        raise RedactorUnavailable(
            f"public_redaction: the identifier gate rules cannot load ({type(exc).__name__})"
        ) from None
    private = list(rules.get("_private_names") or []) + list(rules.get("_private_patterns") or [])
    if not (rules.get("hashed_names") or private):
        raise RedactorUnavailable("public_redaction: the rules carry no names; refusing to continue")
    rules["_private_patterns"] = list(rules.get("_private_patterns") or []) + _map_patterns()
    return ci.Redactor(rules)


def _string_replacements(obj: Any, redactor) -> dict[str, str]:
    """Plan collision-free, document-local aliases using the existing redactor.

    Only keys that would collide need aliases. Reserve all input and redacted
    strings first, including later keys, and reuse aliases for exact string
    references to those keys. Alphabetic suffixes introduce no numeric values.
    """
    replacements: dict[str, str] = {}
    needs_alias: dict[str, None] = {}

    def remember(value: str) -> str:
        if value not in replacements:
            replacements[value] = redactor.redact(value)
        return replacements[value]

    def visit(node: Any) -> None:
        if isinstance(node, str):
            remember(node)
        elif isinstance(node, dict):
            groups: dict[str, list[str]] = {}
            for key, value in node.items():
                if isinstance(key, str):
                    groups.setdefault(remember(key), []).append(key)
                visit(value)
            for stem, keys in groups.items():
                if len(keys) > 1:
                    for key in keys:
                        if key != stem:
                            needs_alias[key] = None
        elif isinstance(node, (list, tuple)):
            for value in node:
                visit(value)

    visit(obj)
    reserved = set(replacements) | set(replacements.values())
    next_suffix: dict[str, int] = {}

    def letters(number: int) -> str:
        out = ""
        while True:
            number, digit = divmod(number, 26)
            out = chr(97 + digit) + out
            if not number:
                return out
            number -= 1

    for key in replacements:
        if key not in needs_alias:
            continue
        stem = replacements[key]
        for _ in range(len(reserved) + len(needs_alias) + 26):
            number = next_suffix.get(stem, 0)
            next_suffix[stem] = number + 1
            alias = f"{stem} [{letters(number)}]"
            if alias not in reserved and redactor.redact(alias) == alias:
                replacements[key] = alias
                reserved.add(alias)
                break
        else:
            raise RedactorUnavailable(
                "public_redaction: safe unique key aliases unavailable; refusing lossy redaction"
            ) from None
    return replacements


def redact_tree(obj: Any, redactor) -> Any:
    """A copy of *obj* with every string -- mapping keys included -- redacted.
    Numbers, booleans and None are returned as they are; *obj* is not
    mutated. Mapping types that support copying (ruamel's round-trip maps)
    keep their type. Colliding changed keys and exact string references share
    document-local aliases; other strings use the gate redactor unchanged.
    Non-string keys retain the existing behavior and are left unchanged.
    """
    return _replace_tree(obj, _string_replacements(obj, redactor))


def _replace_tree(obj: Any, replacements: dict[str, str]) -> Any:
    """Apply one document's replacement plan without mutating its input."""

    def replace(node: Any) -> Any:
        if isinstance(node, str):
            out = replacements[node]
            if out == node:
                return node
            try:
                return type(node)(out)  # keep a quoted-scalar string type
            except Exception:  # noqa: BLE001
                return out
        if isinstance(node, dict):
            new = node.copy() if hasattr(node, "copy") else dict(node)
            new.clear()
            for key, value in node.items():
                new[replace(key) if isinstance(key, str) else key] = replace(value)
            return new
        if isinstance(node, list):
            new = node.copy()
            new[:] = [replace(value) for value in node]
            return new
        if isinstance(node, tuple):
            return tuple(replace(value) for value in node)
        return node

    return replace(obj)


#: One JSON string literal.
_JSON_STRING = re.compile(r'"(?:[^"\\\x00-\x1f]|\\.)*"')


def _redact_json_strings(text: str, replacements: dict[str, str]) -> str:
    """Redact each JSON string literal (keys included) on its own, decoded,
    and re-encode only the literals that change. The rest of the text --
    layout, key order, escapes -- stays byte-identical, and a redaction can
    never cut through an escape sequence."""

    def sub(m: re.Match) -> str:
        lit = m.group(0)
        try:
            value = json.loads(lit)
        except ValueError:
            return lit
        new = replacements[value]
        if new == value:
            return lit
        return json.dumps(new, ensure_ascii=lit.isascii())

    return _JSON_STRING.sub(sub, text)


def _unique_json_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise RedactorUnavailable(
                "public_redaction: duplicate JSON keys; refusing lossy redaction"
            ) from None
        out[key] = value
    return out


class _JsonNumber:
    """Keep JSON number tokens exact during validation, without float/int parsing."""

    def __init__(self, token: str):
        self.token = token

    def __eq__(self, other):
        return isinstance(other, _JsonNumber) and self.token == other.token


def _reject_json_constant(_):
    raise RedactorUnavailable(
        "public_redaction: non-finite JSON number; refusing invalid JSON"
    ) from None


def _parse_json(text: str):
    return json.loads(
        text[1:] if text.startswith("\ufeff") else text,
        object_pairs_hook=_unique_json_object,
        parse_int=_JsonNumber,
        parse_float=_JsonNumber,
        parse_constant=_reject_json_constant,
    )


def _redact_json_document(text: str, redactor) -> str:
    try:
        obj = _parse_json(text)
    except ValueError:
        return redactor.redact(text)
    replacements = _string_replacements(obj, redactor)
    new = _redact_json_strings(text, replacements)
    try:
        output = _parse_json(new)
    except ValueError:  # pragma: no cover - string substitution must preserve JSON
        raise RedactorUnavailable(
            "public_redaction: invalid JSON after redaction; refusing to reserialize values"
        ) from None
    if output != _replace_tree(obj, replacements) or _JSON_STRING.sub("", text) != _JSON_STRING.sub("", new):
        raise RedactorUnavailable(
            "public_redaction: JSON structure or numeric tokens changed; refusing lossy redaction"
        ) from None
    return new


def redact_file_text(text: str, ext: str, redactor) -> str:
    """Redact file content by type. JSON and JSONL are redacted string literal
    by string literal, so a redaction can never break an escape and the file
    stays valid; unchanged text stays byte-identical. Any other type is
    redacted as text."""
    ext = ext.lower()
    if ext == ".json":
        return _redact_json_document(text, redactor)
    if ext == ".jsonl":
        parts = text.split("\n")
        return "\n".join(_redact_json_document(p, redactor) if p.strip() else p for p in parts)
    return redactor.redact(text)


def _read(path: str) -> str:
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _say(msg: str, err: bool = False) -> None:
    (sys.stderr if err else sys.stdout).write(msg + "\n")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in {"self-check", "copy", "inplace", "check"}:
        _say("usage: public_redaction.py self-check | copy SRC DEST | inplace FILE... | check FILE...", True)
        return 2
    cmd, args = argv[0], argv[1:]
    try:
        red = load_redactor()
    except RedactorUnavailable as exc:
        _say(str(exc), True)
        return EXIT_UNAVAILABLE
    if cmd == "self-check":
        _say("public_redaction: redactor loaded")
        return 0
    if cmd == "copy":
        if len(args) != 2:
            _say("public_redaction: copy takes SRC and DEST", True)
            return 2
        src, dest = args
        base = os.path.basename(src)
        if red.redact(base) != base:
            _say("public_redaction: skipped one file whose name carries an identifier")
            return 0
        try:
            new = redact_file_text(_read(src), os.path.splitext(src)[1], red)
        except RedactorUnavailable as exc:
            _say(str(exc), True)
            return EXIT_UNAVAILABLE
        _write(dest, new)
        return 0
    found = 0
    for f in args:
        if os.path.islink(f) or not os.path.isfile(f):
            continue
        with open(f, "rb") as fh:
            head = fh.read(4096)
        if b"\x00" in head:
            # Binary: never rewritten here. The identifier gate reads it, or
            # fails it as uninspectable.
            continue
        text = _read(f)
        try:
            new = redact_file_text(text, os.path.splitext(f)[1], red)
        except RedactorUnavailable as exc:
            _say(str(exc), True)
            return EXIT_UNAVAILABLE
        if new != text:
            found += 1
            if cmd == "inplace":
                _write(f, new)
    if cmd == "check":
        _say(f"public_redaction: {found} of {len(args)} file(s) carry an identifier")
        return EXIT_FOUND if found else 0
    _say(f"public_redaction: redacted {found} of {len(args)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
