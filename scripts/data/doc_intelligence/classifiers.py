"""Heuristic content-type classifiers for document sections.

Each classifier returns True if the section matches its content type.
Priority order: requirements > worked_examples > constants > equations >
procedures > definitions. First match wins.
"""

import re
from typing import Optional

from scripts.data.doc_intelligence.schema import ExtractedSection

# Pre-compiled patterns
_SYMBOL_EQUALS_VALUE = re.compile(
    r"[A-Za-z_]\w*\s*=\s*[\d.]+\s*[a-zA-Z]"
)
_CONSTANT_KEYWORDS = re.compile(r"\bconstant\b", re.IGNORECASE)
_CONSTANT_HEADING = re.compile(r"\bconstant", re.IGNORECASE)

_EQUATION_EXPR = re.compile(
    r"[A-Za-z_]\w*\s*=\s*[A-Za-z_]\w*\s*[+\-*/]"
)
_EQUATION_KEYWORDS = re.compile(
    r"\b(equation|formula)\b", re.IGNORECASE
)

_REQUIREMENT_KEYWORDS = re.compile(
    r"\b(shall|must|required)\b", re.IGNORECASE
)
_REQUIREMENT_HEADING = re.compile(r"\brequirement", re.IGNORECASE)

_PROCEDURE_STEPS = re.compile(
    r"(?:step\s+\d|^\s*\d+\.\s+\w)", re.IGNORECASE | re.MULTILINE
)
_PROCEDURE_HEADING = re.compile(r"\bprocedure\b", re.IGNORECASE)

_DEFINITION_KEYWORDS = re.compile(
    r"\b(means|is defined as|refers to)\b", re.IGNORECASE
)
_DEFINITION_HEADING = re.compile(r"\bdefinition", re.IGNORECASE)

_EXAMPLE_KEYWORDS = re.compile(
    r"(?:\bexample\s*:|sample calculation|worked example)", re.IGNORECASE
)
_GIVEN_FIND = re.compile(
    r"\bgiven\b.*\bfind\b", re.IGNORECASE | re.DOTALL
)
_EXAMPLE_HEADING = re.compile(
    r"\b(worked example|example)\b", re.IGNORECASE
)


def _is_requirements(section: ExtractedSection) -> bool:
    if section.heading and _REQUIREMENT_HEADING.search(section.heading):
        return True
    return bool(_REQUIREMENT_KEYWORDS.search(section.text))


def _is_constants(section: ExtractedSection) -> bool:
    if section.heading and _CONSTANT_HEADING.search(section.heading):
        return True
    if _CONSTANT_KEYWORDS.search(section.text):
        return True
    return bool(_SYMBOL_EQUALS_VALUE.search(section.text))


def _is_equations(section: ExtractedSection) -> bool:
    if _EQUATION_KEYWORDS.search(section.text):
        return True
    return bool(_EQUATION_EXPR.search(section.text))


def _is_procedures(section: ExtractedSection) -> bool:
    if section.heading and _PROCEDURE_HEADING.search(section.heading):
        return True
    return bool(_PROCEDURE_STEPS.search(section.text))


def _is_definitions(section: ExtractedSection) -> bool:
    if section.heading and _DEFINITION_HEADING.search(section.heading):
        return True
    return bool(_DEFINITION_KEYWORDS.search(section.text))


def _is_worked_examples(section: ExtractedSection) -> bool:
    if section.heading and _EXAMPLE_HEADING.search(section.heading):
        return True
    if _EXAMPLE_KEYWORDS.search(section.text):
        return True
    return bool(_GIVEN_FIND.search(section.text))


# Priority-ordered classifier chain
_CLASSIFIERS = [
    ("requirements", _is_requirements),
    ("worked_examples", _is_worked_examples),
    ("constants", _is_constants),
    ("equations", _is_equations),
    ("procedures", _is_procedures),
    ("definitions", _is_definitions),
]


def classify_section(section: ExtractedSection) -> Optional[str]:
    """Classify a section into a content type. Returns None if unclassified."""
    if not section.text.strip():
        return None
    for content_type, checker in _CLASSIFIERS:
        if checker(section):
            return content_type
    return None
