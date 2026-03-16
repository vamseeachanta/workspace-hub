"""Convert pattern groups into Python code with loop collapse.

Dispatches by group size:
  - 1 cell      → single expression
  - 2-5 cells   → explicit assignments
  - 6+ cells    → for loop over rows
"""

from __future__ import annotations

import ast
import re
import sys
import os

# Add parent to path for sibling imports
sys.path.insert(0, os.path.dirname(__file__))
from formula_to_python import can_translate, formula_to_python

_ROW_RE = re.compile(r"(\d+)$")


def _is_valid_expr(expr: str) -> bool:
    """Check if expression is valid Python via ast.parse."""
    try:
        ast.parse(expr, mode="eval")
        return True
    except SyntaxError:
        return False


def _cell_row(ref: str) -> int:
    m = _ROW_RE.search(ref)
    return int(m.group(1)) if m else 1


def _cell_col(ref: str) -> str:
    m = re.match(r"([A-Z]+)", ref, re.IGNORECASE)
    return m.group(1).upper() if m else "A"


def _make_var_name(cell_ref: str, var_map: dict) -> str:
    """Get variable name for a cell ref — always a valid Python identifier."""
    if cell_ref in var_map:
        name = var_map[cell_ref]
    else:
        name = cell_ref.replace("$", "").lower()
    # Sanitize: replace non-identifier chars with underscore
    name = re.sub(r"[^a-z0-9_]", "_", name).strip("_")
    if not name or name[0].isdigit():
        name = "v_" + name
    return name


def _safe_param_name(ref: str, var_map: dict) -> str:
    """Get safe Python parameter name from ref."""
    return _make_var_name(ref, var_map)


def _translate_pattern(pattern: str, var_map: dict) -> str | None:
    """Translate canonical pattern formula to Python expression.

    Returns None if translation fails or produces invalid Python.
    """
    expr = formula_to_python(pattern, var_map)
    if expr is None:
        return None
    if not _is_valid_expr(expr):
        return None
    return expr


def pattern_to_python_code(
    pattern: str,
    cells: list[dict],
    var_map: dict,
) -> str:
    """Generate Python code from a pattern group.

    Args:
        pattern: Canonical (row-1) formula string.
        cells: List of cell dicts sharing this pattern.
        var_map: Cell ref → variable name mapping.

    Returns:
        Python code string (assignments or loop body).
    """
    if not cells:
        return ""

    n = len(cells)
    expr = _translate_pattern(pattern, var_map)

    if expr is None:
        # Untranslatable — generate manual stubs
        lines = []
        for cell in cells:
            vname = _make_var_name(cell["cell_ref"], var_map)
            safe_formula = cell["formula"].replace('"', '\\"')
            lines.append(
                f"    # MANUAL: {safe_formula}"
            )
            lines.append(f"    {vname} = None  # TODO: implement")
        return "\n".join(lines)

    if n == 1:
        vname = _make_var_name(cells[0]["cell_ref"], var_map)
        actual = formula_to_python(cells[0]["formula"], var_map)
        if actual and _is_valid_expr(actual):
            return f"    {vname} = {actual}"
        elif _is_valid_expr(expr):
            return f"    {vname} = {expr}"
        else:
            safe = cells[0]["formula"].replace('"', '\\"')
            return f"    # MANUAL: {safe}\n    {vname} = None  # TODO"

    if n <= 5:
        lines = []
        for cell in cells:
            cell_expr = _row_substitute_expr(expr, cells[0], cell, var_map)
            vname = _make_var_name(cell["cell_ref"], var_map)
            if _is_valid_expr(cell_expr):
                lines.append(f"    {vname} = {cell_expr}")
            else:
                safe = cell["formula"].replace('"', '\\"')
                lines.append(f"    # MANUAL: {safe}")
                lines.append(f"    {vname} = None  # TODO")
        return "\n".join(lines)

    # 6+ cells → loop (only if expr is valid Python)
    if not _is_valid_expr(expr):
        # Fall back to manual stubs for all cells
        lines = []
        for cell in cells[:3]:
            safe = cell["formula"].replace('"', '\\"')
            vname = _make_var_name(cell["cell_ref"], var_map)
            lines.append(f"    # MANUAL: {safe}")
            lines.append(f"    {vname} = None  # TODO")
        if n > 3:
            lines.append(f"    # ... and {n - 3} more cells")
        return "\n".join(lines)

    rows = [_cell_row(c["cell_ref"]) for c in cells]
    col = _cell_col(cells[0]["cell_ref"])
    start, end = min(rows), max(rows)
    safe_comment = pattern.replace('"', '\\"')
    lines = [
        f"    results = {{}}",
        f"    for row in range({start}, {end + 1}):",
        f"        # Pattern: {safe_comment}",
        f"        results['{col.lower()}' + str(row)] = {expr}",
    ]
    return "\n".join(lines)


def _row_substitute_expr(
    base_expr: str, base_cell: dict, target_cell: dict, var_map: dict,
) -> str:
    """Substitute row-1 expression vars for a specific cell's row."""
    actual_expr = formula_to_python(target_cell["formula"], var_map)
    if actual_expr and _is_valid_expr(actual_expr):
        return actual_expr
    return base_expr


def generate_function_from_pattern(
    name: str,
    pattern: str,
    cells: list[dict],
    var_map: dict,
    inputs: list[str],
) -> str:
    """Generate a complete Python function from a pattern group.

    Args:
        name: Function name.
        pattern: Canonical formula string.
        cells: Cells sharing this pattern.
        var_map: Cell ref → variable name mapping.
        inputs: List of input cell refs for this pattern.

    Returns:
        Complete function definition as a string.
    """
    expr = _translate_pattern(pattern, var_map)
    is_manual = expr is None

    # Build parameter list with safe names
    params = []
    for ref in inputs:
        pname = _safe_param_name(ref, var_map)
        if pname not in params:
            params.append(pname)

    param_str = ", ".join(f"{p}: float" for p in params) if params else ""

    n = len(cells)
    body = pattern_to_python_code(pattern, cells, var_map)

    # Escape quotes in pattern for docstring safety
    safe_pattern = pattern.replace('"""', "'''").replace('"', '\\"')
    sheet_name = cells[0]["sheet"] if cells else "Unknown"

    lines = [
        f"def {name}({param_str}) -> float | dict:",
        f'    """Excel pattern: {safe_pattern}',
        f"",
        f"    Cells: {n} ({sheet_name})",
        f'    """',
    ]

    lines.append(body)

    # Return statement
    if is_manual:
        lines.append(f"    return None  # MANUAL: needs implementation")
    elif n == 1:
        vname = _make_var_name(cells[0]["cell_ref"], var_map)
        lines.append(f"    return {vname}")
    elif n <= 5:
        # Return last computed value
        vname = _make_var_name(cells[-1]["cell_ref"], var_map)
        lines.append(f"    return {vname}")
    else:
        lines.append("    return results")

    return "\n".join(lines)
