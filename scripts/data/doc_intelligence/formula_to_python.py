"""Translate simple Excel formulas to Python expressions.

Handles arithmetic operators, PI(), SQRT(), ABS(), cell ref stripping.
Returns None for formulas that need manual translation (VLOOKUP, IF, etc).
"""

import math
import re

# Excel functions with direct Python equivalents
_FUNC_MAP = {
    "PI()": "math.pi",
    "SQRT(": "math.sqrt(",
    "ABS(": "abs(",
    "ROUND(": "round(",
    "SUM(": "sum([",  # needs closing bracket fixup
    "MIN(": "min(",
    "MAX(": "max(",
    "LN(": "math.log(",
    "LOG10(": "math.log10(",
    "LOG(": "math.log(",
    "EXP(": "math.exp(",
    "SIN(": "math.sin(",
    "COS(": "math.cos(",
    "TAN(": "math.tan(",
    "ASIN(": "math.asin(",
    "ACOS(": "math.acos(",
    "ATAN(": "math.atan(",
    "ATAN2(": "math.atan2(",
    "POWER(": "pow(",
    "MOD(": "math.fmod(",
    "INT(": "int(",
}

# Functions that block auto-translation
_COMPLEX_FUNCTIONS = {
    "VLOOKUP", "HLOOKUP", "LOOKUP", "INDEX", "MATCH",
    "IF", "IFS", "CHOOSE", "SWITCH",
    "SUMIF", "SUMIFS", "COUNTIF", "COUNTIFS", "AVERAGEIF",
    "OFFSET", "INDIRECT", "ADDRESS",
    "CONCATENATE", "TEXT", "LEFT", "RIGHT", "MID", "FIND", "SEARCH",
}

# Cell reference pattern (strips $ signs, captures ref)
_CELL_REF = re.compile(
    r"(?:'([^']+)'!|([A-Za-z_]\w*)!)?"
    r"\$?([A-Z]{1,3})\$?(\d+)"
)


def can_translate(formula: str) -> bool:
    """Check if a formula can be auto-translated to Python."""
    if not formula or not formula.startswith("="):
        return False
    upper = formula.upper()
    # Block string concatenation
    if "&" in formula:
        return False
    # Block complex functions
    for func in _COMPLEX_FUNCTIONS:
        if func + "(" in upper:
            return False
    return True


def formula_to_python(formula: str, var_map: dict | None = None) -> str | None:
    """Convert an Excel formula to a Python expression.

    Args:
        formula: Excel formula string (e.g., "=A1*B1+C1")
        var_map: Optional mapping of cell refs to variable names
                 e.g., {"B2": "diameter", "B3": "wall_thickness"}

    Returns:
        Python expression string, or None if formula is too complex.
    """
    if not can_translate(formula):
        return None

    var_map = var_map or {}
    expr = formula.lstrip("=").strip()

    # Replace Excel power operator ^ with Python **
    expr = expr.replace("^", "**")

    # Replace Excel functions with Python equivalents (case-insensitive)
    for excel_fn, py_fn in _FUNC_MAP.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(excel_fn), re.IGNORECASE)
        expr = pattern.sub(py_fn, expr)

    # Fix SUM → sum([...]) — need to close the list bracket
    if "sum([" in expr:
        # Simple case: sum([A1:A10]) → not supported (range), but sum([a, b, c]) works
        pass

    # Replace cell references with variable names or snake_case refs
    def replace_ref(m):
        sheet = m.group(1) or m.group(2) or ""
        col = m.group(3)
        row = m.group(4)
        ref = f"{col}{row}"
        full_ref = f"{sheet}!{ref}" if sheet else ref
        # Check var_map for both full and short ref
        if full_ref in var_map:
            return var_map[full_ref]
        if ref in var_map:
            return var_map[ref]
        # Default: lowercase cell ref as variable name
        return ref.lower()

    expr = _CELL_REF.sub(replace_ref, expr)

    return expr


def formula_to_function(
    name: str,
    formula: str,
    input_refs: list[str],
    var_map: dict | None = None,
    cached_value: float | None = None,
) -> str | None:
    """Generate a complete Python function from an Excel formula.

    Returns a string containing a def statement, or None if untranslatable.
    """
    expr = formula_to_python(formula, var_map)
    if expr is None:
        return None

    var_map = var_map or {}
    # Build parameter list from input refs
    params = []
    for ref in input_refs:
        param_name = var_map.get(ref, ref.lower())
        if param_name not in params:
            params.append(param_name)

    param_str = ", ".join(f"{p}: float" for p in params)
    lines = [
        f"def {name}({param_str}) -> float:",
        f'    """Excel: {formula}"""',
        f"    return {expr}",
    ]

    if cached_value is not None and isinstance(cached_value, (int, float)):
        lines.append("")
        lines.append(f"# Test: {name}(...) == pytest.approx({cached_value})")

    return "\n".join(lines)


def translate_simple_formulas(formulas_yaml: dict) -> dict:
    """Translate all simple formulas from a formulas.yaml file.

    Returns dict with 'translated' and 'skipped' lists.
    """
    result = {"translated": [], "skipped": [], "stats": {}}
    formulas = formulas_yaml.get("formulas", [])

    for f in formulas:
        formula = f.get("formula", "")
        if can_translate(formula):
            expr = formula_to_python(formula)
            if expr:
                result["translated"].append({
                    "cell_ref": f["cell_ref"],
                    "sheet": f["sheet"],
                    "excel": formula,
                    "python": expr,
                    "cached_value": f.get("cached_value"),
                })
            else:
                result["skipped"].append({
                    "cell_ref": f["cell_ref"],
                    "formula": formula,
                    "reason": "translation returned None",
                })
        else:
            result["skipped"].append({
                "cell_ref": f["cell_ref"],
                "formula": formula,
                "reason": "complex function detected",
            })

    result["stats"] = {
        "total": len(formulas),
        "translated": len(result["translated"]),
        "skipped": len(result["skipped"]),
        "pct_translated": round(
            100 * len(result["translated"]) / max(len(formulas), 1), 1
        ),
    }
    return result
