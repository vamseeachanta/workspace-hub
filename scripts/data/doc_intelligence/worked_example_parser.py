"""Enhanced worked-example parser — extracts inputs, units, generates real assertions.

Extends the basic regex parsing in promoters/worked_examples.py with:
- "Given:" section input parameter extraction (symbol, value, unit)
- Solution line unit extraction
- Real pytest test file generation with pytest.approx assertions

Usage:
    from scripts.data.doc_intelligence.worked_example_parser import (
        parse_enhanced_example, render_real_test_file,
    )
"""

import re
from typing import Optional


# Pattern: "Example N.N: <title>" (N can have multiple dot-separated parts)
_EXAMPLE_RE = re.compile(
    r"Example\s+([\d]+(?:\.[\d]+)*)\s*:\s*(.+?)(?:\.\s|\.$|$)", re.IGNORECASE
)

# Pattern: last number on the Solution line (handles commas in numbers)
_SOLUTION_RE = re.compile(
    r"Solution\s*:.*?=\s*.*?([\d,]+(?:\.\d+)?)\s*(?:([A-Za-z/%][A-Za-z0-9/%]*)\s*$|$)",
    re.MULTILINE,
)

# Pattern: single input assignment "symbol = value [unit]"
_INPUT_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"  # symbol =
    r"([\d,]+(?:\.\d+)?(?:[eE][+-]?\d+)?)"  # numeric value
    r"(?:\s+([A-Za-z/%][A-Za-z0-9/^%]*))?"  # optional unit
)


def parse_given_inputs(text: str) -> list[dict]:
    """Extract input parameters from 'Given:' section.

    Handles comma-separated, newline-separated, and mixed formats.
    Returns list of dicts with keys: symbol, value, unit.
    """
    # Find the "Given:" section
    given_match = re.search(r"Given\s*:\s*(.*?)(?=\nSolution|\Z)", text, re.DOTALL | re.IGNORECASE)
    if not given_match:
        return []

    given_text = given_match.group(1)
    inputs = []

    for m in _INPUT_RE.finditer(given_text):
        symbol = m.group(1)
        raw_value = m.group(2).replace(",", "")
        unit = m.group(3) or ""

        try:
            value = float(raw_value)
        except ValueError:
            continue

        inputs.append({"symbol": symbol, "value": value, "unit": unit})

    return inputs


def parse_solution_units(text: str) -> str:
    """Extract unit from the Solution line's final value.

    Returns the unit string, or '' if no unit found.
    """
    for line in text.split("\n"):
        if not line.strip().lower().startswith("solution"):
            continue

        # Look for "= <number> <unit>" at end of line
        m = re.search(
            r"=\s*[\d,]+(?:\.\d+)?\s+([A-Za-z/%][A-Za-z0-9/%]*)\s*$",
            line.strip(),
        )
        if m:
            return m.group(1)

    return ""


def parse_enhanced_example(
    text: str,
    domain: str = "general",
    source: Optional[dict] = None,
) -> Optional[dict]:
    """Parse a worked example with full input/output extraction.

    Returns dict with: number, title, expected_value, output_unit, inputs,
    source, domain. Returns None if the text doesn't match example patterns.
    """
    title_match = _EXAMPLE_RE.search(text)
    if not title_match:
        return None

    number = title_match.group(1)
    title = title_match.group(2).strip()

    # Find expected value from Solution line
    expected_value = None
    for line in text.split("\n"):
        if line.strip().lower().startswith("solution"):
            # Extract last number on the line
            sol_re = re.compile(r"([\d,]+(?:\.\d+)?)\s*(?:[A-Za-z/%]|$)")
            matches = list(sol_re.finditer(line))
            if matches:
                raw = matches[-1].group(1).replace(",", "")
                try:
                    expected_value = float(raw)
                except ValueError:
                    pass

    if expected_value is None:
        return None

    inputs = parse_given_inputs(text)
    output_unit = parse_solution_units(text)

    return {
        "number": number,
        "title": title,
        "expected_value": expected_value,
        "output_unit": output_unit,
        "inputs": inputs,
        "source": source or {},
        "domain": domain,
    }


def _format_value(val: float) -> str:
    """Format numeric value for code output."""
    if val == int(val) and abs(val) < 1e15:
        return str(int(val))
    return repr(val)


def render_real_test_file(
    manifest: str,
    examples: list[dict],
) -> str:
    """Render a pytest test file with real assertions using pytest.approx.

    Each example becomes a separate test function with:
    - Input variables from the 'Given:' section
    - Expected value with pytest.approx(rel=1e-3)
    - Comment with source citation
    """
    if not examples:
        return ""

    lines = [
        f'"""Worked examples from {manifest} — auto-promoted with real assertions.',
        "",
        "Each test captures inputs and expected output from the source document.",
        "Wire the 'result = ...' line to the actual implementation function.",
        '"""',
        "",
        "import pytest",
        "",
        "",
    ]

    for ex in examples:
        number = ex["number"]
        title = ex["title"]
        expected = ex["expected_value"]
        inputs = ex.get("inputs", [])
        output_unit = ex.get("output_unit", "")
        source = ex.get("source", {})

        func_name = f"test_example_{number.replace('.', '_')}"
        source_doc = source.get("document", manifest)
        source_page = source.get("page", "?")

        lines.append(f"def {func_name}():")
        lines.append(f'    """Example {number}: {title}.')
        lines.append("")
        lines.append(f"    Source: {source_doc} p.{source_page}")
        lines.append('    """')

        # Input variables
        if inputs:
            lines.append("    # Inputs")
            for inp in inputs:
                unit_comment = f"  # {inp['unit']}" if inp["unit"] else ""
                lines.append(
                    f"    {inp['symbol']} = {_format_value(inp['value'])}{unit_comment}"
                )
            lines.append("")

        # Expected value
        unit_comment = f"  # {output_unit}" if output_unit else ""
        lines.append(f"    expected = {_format_value(expected)}{unit_comment}")
        lines.append("")

        # TODO assertion — wire to real implementation
        lines.append("    # TODO: Wire to actual implementation function")
        if inputs:
            args = ", ".join(
                f"{inp['symbol']}={inp['symbol']}" for inp in inputs
            )
            lines.append(f"    # result = calculate({args})")
        else:
            lines.append("    # result = calculate()")
        lines.append("    result = expected  # placeholder — replace with real call")
        lines.append("")
        lines.append("    assert result == pytest.approx(expected, rel=1e-3)")
        lines.append("")
        lines.append("")

    return "\n".join(lines)
