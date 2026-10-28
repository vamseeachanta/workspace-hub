"""Literal verdict regressions for issue #1736.

Independent expectation specification (compatibility scope)
=========================================================
This specification defines the expected results for this test module. It is a
reviewable test oracle, authored separately from the parser's control flow;
no expectation is obtained by running or inspecting a parser branch at runtime.
Issue #1736 supplies the alias inventory, not the mappings. The mappings below
specify the retained compatibility behavior, not the proposed enum migration.
The independently specified examples here are the basis for the literal cases.

C1: Alias expectations (complete review, no severity tags)
    Input spelling(s)                                      Expected label
    APPROVE, APPROVED, PASS, No findings, no_findings         APPROVE
    MINOR                                                   MINOR
    MAJOR, REVISION NEEDED, REVISE, REJECT                    MAJOR
    changes-requested, changes_requested                     MAJOR
    Request changes, REQUEST_CHANGES, REQUEST-CHANGES         MAJOR
    CONDITIONAL_PASS, CONDITIONAL-PASS, CONDITIONAL PASS      CONDITIONAL_PASS
    NO_OUTPUT, NO OUTPUT                                    NO_OUTPUT
    PENDING                                                 ERROR
    PENDING expresses no completed decision, so a complete review with only
    that label is an error; it must not be accepted as an approval or new enum.
    REJECT retains MAJOR compatibility rather than introducing a new label.

C2: Header forms
    Verdict: aPpRoVe; Verdict = APPROVE; ### Verdict: APPROVE;
    **Verdict:** APPROVE; ### **Verdict:** APPROVE -> APPROVE individually.
    Case and these presentation forms must not alter the decision.

C3: Header precedence
    An explicit header determines the label despite verdict words in prose.
    Example: ### Verdict: MINOR with conditional_pass in the summary -> MINOR.
    Apply C1 equally to APPROVE, MINOR, MAJOR, REJECT, CONDITIONAL_PASS and
    NO_OUTPUT when the surrounding prose mentions competing verdict words.

C4: Templates
    A pipe-separated option list is not a decision. A complete review containing
    only Verdict: APPROVE | MINOR | MAJOR -> INVALID_OUTPUT (also for the
    REQUEST_CHANGES/REJECT options and Markdown header/bold presentation).
    A real APPROVE header before or after an option list -> APPROVE.

C5: Repeated headers
    The final non-template explicit decision supersedes earlier decisions:
    REJECT then APPROVE -> APPROVE; APPROVE then REJECT -> MAJOR.

C6: Empty input
    Empty or whitespace-only text -> ERROR because no decision is supplied.

C7: Severity
    For REQUEST_CHANGES, REQUEST-CHANGES and Request changes, P1 or P2 -> MAJOR;
    P3 alone -> MINOR; P3 plus P1/P2 -> MAJOR regardless of tag case; an untagged
    finding -> MAJOR. Blocking findings must dominate presentation findings.

Each case cites C1-C7 below; all expected labels remain literal constants.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


NORMALIZER = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts" / "review" / "normalize-verdicts.sh"
)

# Oracle: C1; every distinct alias in the issue's observed list.
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

# Oracle: C1; remaining compatibility spellings, including REJECT -> MAJOR.
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
    review_file.write_text(review, encoding="utf-8", newline="\n")
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


# Oracle: C2; presentation and case must preserve the explicit decision.
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


# Oracle: C3; prose before and after a header must not override its decision.
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


# Oracle: C4; option lists alone supply no decision; real headers still count.
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


# Oracle: C5; a later real decision supersedes an earlier one.
@pytest.mark.parametrize(
    "headers, expected",
    (
        ("### Verdict: REJECT\n### Verdict: APPROVE", "APPROVE"),
        ("### Verdict: APPROVE\n### Verdict: REJECT", "MAJOR"),
    ),
)
def test_last_explicit_header_wins(tmp_path, headers, expected):
    assert _normalize(tmp_path, _review(headers)) == f"{expected}\n"


# Oracle: C6; absent decisions must produce ERROR.
@pytest.mark.parametrize("review", ("", " \t\n\n"))
def test_empty_input_is_error(tmp_path, review):
    assert _normalize(tmp_path, review) == "ERROR\n"


# Oracle: C7; blocking severity dominates presentation severity.
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
