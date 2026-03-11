#!/usr/bin/env python3
"""AST-based public symbol and docstring coverage scanner (WRK-1059).

Usage: uv run --no-project python scripts/quality/api-audit.py <repo_name> <src_path>
Output: JSON {"repo": str, "total": int, "with_docstring": int, "coverage_pct": float}
"""

import ast
import json
import sys
from pathlib import Path


def has_docstring(node: ast.AST) -> bool:
    """Return True if the node body starts with a string constant (docstring)."""
    body = getattr(node, "body", [])
    return (
        bool(body)
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def collect_symbols(tree: ast.Module) -> list[tuple[str, bool]]:
    """Return (name, has_docstring) for public module-level and class-level symbols only.

    Counts module-level functions/classes and methods directly inside public classes.
    Nested/inner functions are excluded to avoid inflating coverage metrics.
    """
    symbols: list[tuple[str, bool]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                symbols.append((node.name, has_docstring(node)))
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                symbols.append((node.name, has_docstring(node)))
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not member.name.startswith("_"):
                            symbols.append((member.name, has_docstring(member)))
    return symbols


def audit_path(src_path: Path) -> tuple[int, int]:
    """Return (total, with_docstring) counts across all .py files under src_path."""
    total = 0
    with_doc = 0
    for py_file in sorted(src_path.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for _name, doc_present in collect_symbols(tree):
            total += 1
            if doc_present:
                with_doc += 1
    return total, with_doc


def main() -> None:
    """Entry point: argv = <repo_name> <src_path>."""
    if len(sys.argv) != 3:
        print("Usage: api-audit.py <repo_name> <src_path>", file=sys.stderr)
        sys.exit(1)

    repo_name = sys.argv[1]
    src_path = Path(sys.argv[2])

    if not src_path.is_dir():
        print(f"ERROR: src_path not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    total, with_doc = audit_path(src_path)
    coverage_pct = round((with_doc / total * 100) if total > 0 else 0.0, 1)

    result = {
        "repo": repo_name,
        "total": total,
        "with_docstring": with_doc,
        "coverage_pct": coverage_pct,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
