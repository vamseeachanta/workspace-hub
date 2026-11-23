#!/usr/bin/env python3
"""Reject Python files and functions exceeding physical-line limits."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Sequence


def _physical_lines(text: str) -> int:
    return len(text.splitlines())


def _function_span(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
    starts = [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
    return min(starts), node.end_lineno or node.lineno


def _check(path: Path, max_file_lines: int, max_function_lines: int) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{path}: cannot inspect Python source: {exc}"]
    failures: list[str] = []
    file_lines = _physical_lines(text)
    if file_lines > max_file_lines:
        failures.append(f"{path}: file has {file_lines} physical lines (max {max_file_lines})")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end = _function_span(node)
            count = end - start + 1
            if count > max_function_lines:
                failures.append(
                    f"{path}:{start}: {node.name} has {count} physical lines "
                    f"(max {max_function_lines})"
                )
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-file-lines", type=int, default=400)
    parser.add_argument("--max-function-lines", type=int, default=50)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    if args.max_file_lines < 1 or args.max_function_lines < 1:
        parser.error("line limits must be positive")
    failures = [
        failure
        for path in args.paths
        for failure in _check(path, args.max_file_lines, args.max_function_lines)
    ]
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
