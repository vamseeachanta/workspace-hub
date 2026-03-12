#!/usr/bin/env python3
"""render_template.py — dependency-free template renderer for new-module.sh.

Replaces {{PLACEHOLDER}} tokens in template files with provided values.

Usage:
    python render_template.py <template_file> <output_file> KEY=value [KEY=value ...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def render(template_text: str, variables: dict[str, str]) -> str:
    """Replace all {{KEY}} tokens with values from variables dict."""
    def replace_token(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Template token {{{{{key}}}}} has no substitution value")
        return variables[key]

    return re.sub(r"\{\{([A-Z_]+)\}\}", replace_token, template_text)


def main() -> None:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <template_file> <output_file> [KEY=value ...]", file=sys.stderr)
        sys.exit(1)

    template_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    raw_vars = sys.argv[3:]

    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    variables: dict[str, str] = {}
    for item in raw_vars:
        if "=" not in item:
            print(f"Invalid variable (expected KEY=value): {item!r}", file=sys.stderr)
            sys.exit(1)
        key, _, value = item.partition("=")
        variables[key.strip()] = value

    template_text = template_path.read_text(encoding="utf-8")
    try:
        output_text = render(template_text, variables)
    except KeyError as exc:
        print(f"Render error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")


if __name__ == "__main__":
    main()
