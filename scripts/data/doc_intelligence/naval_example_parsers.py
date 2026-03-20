"""Multi-format worked example parsers for naval architecture textbooks.

Three parser strategies for distinct textbook formats:
- Format A (EN400/DNV): ``Example N.N <title>`` + ``Given:`` + ``Solution:``
- Format B (Tupper/Biran): ``Example N.N[ - title]`` (no colon) + prose + ``Solution``
- Format C (Attwood/PNA): Inline ``Example.`` with prose calculations

Usage:
    from scripts.data.doc_intelligence.naval_example_parsers import (
        parse_examples_multi_format,
    )
    results = parse_examples_multi_format(text, source, domain)
"""

import re
from typing import Protocol

from scripts.data.doc_intelligence.worked_example_parser import (
    parse_given_inputs,
    parse_prose_inputs,
    parse_solution_units,
)


class ExampleParserStrategy(Protocol):
    """Protocol for format-specific worked example parsers."""

    def can_parse(self, text: str) -> bool: ...
    def parse(self, text: str, source: dict, domain: str) -> list[dict]: ...


# ── Shared helpers ──────────────────────────────────────────────────

_LAST_NUMBER_RE = re.compile(
    r"([\d,]+(?:\.\d+)?)\s*([A-Za-z/%][A-Za-z0-9/²³^%]*)?",
)

_LAST_EQUALS_RE = re.compile(
    r"=\s*([\d,]+(?:\.\d+)?)\s*([A-Za-z/%][A-Za-z0-9/²³^%]*(?:\s+[a-z/][a-z0-9/]*)*)?",
)


def _extract_final_answer(text: str) -> tuple[float | None, str]:
    """Extract the last ``= value [unit]`` from text."""
    matches = list(_LAST_EQUALS_RE.finditer(text))
    if not matches:
        return None, ""
    m = matches[-1]
    raw = m.group(1).replace(",", "")
    unit = (m.group(2) or "").strip()
    try:
        return float(raw), unit
    except ValueError:
        return None, ""


def _build_result(
    number: str, title: str, source: dict, domain: str,
    expected: float, unit: str, inputs: list[dict], fmt: str,
) -> dict:
    page = source.get("page", 0)
    has_numerical_input = any(
        isinstance(i.get("value"), (int, float)) for i in inputs
    )
    return {
        "number": number,
        "title": title,
        "source_book": source.get("document", ""),
        "page": page,
        "parser_format": fmt,
        "inputs": inputs,
        "expected_value": expected,
        "output_unit": unit,
        "use_as_test": has_numerical_input and expected is not None,
        "domain": domain,
    }


# ── Format A: EN400 / DNV ──────────────────────────────────────────

# "Example N.N <title>" — title must be on same line as number
_FMT_A_RE = re.compile(
    r"Example[ \t]+([\d]+(?:\.[\d]+)*)[ \t]+([A-Z].+?)(?:\.\s|\.$|$)",
    re.IGNORECASE | re.MULTILINE,
)


class EN400Parser:
    """Parses ``Example N.N <title>`` with optional Given/Solution."""

    def can_parse(self, text: str) -> bool:
        m = _FMT_A_RE.search(text)
        if not m:
            return False
        has_given = bool(re.search(r"\bGiven\s*:", text, re.IGNORECASE))
        has_solution_colon = bool(
            re.search(r"\bSolution\s*:", text, re.IGNORECASE)
        )
        has_title_after_number = bool(m.group(2).strip())
        return has_given or has_solution_colon or has_title_after_number

    def parse(self, text: str, source: dict, domain: str) -> list[dict]:
        m = _FMT_A_RE.search(text)
        if not m:
            return []
        number = m.group(1)
        title = m.group(2).strip().rstrip(".")
        inputs = parse_given_inputs(text)
        if not inputs:
            inputs = parse_prose_inputs(text)
        unit = parse_solution_units(text)
        expected, eq_unit = _extract_final_answer(text)
        if expected is None:
            return []
        if not unit and eq_unit:
            unit = eq_unit
        return [_build_result(
            number, title, source, domain,
            expected, unit, inputs, "en400_dnv",
        )]


# ── Format B: Tupper / Biran ───────────────────────────────────────

# "Example N.N" or "Example N.N - Title" (no colon after number)
_FMT_B_RE = re.compile(
    r"Example\s+([\d]+(?:\.[\d]+)*)\s*(?:-\s*(.+?))?$",
    re.MULTILINE,
)
_FMT_B_SOLUTION = re.compile(r"^Solution\s*$", re.MULTILINE | re.IGNORECASE)


class TupperBiranParser:
    """Parses ``Example N.N[ - title]`` + prose + ``Solution``."""

    def can_parse(self, text: str) -> bool:
        has_example = bool(_FMT_B_RE.search(text))
        has_solution = bool(_FMT_B_SOLUTION.search(text))
        no_given_colon = not bool(
            re.search(r"\bGiven\s*:", text, re.IGNORECASE)
        )
        return has_example and has_solution and no_given_colon

    def parse(self, text: str, source: dict, domain: str) -> list[dict]:
        m = _FMT_B_RE.search(text)
        if not m:
            return []
        number = m.group(1)
        title = (m.group(2) or "").strip()
        if not title:
            end = m.end()
            next_lines = text[end:end + 200].strip().split("\n")
            prose = " ".join(
                ln.strip() for ln in next_lines[:3] if ln.strip()
            )
            title = prose[:80].rstrip(".")

        sol_match = _FMT_B_SOLUTION.search(text)
        if not sol_match:
            return []
        solution_text = text[sol_match.start():]
        expected, unit = _extract_final_answer(solution_text)
        if expected is None:
            return []
        inputs = parse_prose_inputs(text)
        return [_build_result(
            number, title, source, domain,
            expected, unit, inputs, "tupper_biran",
        )]


# ── Format C: Attwood / PNA ────────────────────────────────────────

_FMT_C_RE = re.compile(
    r"Example\.\s+(.+?)(?:\n\n|\Z)",
    re.DOTALL,
)


class AttwoodPNAParser:
    """Parses inline ``Example. <prose>`` with embedded answer."""

    def can_parse(self, text: str) -> bool:
        has_example_dot = bool(re.search(r"Example\.\s", text))
        no_numbered = not bool(
            re.search(r"Example\s+\d+\.\d+", text, re.IGNORECASE)
        )
        return has_example_dot and no_numbered

    def parse(self, text: str, source: dict, domain: str) -> list[dict]:
        m = _FMT_C_RE.search(text)
        if not m:
            return []
        preamble = m.group(1).strip()
        title = preamble[:80].rstrip(".")
        expected, unit = _extract_final_answer(text)
        if expected is None:
            return []
        page = source.get("page", 0)
        number = f"p{page}" if page else "inline"
        inputs = parse_prose_inputs(text)
        return [_build_result(
            number, title, source, domain,
            expected, unit, inputs, "attwood_pna",
        )]


# ── Dispatcher ──────────────────────────────────────────────────────

_PARSERS: list[ExampleParserStrategy] = [
    EN400Parser(),
    TupperBiranParser(),
    AttwoodPNAParser(),
]


def parse_examples_multi_format(
    text: str,
    source: dict,
    domain: str,
) -> list[dict]:
    """Try all parser strategies; return results from first match."""
    for parser in _PARSERS:
        if parser.can_parse(text):
            results = parser.parse(text, source, domain)
            if results:
                return results
    return []
