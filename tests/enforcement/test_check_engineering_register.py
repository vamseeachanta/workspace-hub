from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def load_checker():
    path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "enforcement"
        / "check-engineering-register.py"
    )
    spec = importlib.util.spec_from_file_location("check_engineering_register", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def findings_for(tmp_path: Path, body: str) -> list[str]:
    checker = load_checker()
    path = tmp_path / "note.md"
    path.write_text(body, encoding="utf-8", newline="\n")
    return checker.check(path)


def test_existing_self_test_counts_stay_exact(tmp_path: Path) -> None:
    checker = load_checker()
    for name, (body, expected) in checker.SELF_TEST.items():
        path = tmp_path / f"{name}.md"
        path.write_text(body, encoding="utf-8", newline="\n")
        assert len(checker.check(path)) == expected, name


def test_url_slug_masks_intensifier_but_prose_still_reports(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "Reference: https://example.org/reports/definitely-reviewed\n"
        "The result is definitely complete.\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R1.2]" in findings[0]


def test_markdown_link_target_masks_first_person_visible_text_is_prose(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "[the analysis](https://example.org/reports/our-review)\n"
        "[our analysis](https://example.org/reports/the-analysis)\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R6]" in findings[0]


def test_inline_code_span_masks_unsupported_adjective_but_prose_reports(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "The token ``the estimate is conservative`` is read from source text.\n"
        "The estimate is conservative.\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R3]" in findings[0]


def test_single_backtick_span_masks_first_person_but_prose_reports(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "The token `our` is read from source text.\n"
        "Our review records the finding.\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R6]" in findings[0]


# These pin unchanged behaviour: unbalanced backticks do not start masking.
def test_lone_backtick_leaves_following_prose_checked(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "The token ` source text is recorded. Our review records the finding.\n",
    )
    assert len(findings) == 1
    assert ":1:" in findings[0]
    assert "[R6]" in findings[0]


# These pin unchanged behaviour: unbalanced backticks do not start masking.
def test_unclosed_double_backtick_leaves_following_prose_checked(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "The token `` source text is recorded.\n"
        "Our review records the finding.\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R6]" in findings[0]


def test_angle_bracket_link_masks_first_person_but_prose_reports(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "<https://example.net/reports/our-review>\n"
        "Our review records the finding.\n",
    )
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert "[R6]" in findings[0]


def test_first_person_masks_inside_url_and_code_but_not_prose(tmp_path: Path) -> None:
    findings = findings_for(
        tmp_path,
        "Reference: https://example.org/reports/our-review\n"
        "The token ``our`` is read from source text.\n"
        "Our review records the finding.\n",
    )
    assert len(findings) == 1
    assert ":3:" in findings[0]
    assert "[R6]" in findings[0]


def test_url_and_prose_occurrence_preserves_prose_column(tmp_path: Path) -> None:
    checker = load_checker()
    body = (
        "Reference https://example.org/reports/our-review; "
        "our review records the finding.\n"
    )
    masked = checker.prose_only(body)
    match = next(checker.FIRST_PERSON.finditer(masked))
    assert match.start() == body.index("our review")


# Source: issue #3835, acceptance criteria and minimal pairs (2026).
# Expected counts below are hand classifications: a claim with a same-sentence
# criterion contributes no finding; each bare claim contributes its rule once.
@pytest.mark.parametrize(
    "body",
    [
        "Manual pulls are safe because the agent no longer reads FETCH_HEAD.",
        "Because the agent no longer reads FETCH_HEAD, manual pulls are safe.",
        "The grade is not obviously correct since the mill certificate is absent.",
        "Since the mill certificate is absent, the grade is not obviously correct.",
        "Per the inspection record, the result is acceptable.",
        "The result is acceptable per the inspection record.",
        "Against the allowable, the estimate remains conservative.",
        "The estimate remains conservative against the allowable.",
        "By design, the grade is not necessarily correct.",
        "The grade is not necessarily correct by design.",
        # Reference numbering comes from the existing criterion_named fixture.
        "Per Table 4.1, the result is acceptable.",
        "The result is acceptable per Table 4.1.",
        "Per Table 4.1, the grade is not obviously correct.",
        "The grade is not obviously correct per Table 4.1.",
    ],
)
def test_criterion_in_either_clause_order(tmp_path: Path, body: str) -> None:
    """Hand oracle: the one claim has a criterion, so there are no findings."""
    assert findings_for(tmp_path, body) == []


@pytest.mark.parametrize(
    ("claim", "code"),
    [
        ("Manual pulls are safe now", "R3"),
        ("The grade is not obviously correct", "R5"),
    ],
)
@pytest.mark.parametrize("boundary", [". ", "! ", "? ", "\n\n", "\n \t\n"])
@pytest.mark.parametrize("criterion_first", [True, False])
@pytest.mark.parametrize(
    "criterion",
    ["The inspection records the governing criterion", "The inspection cites Table 4.1"],
)
def test_adjacent_sentence_criterion_does_not_suppress(
    tmp_path: Path, claim: str, code: str, boundary: str, criterion_first: bool,
    criterion: str,
) -> None:
    """Hand oracle: only the bare claim contributes one finding of its rule.

    Issue #3835 bounds scope in both directions. Blank paragraphs also separate
    Markdown prose blocks even when the preceding paragraph has no full stop.
    """
    parts = [criterion, claim] if criterion_first else [claim, criterion]
    findings = findings_for(tmp_path, boundary.join(parts) + ".")
    assert len(findings) == 1
    assert f"[{code}]" in findings[0]


@pytest.mark.parametrize(
    "body",
    [
        "Because the inspection record is complete,\nmanual pulls are safe.",
        "The grade is not obviously correct\nsince the mill certificate is absent.",
        "Since the mill certificate is absent,\nthe grade is not obviously correct.",
        "Manual pulls are safe\nbecause the agent no longer reads FETCH_HEAD.",
    ],
)
def test_wrapped_sentence_keeps_criterion(tmp_path: Path, body: str) -> None:
    """Hand oracle: a soft line wrap keeps the criterion with its one claim."""
    assert findings_for(tmp_path, body) == []


@pytest.mark.parametrize(
    ("body", "code"),
    [
        (("Because the record is complete, manual pulls are safe.\n"
          "Manual pulls are safe now.\n"), "R3"),
        (("Since the certificate is absent, the grade is not obviously correct.\n"
          "The grade is not obviously correct.\n"), "R5"),
    ],
)
def test_justified_and_bare_claims_produce_different_output(
    tmp_path: Path, body: str, code: str
) -> None:
    """Hand oracle: the first claim is justified; only line two is reported."""
    findings = findings_for(tmp_path, body)
    assert len(findings) == 1
    assert ":2:" in findings[0]
    assert f"[{code}]" in findings[0]


@pytest.mark.parametrize(
    "claim", ["Manual pulls are safe", "The grade is not obviously correct"]
)
@pytest.mark.parametrize("criterion_first", [True, False])
def test_criterion_scope_has_no_character_window(
    tmp_path: Path, claim: str, criterion_first: bool
) -> None:
    """Hand oracle: repeating neutral words does not change the sentence.

    The repetition deliberately exceeds the legacy regex windows; it is a test
    construction, not an engineering coefficient or an acceptance threshold.
    """
    padding = "the inspection record notes that " * 12
    body = (
        "Because " + padding + "the record is complete, " + claim + "."
        if criterion_first
        else claim + " " + padding + "because the record is complete."
    )
    assert findings_for(tmp_path, body) == []


@pytest.mark.parametrize(
    "body",
    [
        "The estimate is conservative: failure is contained by the barrier.",
        "The estimate is conservative and analogous to a screen-out.",
        "Manufacture does not obviously fit: the items exceed the window.",
        "Manufacture does not obviously fit — the items exceed the window.",
        # The reference numbering follows the existing criterion_named fixture.
        "Item 4.1 does not obviously fit: the items exceed the window.",
        "The item does not obviously fit 4.1:\nthe items exceed the window.",
    ],
)
def test_existing_explanatory_forms_still_pass(tmp_path: Path, body: str) -> None:
    """Hand oracle from existing rule comments: the explanation is explicit."""
    assert findings_for(tmp_path, body) == []


@pytest.mark.parametrize(
    ("body", "code"),
    [
        ("`Because the record is complete`, manual pulls are safe.", "R3"),
        ("The grade is not obviously correct. `since the record is absent`", "R5"),
    ],
)
def test_masked_criterion_cannot_justify_prose(
    tmp_path: Path, body: str, code: str
) -> None:
    """Hand oracle: inline code is excluded evidence; the prose claim is bare."""
    findings = findings_for(tmp_path, body)
    assert len(findings) == 1
    assert f"[{code}]" in findings[0]


def test_worked_example_cli_reports_only_bare_claims(tmp_path: Path, capsys) -> None:
    """Independent hand count for the guide's example, from issue #3835 (2026).

    Lines one and two explain the claim with 'Because' and 'Since': no findings.
    Line three is a bare 'are safe': one R3. Line four is a bare 'not obviously':
    one R5. Summing those classifications gives two findings at lines three and
    four; none of the other register rules matches these impersonal sentences.
    """
    checker = load_checker()
    path = tmp_path / "example.md"
    path.write_text(
        "Because the agent no longer reads FETCH_HEAD, manual pulls are safe.\n"
        "Since the mill certificate is absent, the grade is not obviously correct.\n"
        "Manual pulls are safe now.\n"
        "The grade is not obviously correct.\n",
        encoding="utf-8", newline="\n",
    )
    assert checker.main(["check-engineering-register.py", str(path)]) == 1
    output = capsys.readouterr().out
    assert ":3: [R3]" in output
    assert ":4: [R5]" in output
    assert "1 file(s) checked, 2 violation(s)" in output


@pytest.mark.parametrize(
    ("body", "codes"),
    [
        ("The estimate is conservative", ["R3"]),
        ("The result is acceptable.", ["R3"]),
        ("The record was decoded, so manual pulls are safe.", ["R3"]),
        ("The grade is not obviously correct", ["R5"]),
        ("The estimate is conservative while the method is acceptable.", ["R3", "R3"]),
    ],
)
def test_bare_claims_remain_reported(tmp_path: Path, body: str, codes: list[str]) -> None:
    """Hand count: every unqualified claim contributes one specified finding."""
    findings = findings_for(tmp_path, body)
    assert len(findings) == len(codes)
    for finding, code in zip(findings, codes):
        assert f"[{code}]" in finding


@pytest.mark.parametrize("code,claim", [
    ("R3", "Manual pulls are safe now"),
    ("R5", "The grade is not obviously correct"),
])
@pytest.mark.parametrize("criterion_first", [True, False])
@pytest.mark.parametrize("excluded", ["url", "quotation"])
@pytest.mark.parametrize("stop", [".", "?", "!"])
def test_exclusions_preserve_sentence_boundaries(
    tmp_path: Path, code: str, claim: str, criterion_first: bool,
    excluded: str, stop: str,
) -> None:
    """Hand oracle: the adjacent sentence cannot justify the bare claim."""
    ending = (
        "https:" + "/" * 2 + "example.org/record" + stop
        if excluded == "url" else '"the record is complete' + stop + '"'
    )
    reason = "The criterion is recorded at " + ending
    parts = [reason, claim + "."] if criterion_first else [claim + " " + ending, reason]
    findings = findings_for(tmp_path, "\n".join(parts))
    assert len(findings) == 1
    assert f"[{code}]" in findings[0]
    assert f":{2 if criterion_first else 1}:" in findings[0]


@pytest.mark.parametrize("claim,code", [
    ("The result is safe", "R3"),
    ("The result is not obviously correct", "R5"),
])
@pytest.mark.parametrize("token", ["codec", "tablet", "standardized", "limited", "basisless"])
@pytest.mark.parametrize("token_first", [True, False])
def test_criterion_prefixes_do_not_justify_claims(
    tmp_path: Path, claim: str, code: str, token: str, token_first: bool,
) -> None:
    """Hand oracle: an unrelated word is not a named criterion."""
    body = f"The {token} exists and {claim}." if token_first else f"{claim} with the {token}."
    findings = findings_for(tmp_path, body)
    assert len(findings) == 1
    assert f"[{code}]" in findings[0]


@pytest.mark.parametrize("token", [
    "criterion", "criteria", "limit", "limits", "thresholds", "allowable",
    "basis", "bases", "code", "codes", "standard", "standards", "Reference",
    "references", "Table", "tables", "Section", "sections",
])
@pytest.mark.parametrize("claim", ["The result is safe", "The result is not obviously correct"])
def test_complete_criterion_words_still_qualify(tmp_path: Path, token: str, claim: str) -> None:
    """Hand oracle: an explicitly named criterion qualifies either rule."""
    assert findings_for(tmp_path, f"The {token} governs and {claim}.") == []
