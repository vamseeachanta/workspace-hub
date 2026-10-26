"""Literal verdict regressions for issue #1736.

Alias inventory: issue #1736, "Observed Verdict Strings".
Canonical-label basis: scripts/review/normalize-verdicts.sh, explicit-header
mapping and severity rules; tests/review/test_verdict_normalization.py provides
existing REQUEST_CHANGES, changes-requested, REVISION NEEDED and No findings
examples. Expected labels below are independent literals, never parser output.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


NORMALIZER = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts" / "review" / "normalize-verdicts.sh"
)

# Every distinct alias in the issue's observed list. PENDING has no supported
# mapping: a complete review passes structural validation and falls back to ERROR
# (normalize-verdicts.sh, final validation branch). It is not a new enum member.
ISSUE_VERDICT_ALIASES = (
    ("APPROVE", "APPROVE"),
    ("MINOR", "MINOR"),
    ("MAJOR", "MAJOR"),
    ("REVISION NEEDED", "MAJOR"),
    ("REVISE", "MAJOR"),
    ("changes-requested", "MAJOR"),
    ("Request changes", "MAJOR"),
    ("REQUEST_CHANGES", "MAJOR"),
    ("changes_requested", "MAJOR"),
    ("No findings", "APPROVE"),
    ("PENDING", "ERROR"),
)

# Remaining spellings from normalize-verdicts.sh's explicit-header case table.
# In particular, REJECT remains MAJOR; this suite does not migrate the vocabulary.
COMPATIBILITY_ALIASES = (
    ("REQUEST-CHANGES", "MAJOR"),
    ("REJECT", "MAJOR"),
    ("APPROVED", "APPROVE"),
    ("PASS", "APPROVE"),
    ("no_findings", "APPROVE"),
    ("CONDITIONAL_PASS", "CONDITIONAL_PASS"),
    ("CONDITIONAL-PASS", "CONDITIONAL_PASS"),
    ("CONDITIONAL PASS", "CONDITIONAL_PASS"),
    ("NO_OUTPUT", "NO_OUTPUT"),
    ("NO OUTPUT", "NO_OUTPUT"),
)


def _review(
    verdict_lines: str,
    *,
    summary: str = "Synthetic review of an isolated change.",
    issues: str = "- None.",
) -> str:
    """Supply all sections required by validate-review-output.sh."""
    return f"""{verdict_lines}
### Summary
{summary}
### Issues Found
{issues}
### Suggestions
- Resolve any listed findings.
### Questions for Author
- None.
"""


def _normalize(tmp_path: Path, review: str) -> str:
    review_file = tmp_path / "review.md"
    review_file.write_text(review, encoding="utf-8")
    result = subprocess.run(
        ["bash", str(NORMALIZER), str(review_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stderr == ""
    return result.stdout


@pytest.mark.parametrize("alias, expected", ISSUE_VERDICT_ALIASES)
def test_issue_verdict_alias_matrix(tmp_path, alias, expected):
    assert _normalize(tmp_path, _review(f"### Verdict: {alias}")) == f"{expected}\n"


@pytest.mark.parametrize("alias, expected", COMPATIBILITY_ALIASES)
def test_documented_compatibility_alias_matrix(tmp_path, alias, expected):
    assert _normalize(tmp_path, _review(f"### Verdict: {alias}")) == f"{expected}\n"


# Header forms follow normalize-verdicts.sh's explicit-header expression.
@pytest.mark.parametrize(
    "header",
    (
        "Verdict: aPpRoVe",
        "Verdict = APPROVE",
        "### Verdict: APPROVE",
        "**Verdict:** APPROVE",
        "### **Verdict:** APPROVE",
    ),
)
def test_explicit_header_forms(tmp_path, header):
    assert _normalize(tmp_path, _review(header)) == "APPROVE\n"


# The explicit-header precedence contract applies even when fallback keywords
# such as conditional_pass occur in prose before and after the selected verdict.
@pytest.mark.parametrize(
    "alias, expected",
    (
        ("APPROVE", "APPROVE"),
        ("MINOR", "MINOR"),
        ("MAJOR", "MAJOR"),
        ("REJECT", "MAJOR"),
        ("CONDITIONAL_PASS", "CONDITIONAL_PASS"),
        ("NO_OUTPUT", "NO_OUTPUT"),
    ),
)
def test_explicit_verdict_beats_body_mentions(tmp_path, alias, expected):
    prose = (
        "The example mentions APPROVE, MINOR, MAJOR, REJECT, conditional_pass "
        "and NO_OUTPUT. A quoted Verdict: REQUEST_CHANGES is explanatory prose."
    )
    review = prose + "\n" + _review(
        f"### Verdict: {alias}", summary=prose, issues=f"- {prose}"
    )
    assert _normalize(tmp_path, review) == f"{expected}\n"


# Pipe-separated templates are ignored by both the explicit-header selector and
# structural validator. A complete template alone is INVALID_OUTPUT, not a vote.
@pytest.mark.parametrize(
    "headers, expected",
    (
        ("### Verdict: APPROVE | REQUEST_CHANGES | REJECT", "INVALID_OUTPUT"),
        ("Verdict: APPROVE | MINOR | MAJOR", "INVALID_OUTPUT"),
        ("**Verdict:** APPROVE | REQUEST_CHANGES | REJECT", "INVALID_OUTPUT"),
        (
            "### Verdict: APPROVE\n### Verdict: APPROVE | REQUEST_CHANGES | REJECT",
            "APPROVE",
        ),
        (
            "### Verdict: APPROVE | REQUEST_CHANGES | REJECT\n### Verdict: APPROVE",
            "APPROVE",
        ),
    ),
)
def test_template_options_do_not_count_as_verdict(tmp_path, headers, expected):
    assert _normalize(tmp_path, _review(headers)) == f"{expected}\n"


# The selector retains the last explicit non-template verdict header.
@pytest.mark.parametrize(
    "headers, expected",
    (
        ("### Verdict: REJECT\n### Verdict: APPROVE", "APPROVE"),
        ("### Verdict: APPROVE\n### Verdict: REJECT", "MAJOR"),
    ),
)
def test_last_explicit_header_wins(tmp_path, headers, expected):
    assert _normalize(tmp_path, _review(headers)) == f"{expected}\n"


# Empty/whitespace input is ERROR in normalize-verdicts.sh's initial guard.
@pytest.mark.parametrize("review", ("", " \t\n\n"))
def test_empty_input_is_error(tmp_path, review):
    assert _normalize(tmp_path, review) == "ERROR\n"


# P1/P2 map to MAJOR, P3 alone to MINOR; P1/P2 take precedence over P3.
# Source: normalize-verdicts.sh's severity branch, also exercised for P1/P2 in
# test_verdict_normalization.py. Untagged requests retain the MAJOR default.
@pytest.mark.parametrize("alias", ("REQUEST_CHANGES", "REQUEST-CHANGES", "Request changes"))
@pytest.mark.parametrize(
    "issues, expected",
    (
        ("- [P1] Synthetic blocking finding.", "MAJOR"),
        ("- [P2] Synthetic correctness finding.", "MAJOR"),
        ("- [P3] Synthetic presentation finding.", "MINOR"),
        ("- [P3] Presentation finding.\n- [P2] Correctness finding.", "MAJOR"),
        ("- [p3] Presentation finding.\n- [p1] Blocking finding.", "MAJOR"),
        ("- Untagged synthetic finding.", "MAJOR"),
    ),
)
def test_request_changes_severity_mapping(tmp_path, alias, issues, expected):
    review = _review(f"### Verdict: {alias}", issues=issues)
    assert _normalize(tmp_path, review) == f"{expected}\n"
