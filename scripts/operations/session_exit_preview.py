#!/usr/bin/env python3
"""Format supplied JSON from stdin as an offline Markdown exit preview.

Minimal schema (all other keys are rejected):
  issues: optional array of objects with required number (positive JSON integer)
          and optional state ("open", "closed", or "unknown").
  dirty_paths: optional array of canonical repository-relative POSIX path strings.
  next_steps: optional array of nonempty single-line strings, in supplied order.

Missing fields render as "missing"; empty arrays render as "none supplied".
Null is not a substitute for a missing field. Text cannot contain control,
format, surrogate, or line/paragraph separator characters. Paths cannot contain
backslashes, drive prefixes, empty components, or dot/parent components.
Markdown syntax and HTML in supplied text are escaped. Duplicate JSON fields and
non-finite numbers are rejected. Diagnostics contain fixed schema fields only.

Example: {"issues": [{"number": 17, "state": "unknown"}], "dirty_paths": []}
The example number is a synthetic issue identifier, not a measured quantity.
No observations, authorization, priorities, or process metadata are inferred.
This command neither collects live state nor persists a final handoff.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import PureWindowsPath
import re
import sys
import unicodedata


class PreviewError(ValueError):
    """Invalid supplied data; messages never contain input values."""


def _object(value: object, allowed: set[str], field: str) -> dict:
    if not isinstance(value, dict):
        raise PreviewError(f"{field}: expected object")
    if value.keys() - allowed:
        raise PreviewError(f"{field}: unknown field")
    return value


def _text(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or any(unicodedata.category(char).startswith('C')
               or unicodedata.category(char) in {'Zl', 'Zp'} for char in value)
    ):
        raise PreviewError(f"{field}: expected nonempty single-line string")
    return value


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PreviewError('$: duplicate field')
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise PreviewError('$: invalid JSON')


def _validate(raw: str) -> dict:
    try:
        data = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        if isinstance(exc, PreviewError):
            raise
        raise PreviewError('$: invalid JSON') from None
    data = _object(data, {'issues', 'dirty_paths', 'next_steps'}, '$')
    for field, items in data.items():
        if not isinstance(items, list):
            raise PreviewError(f'{field}: expected array')
        for item in items:
            if field == 'issues':
                issue = _object(item, {'number', 'state'}, 'issues[]')
                if 'number' not in issue:
                    raise PreviewError('issues[].number: required')
                # Positive issue identifiers follow the documented schema;
                # zero is the integer sign boundary, not an empirical threshold.
                if type(issue['number']) is not int or issue['number'] <= 0:
                    raise PreviewError('issues[].number: expected positive integer')
                if 'state' in issue and (
                    not isinstance(issue['state'], str)
                    or issue['state'] not in {'open', 'closed', 'unknown'}
                ):
                    raise PreviewError('issues[].state: expected open, closed or unknown')
            else:
                text = _text(item, f'{field}[]')
                if field == 'dirty_paths' and (
                    PureWindowsPath(text).drive
                    or '\\' in text
                    or any(part in {'', '.', '..'} for part in text.split('/'))
                ):
                    raise PreviewError('dirty_paths[]: expected canonical relative path')
    return data


def _escape(text: str) -> str:
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~\-])', r'\\\1', html.escape(text, quote=False))


def render_preview(raw: str) -> str:
    """Validate completely before rendering, without external side effects."""
    data = _validate(raw)
    lines = ['# Exit preview']
    for field, title in (
        ('issues', 'Issues'),
        ('dirty_paths', 'Dirty paths'),
        ('next_steps', 'Supplied next steps'),
    ):
        lines.extend(['', f'## {title}'])
        if field not in data:
            lines.append('- missing')
        elif not data[field]:
            lines.append('- none supplied')
        else:
            for item in data[field]:
                if field == 'issues':
                    lines.append(f"- Issue {item['number']}: {item.get('state', 'missing')}")
                else:
                    lines.append(f'- {_escape(item)}')
    return '\n'.join(lines) + '\n'


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's default error echoes unknown arguments; keep these private.
        raise PreviewError('arguments: invalid arguments')


def main(argv: list[str] | None = None) -> int:
    """CLI status follows the shell convention: zero succeeds, nonzero fails."""
    parser = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    try:
        parser.parse_args(argv)
        output = render_preview(sys.stdin.read())
    except (PreviewError, UnicodeError, OSError) as exc:
        diagnostic = str(exc) if isinstance(exc, PreviewError) else 'stdin: unable to read text'
        print(diagnostic, file=sys.stderr)
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
