from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_checker():
    path = Path("scripts/enforcement/check-engineering-register.py")
    spec = importlib.util.spec_from_file_location("check_engineering_register", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def findings_for(tmp_path: Path, body: str) -> list[str]:
    checker = load_checker()
    path = tmp_path / "note.md"
    path.write_text(body, encoding="utf-8")
    return checker.check(path)


def test_existing_self_test_counts_stay_exact(tmp_path: Path) -> None:
    checker = load_checker()
    for name, (body, expected) in checker.SELF_TEST.items():
        path = tmp_path / f"{name}.md"
        path.write_text(body, encoding="utf-8")
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
