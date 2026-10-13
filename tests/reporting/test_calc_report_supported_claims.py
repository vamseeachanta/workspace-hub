"""Tests for supported role claims and illustrative calc-report notices."""

from pathlib import Path

import pytest
import yaml


ILLUSTRATIVE_LINE = (
    "Illustrative example: values are typed inputs for demonstration, "
    "not a project calculation."
)


def _base_data():
    return {
        "metadata": {
            "title": "Synthetic Check",
            "doc_id": "SYN-001",
            "revision": 1,
            "date": "2026-01-01",
            "status": "draft",
        },
        "inputs": [
            {"name": "Load", "symbol": "P", "value": 100, "unit": "kN"},
        ],
        "methodology": {
            "description": "Synthetic method.",
            "standard": "Synthetic criterion",
            "equations": [
                {
                    "id": 1,
                    "name": "Unity",
                    "latex": "UC = P/R",
                    "description": "Synthetic ratio.",
                },
            ],
        },
        "outputs": [
            {"name": "Unity", "symbol": "UC", "value": 0.5, "unit": "-"},
        ],
        "references": ["Synthetic reference"],
    }


def _render_both(data):
    from generate_calc_report import load_and_validate, render_html, render_markdown

    checked = load_and_validate(data)
    markdown = render_markdown(checked)
    return markdown, render_html(checked, markdown)


def _write_input(tmp_path, data):
    path = tmp_path / "input.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_plain_string_reviewer_is_omitted_and_warns_once(capsys):
    data = _base_data()
    data["metadata"]["reviewer"] = "Reviewer"

    markdown, html = _render_both(data)

    assert "Reviewer" not in markdown
    assert "<strong>Reviewer</strong>" not in html
    warning = capsys.readouterr().err
    assert "metadata.reviewer" in warning
    assert "Reviewer" not in warning


@pytest.mark.parametrize("role_key", ["reviewer", "approver"])
def test_role_word_mapping_with_date_is_omitted(role_key):
    data = _base_data()
    data["metadata"][role_key] = {"name": "Independent Reviewer", "date": "2026-02-01"}

    markdown, html = _render_both(data)

    assert "Independent Reviewer" not in markdown
    assert "Independent Reviewer" not in html
    assert role_key.title() not in markdown
    assert f"<strong>{role_key.title()}</strong>" not in html


@pytest.mark.parametrize("role_key", ["reviewer", "approver"])
def test_person_role_mapping_with_date_is_printed(role_key):
    data = _base_data()
    data["metadata"][role_key] = {"name": "A. Example", "date": "2026-02-01"}

    markdown, html = _render_both(data)

    assert f"{role_key.title()}: A. Example (2026-02-01)" in markdown
    assert "A. Example" in html
    assert "2026-02-01" in html


@pytest.mark.parametrize(
    "role_value",
    [
        {"name": "A. Example"},
        {"name": "A. Example", "date": "not-a-date"},
    ],
)
def test_role_mapping_without_iso_date_is_omitted(role_value):
    data = _base_data()
    data["metadata"]["reviewer"] = role_value

    markdown, html = _render_both(data)

    assert "Reviewer" not in markdown
    assert "<strong>Reviewer</strong>" not in html


def test_checker_requires_person_name_and_verification_date():
    data = _base_data()
    data["verification"] = {
        "checker": "A. Example",
        "date": "2026-02-01",
        "method": "Synthetic independent check",
        "status": "verified",
    }

    markdown, html = _render_both(data)

    assert "Checker:** A. Example (2026-02-01)" in markdown
    assert "A. Example" in html
    assert "Synthetic independent check" in html
    assert "verified" in html


def test_program_checker_is_omitted_but_verification_card_stays():
    data = _base_data()
    data["verification"] = {
        "checker": "solver v2.21",
        "date": "2026-02-01",
        "method": "Synthetic comparison",
        "status": "verified",
    }

    markdown, html = _render_both(data)

    assert "Checker" not in markdown
    assert "<strong>Checker:</strong>" not in html
    assert "Synthetic comparison" in markdown
    assert "Synthetic comparison" in html
    assert "verified" in html


def test_verification_without_checker_builds():
    data = _base_data()
    data["verification"] = {
        "date": "2026-02-01",
        "method": "Synthetic comparison",
        "status": "verified",
    }

    markdown, html = _render_both(data)

    assert "Checker" not in markdown
    assert "<strong>Checker:</strong>" not in html
    assert "Synthetic comparison" in html


@pytest.mark.parametrize(
    "author",
    [
        "Generator (automated)",
        "GPT model",
        "repo/name",
        "Example Engineering",
    ],
)
def test_non_person_author_is_omitted(author):
    data = _base_data()
    data["metadata"]["author"] = author

    markdown, html = _render_both(data)

    assert "Author" not in markdown
    assert "<strong>Author</strong>" not in html
    assert author not in markdown
    assert author not in html


def test_person_author_is_printed_and_missing_author_builds():
    with_author = _base_data()
    with_author["metadata"]["author"] = "A. Example"
    markdown, html = _render_both(with_author)
    assert "A. Example" in markdown
    assert "A. Example" in html

    without_author = _base_data()
    markdown, html = _render_both(without_author)
    assert "Author" not in markdown
    assert "<strong>Author</strong>" not in html


def test_illustrative_line_is_first_text_after_title():
    markdown, html = _render_both(_base_data())

    assert markdown.count(ILLUSTRATIVE_LINE) == 1
    lines = [line for line in markdown.splitlines() if line.strip()]
    assert lines[0] == "# Synthetic Check"
    assert lines[1] == ILLUSTRATIVE_LINE

    assert html.count(ILLUSTRATIVE_LINE) == 1
    title_index = html.index('<h1 class="report-title">Synthetic Check</h1>')
    line_index = html.index(ILLUSTRATIVE_LINE)
    chips_index = html.index('<div class="meta-chips">')
    assert title_index < line_index < chips_index


def test_computed_by_suppresses_line_and_adds_reference(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    module = repo / "calc_module.py"
    module.write_text("VALUE = 1\n", encoding="utf-8")
    data = _base_data()
    data["metadata"]["computed_by"] = "calc_module.py"
    input_path = _write_input(repo, data)
    html_path = tmp_path / "out.html"

    from generate_calc_report import generate_report

    generate_report(str(input_path), output_path=str(html_path))
    html = html_path.read_text(encoding="utf-8")

    assert ILLUSTRATIVE_LINE not in html
    assert "Computed by: calc_module.py" in html


@pytest.mark.parametrize("computed_by", ["", "missing.py"])
def test_invalid_computed_by_raises_validation_error(tmp_path, computed_by):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    data = _base_data()
    data["metadata"]["computed_by"] = computed_by
    input_path = _write_input(repo, data)

    from generate_calc_report import generate_report

    with pytest.raises(ValueError, match="metadata.computed_by"):
        generate_report(str(input_path), output_path=str(tmp_path / "out.html"))


def test_removed_wording_search_over_generated_pages():
    cases = []
    for field, value in [
        ("reviewer", "Independent Reviewer"),
        ("author", "Generator (automated)"),
        ("author", "repo/name"),
        ("author", "Example Engineering"),
    ]:
        data = _base_data()
        data["metadata"][field] = value
        cases.append(data)

    checker_case = _base_data()
    checker_case["verification"] = {
        "checker": "solver v2.21",
        "date": "2026-02-01",
        "method": "Synthetic comparison",
        "status": "verified",
    }
    cases.append(checker_case)

    rendered = "\n".join(
        "\n".join(_render_both(data))
        for data in cases
    )
    lowered = rendered.lower()
    assert "independent reviewer" not in lowered
    assert "reviewer" not in lowered
    assert "checker" not in lowered
    assert "approver" not in lowered
    assert "(automated)" not in lowered
    assert "author" not in lowered
