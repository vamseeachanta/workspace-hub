"""Redact client identifiers from text before a generator writes a PUBLIC file.

Owner decision C20 (2026-09-26). Several generators write files of this public
repository from text nobody reviews first: the kanban reconciler and the
provider boards from GitHub issue titles and bodies, the learning-artifact
snapshot from host agent state. Each of them calls this module, which applies
the identifier gate's single ``Redactor`` (``scripts/legal/check_identifiers.py``)
-- the same rules, the same private list, the same marker -- so a generator
cannot publish what the gate would fail.

Fail closed. ``load_redactor`` raises ``RedactorUnavailable`` when:

* the gate module or its rules file cannot load;
* no private deny list is loaded (``WORKSPACE_HUB_DENY_LIST``, or the default
  private path the gate reads) -- the public hashes alone do not cover the
  multi-word names on the private list, so a public-only redactor would pass
  them through;
* ``LEGAL_CLIENT_MAP`` names a client codename map that is missing or
  unreadable. When it is set, the map's patterns are added to the Redactor's
  private patterns.

A generator that catches ``RedactorUnavailable`` must stop without writing.

Command line (exit 0 success, 1 ``check`` found identifiers, 3 unavailable)::

    python scripts/legal/public_redaction.py self-check
    python scripts/legal/public_redaction.py copy SRC DEST
    python scripts/legal/public_redaction.py inplace FILE...
    python scripts/legal/public_redaction.py check FILE...

``copy`` writes the redacted content of SRC to DEST, and skips SRC -- writing
nothing -- when its file name carries an identifier. Nothing this module
prints quotes the text it redacted or a path it was given.
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


def load_redactor(require_private: bool = True):
    """The gate's Redactor over its rules, the private list and, when
    ``LEGAL_CLIENT_MAP`` is set, the client codename map. Raises
    ``RedactorUnavailable`` rather than return a partial redactor."""
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
    if require_private and not private:
        raise RedactorUnavailable(
            "public_redaction: no private deny list is loaded; set "
            f"{ci.PRIVATE_ENV} to the private list. The public hashes alone do "
            "not cover every name, so writing a public file is refused."
        )
    if not (rules.get("hashed_names") or private):
        raise RedactorUnavailable("public_redaction: the rules carry no names; refusing to continue")
    rules["_private_patterns"] = list(rules.get("_private_patterns") or []) + _map_patterns()
    return ci.Redactor(rules)


def redact_tree(obj: Any, redactor) -> Any:
    """A copy of *obj* with every string -- mapping keys included -- redacted.
    Numbers, booleans and None are returned as they are; *obj* is not
    mutated. Mapping types that support copying (ruamel's round-trip maps)
    keep their type."""
    if isinstance(obj, str):
        out = redactor.redact(obj)
        if out == obj:
            return obj
        try:
            return type(obj)(out)  # keep a quoted-scalar string type
        except Exception:  # noqa: BLE001
            return out
    if isinstance(obj, dict):
        new = obj.copy() if hasattr(obj, "copy") else dict(obj)
        new.clear()
        for k, v in obj.items():
            new[redact_tree(k, redactor) if isinstance(k, str) else k] = redact_tree(v, redactor)
        return new
    if isinstance(obj, list):
        new = obj.copy()
        new[:] = [redact_tree(v, redactor) for v in obj]
        return new
    if isinstance(obj, tuple):
        return tuple(redact_tree(v, redactor) for v in obj)
    return obj


#: One JSON string literal.
_JSON_STRING = re.compile(r'"(?:[^"\\\x00-\x1f]|\\.)*"')


def _redact_json_strings(text: str, redactor) -> str:
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
        new = redactor.redact(value)
        if new == value:
            return lit
        return json.dumps(new, ensure_ascii=lit.isascii())

    return _JSON_STRING.sub(sub, text)


def _redact_json_document(text: str, redactor) -> str:
    try:
        json.loads(text)
    except ValueError:
        return redactor.redact(text)
    new = _redact_json_strings(text, redactor)
    try:
        json.loads(new)
    except ValueError:  # pragma: no cover - defensive: re-serialise instead
        obj = redact_tree(json.loads(text), redactor)
        return json.dumps(obj, indent=2, ensure_ascii=False) + ("\n" if text.endswith("\n") else "")
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
        _write(dest, redact_file_text(_read(src), os.path.splitext(src)[1], red))
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
        new = redact_file_text(text, os.path.splitext(f)[1], red)
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
