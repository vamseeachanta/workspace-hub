"""Keyword labels and precedence specified by issues/121.

The new field is independent of the existing weighted tier and provider scores.
"""

import json
import subprocess
from pathlib import Path

import pytest


LIBRARY = (
    Path(__file__).resolve().parents[2]
    / "scripts/coordination/routing/lib/task_classifier.sh"
)

# Source: issues/121, routine and complex keyword lists (no score thresholds).
ROUTINE_KEYWORDS = ("format", "config", "rename", "copy", "update-doc", "scaffold")
COMPLEX_KEYWORDS = ("architecture", "cross-repo", "security", "design")
KEYWORD_LABELS = [(word, "routine") for word in ROUTINE_KEYWORDS] + [
    (word, "complex") for word in COMPLEX_KEYWORDS
]
DEFAULT_DESCRIPTIONS = (
    "",
    " \t\n",
    "calculate totals",
    "implement a parser",
    "'quoted' \"$value\"; $(false)\ncheck totals",
)


def classify(description):
    # Arguments keep task text literal, including quotes and shell syntax.
    result = subprocess.run(
        [
            "bash", "--noprofile", "--norc", "-c",
            'source "$1"; classify_task "$2"',
            "classifier-test", str(LIBRARY), description,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("keyword, expected", KEYWORD_LABELS)
@pytest.mark.parametrize(
    "case", (str.lower, str.upper, str.title), ids=("lower", "upper", "mixed")
)
def test_issue_keyword_labels(keyword, expected, case):
    assert classify(f"Please {case(keyword)} this task.")["complexity_tier"] == expected


@pytest.mark.parametrize("description", DEFAULT_DESCRIPTIONS)
def test_unmatched_defaults_to_standard(description):
    # Source: issues/121, unmatched descriptions default to standard.
    assert classify(description)["complexity_tier"] == "standard"


@pytest.mark.parametrize("routine", ROUTINE_KEYWORDS)
@pytest.mark.parametrize("complex_keyword", COMPLEX_KEYWORDS)
@pytest.mark.parametrize(
    "complex_first", (False, True), ids=("routine-first", "complex-first")
)
def test_complex_takes_precedence(routine, complex_keyword, complex_first):
    # Source: issues/121, complex wins when both keyword groups match.
    words = (
        (complex_keyword.upper(), routine)
        if complex_first else (routine, complex_keyword.upper())
    )
    description = "Please " + " and ".join(words) + " this task."
    assert classify(description)["complexity_tier"] == "complex"
