# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Parse engineering standard references into structured data.

Supports: DNV, API, ISO, ASME, NORSOK, IEC, ABS, BV, LR.

Usage:
    uv run --no-project python parse_standard_reference.py --input refs.txt
    uv run --no-project python parse_standard_reference.py --input refs.txt --output out.yaml
    cat refs.txt | uv run --no-project python parse_standard_reference.py
"""

from __future__ import annotations

import re
import sys
import argparse
from typing import Optional

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
ParsedRef = dict  # keys: body, code, section, edition, year, title


def _make_ref(
    body: str,
    code: str,
    section: Optional[str] = None,
    edition: Optional[str] = None,
    year: Optional[int] = None,
    title: Optional[str] = None,
) -> ParsedRef:
    return {
        "body": body,
        "code": code,
        "section": section,
        "edition": edition,
        "year": year,
        "title": title,
    }


# ---------------------------------------------------------------------------
# Section suffix — optional trailing " Section X.Y.Z"
# ---------------------------------------------------------------------------
_SECTION_SUFFIX = r"(?:\s+[Ss]ection\s+([\d.]+))?"

# ---------------------------------------------------------------------------
# Per-body patterns
# Each entry: (body_label, compiled_regex, extractor_callable)
# The extractor receives the match object and returns a ParsedRef or None.
# ---------------------------------------------------------------------------

def _dnv_extractor(m: re.Match) -> ParsedRef:
    type_code = m.group(1)   # e.g. RP-C205, ST-F101
    section = m.group(2)
    return _make_ref("DNV", type_code, section=section)


_DNV_PATTERN = re.compile(
    r"\bDNV-((?:RP|ST|OS|SE|GL|CG|CP|AS|CE|GF|PN|SR|FP)-[A-Z0-9]+)"
    + _SECTION_SUFFIX,
    re.IGNORECASE,
)


def _api_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1).strip()
    edition = m.group(2)  # e.g. "22nd"
    return _make_ref("API", code, edition=edition)


# API RP 2A-WSD 22nd Ed. | API RP 2GEO | API Spec 5L | API Std 1104
_API_PATTERN = re.compile(
    r"\bAPI\s+((?:RP|Spec|STD|Std|SPEC|Bull|Publ|TR)\s+[A-Z0-9][-A-Z0-9]*)"
    r"(?:\s+(\d+(?:st|nd|rd|th))\s+Ed(?:ition|\.))?"
    + _SECTION_SUFFIX,
    re.IGNORECASE,
)


def _iso_extractor(m: re.Match) -> ParsedRef:
    num = m.group(1)    # e.g. 19901-1  or  19906
    year_str = m.group(2)
    year = int(year_str) if year_str else None
    return _make_ref("ISO", num, year=year)


_ISO_PATTERN = re.compile(
    r"\bISO\s+(\d+(?:-\d+)*)(?::(\d{4}))?"
    + _SECTION_SUFFIX,
)


def _asme_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1)
    return _make_ref("ASME", code)


_ASME_PATTERN = re.compile(
    r"\bASME\s+([A-Z]\d+[A-Z0-9]*(?:-[A-Z0-9]+)*)"
    + _SECTION_SUFFIX,
)


def _norsok_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1)
    return _make_ref("NORSOK", code)


_NORSOK_PATTERN = re.compile(
    r"\bNORSOK\s+([A-Z]-\d+(?:\s+Rev\.\s*\d+)?)"
    + _SECTION_SUFFIX,
    re.IGNORECASE,
)


def _iec_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1)
    year_str = m.group(2)
    year = int(year_str) if year_str else None
    return _make_ref("IEC", code, year=year)


_IEC_PATTERN = re.compile(
    r"\bIEC\s+(\d+(?:-\d+)*)(?::(\d{4}))?"
    + _SECTION_SUFFIX,
)


def _abs_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1).strip()
    return _make_ref("ABS", code)


# ABS Rules for Building and Classing | ABS Guide for ... | ABS Guidance Notes
_ABS_PATTERN = re.compile(
    r"\bABS\s+((?:Rules?|Guide(?:lines?)?|Guidance\s+Notes?)"
    r"(?:\s+for\s+[\w\s,&'-]+?)?)"
    r"(?=\s*[.,;()\n]|$)",
    re.IGNORECASE,
)


def _bv_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1).strip()
    return _make_ref("BV", code)


# BV NR 445 | BV Rules
_BV_PATTERN = re.compile(
    r"\bBV\s+((?:NR|Rules?|Part)\s+[A-Z0-9]+(?:\s+[A-Z0-9]+)?)"
    r"(?=\s*[.,;()\n]|$)",
    re.IGNORECASE,
)


def _lr_extractor(m: re.Match) -> ParsedRef:
    code = m.group(1).strip()
    return _make_ref("LR", code)


# LR Rules | LR Rules and Regulations
_LR_PATTERN = re.compile(
    r"\bLR\s+(Rules?(?:\s+and\s+Regulations?)?)"
    r"(?=\s*[.,;()\n]|$)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Registry: ordered so greedier / more-specific patterns run first
# ---------------------------------------------------------------------------
_PARSERS: list[tuple[re.Pattern, callable]] = [
    (_DNV_PATTERN, _dnv_extractor),
    (_API_PATTERN, _api_extractor),
    (_ISO_PATTERN, _iso_extractor),
    (_ASME_PATTERN, _asme_extractor),
    (_NORSOK_PATTERN, _norsok_extractor),
    (_IEC_PATTERN, _iec_extractor),
    (_ABS_PATTERN, _abs_extractor),
    (_BV_PATTERN, _bv_extractor),
    (_LR_PATTERN, _lr_extractor),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_reference(text: str) -> Optional[ParsedRef]:
    """Parse a single standard reference string.

    Returns a dict with keys body, code, section, edition, year, title,
    or None if no recognised reference is found.
    """
    text = text.strip()
    for pattern, extractor in _PARSERS:
        m = pattern.search(text)
        if m:
            return extractor(m)
    return None


def extract_all_references(text: str) -> list[ParsedRef]:
    """Find all standard references in a block of text.

    Returns a deduplicated list of parsed reference dicts, preserving
    order of first occurrence.
    """
    results: list[ParsedRef] = []
    seen: set[tuple] = set()

    for pattern, extractor in _PARSERS:
        for m in pattern.finditer(text):
            ref = extractor(m)
            key = (ref["body"], ref["code"], ref["section"])
            if key not in seen:
                seen.add(key)
                results.append(ref)

    # Sort by position of first match to preserve reading order
    def _first_pos(ref: ParsedRef) -> int:
        for pattern, _ in _PARSERS:
            m = pattern.search(text)
            if m:
                candidate = _make_ref_key_from_pattern(pattern, m)
                if candidate == (ref["body"], ref["code"], ref["section"]):
                    return m.start()
        return 0

    # Build position index
    pos_map: dict[tuple, int] = {}
    for pattern, extractor in _PARSERS:
        for m in pattern.finditer(text):
            ref = extractor(m)
            key = (ref["body"], ref["code"], ref["section"])
            if key not in pos_map:
                pos_map[key] = m.start()

    results.sort(key=lambda r: pos_map.get((r["body"], r["code"], r["section"]), 0))
    return results


def _make_ref_key_from_pattern(
    pattern: re.Pattern,
    m: re.Match,
) -> tuple:
    """Helper — not part of public API."""
    for p, extractor in _PARSERS:
        if p is pattern:
            ref = extractor(m)
            return (ref["body"], ref["code"], ref["section"])
    return ("", "", None)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse engineering standard references from text."
    )
    parser.add_argument(
        "--input",
        "-i",
        metavar="FILE",
        help="Input text file (default: stdin)",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output YAML file (default: stdout as YAML)",
    )
    args = parser.parse_args()

    if args.input:
        with open(args.input, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()

    refs = extract_all_references(text)

    import yaml  # deferred — only needed for CLI

    yaml_str = yaml.dump(refs, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(yaml_str)
        print(f"Wrote {len(refs)} reference(s) to {args.output}", file=sys.stderr)
    else:
        print(yaml_str)


if __name__ == "__main__":
    main()
