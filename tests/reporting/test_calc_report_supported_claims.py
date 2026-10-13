"""Tests for supported role claims and illustrative calc-report notices."""

import subprocess
from html import escape as html_escape
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


def _generate_both(input_path, output_dir):
    from generate_calc_report import generate_report

    html_path = output_dir / "out.html"
    md_path = output_dir / "out.md"
    generate_report(str(input_path), output_path=str(html_path))
    generate_report(str(input_path), fmt="md", output_path=str(md_path))
    return md_path.read_text(encoding="utf-8"), html_path.read_text(encoding="utf-8")


def _write_input(tmp_path, data):
    path = tmp_path / "input.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def _git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    return repo


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
    assert "<strong>Status:</strong> verified" not in html


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
        "XLSX Auto-Extraction (WRK-1247)",
        "xlsx-poc-v2 pipeline",
        "Test Author",
        "Reviewer 1",
        "Independent Checker",
        "QA Reviewer",
        "TBC",
        "To be confirmed",
        "ChatGPT",
        "gpt4",
        "Python",
        "Excel",
        "calc_module.py",
        "noreply@<vendor>.com",
        "QA Dept",
        "",
        "   ",
        r"Example\Name",
        "Example Team",
    ],
)
def test_non_person_author_is_omitted(author):
    data = _base_data()
    data["metadata"]["author"] = author

    markdown, html = _render_both(data)

    assert "Author" not in markdown
    assert "<strong>Author</strong>" not in html
    if author.strip():
        assert author not in markdown
        assert author not in html


@pytest.mark.parametrize(
    "author",
    [
        "A. Example",
        "Example-Synthetic",
        "O'Example",
        "Example",
        "例子",
        "Пример",
        "مثال",
        "Claude Example",
    ],
)
def test_person_author_is_printed(author):
    with_author = _base_data()
    with_author["metadata"]["author"] = author
    markdown, html = _render_both(with_author)
    assert author in markdown
    assert html_escape(author) in html


def test_missing_author_builds():

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


def test_computed_by_suppresses_line_without_reference_in_both_outputs(tmp_path):
    repo = _git_repo(tmp_path)
    module = repo / "calc_module.py"
    module.write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "calc_module.py"], cwd=repo, check=True)
    data = _base_data()
    data["metadata"]["computed_by"] = "calc_module.py"
    input_path = _write_input(repo, data)

    markdown, html = _generate_both(input_path, tmp_path)

    assert ILLUSTRATIVE_LINE not in markdown
    assert ILLUSTRATIVE_LINE not in html
    assert "Computed by" not in markdown
    assert "Computed by" not in html
    assert "calc_module.py" not in markdown
    assert "calc_module.py" not in html


@pytest.mark.parametrize(
    "computed_by, setup",
    [
        ("", None),
        ("missing.py", None),
        ("calc_module.py", "untracked"),
        ("ignored.py", "ignored"),
        ("input.yaml", "input"),
        (".git/HEAD", None),
        ("README.md", "tracked_md"),
    ],
)
def test_invalid_computed_by_raises_validation_error(tmp_path, computed_by, setup):
    repo = _git_repo(tmp_path)
    data = _base_data()
    data["metadata"]["computed_by"] = computed_by
    input_path = _write_input(repo, data)
    if setup == "untracked":
        (repo / computed_by).write_text("VALUE = 1\n", encoding="utf-8")
    elif setup == "ignored":
        (repo / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
        (repo / computed_by).write_text("VALUE = 1\n", encoding="utf-8")
    elif setup == "tracked_md":
        (repo / computed_by).write_text("# Synthetic\n", encoding="utf-8")
        subprocess.run(["git", "add", computed_by], cwd=repo, check=True)

    from generate_calc_report import generate_report

    with pytest.raises(ValueError, match="metadata.computed_by"):
        generate_report(str(input_path), output_path=str(tmp_path / "out.html"))


def test_computed_by_outside_checkout_keeps_sentence_and_warns(tmp_path, capsys):
    data = _base_data()
    data["metadata"]["computed_by"] = "calc_module.py"
    input_path = _write_input(tmp_path, data)

    markdown, html = _generate_both(input_path, tmp_path)

    assert ILLUSTRATIVE_LINE in markdown
    assert ILLUSTRATIVE_LINE in html
    warning = capsys.readouterr().err
    assert "metadata.computed_by" in warning
    assert "calc_module.py" not in warning


def test_unquoted_yaml_dates_print_roles_and_verification(tmp_path):
    data = _base_data()
    data["metadata"]["status"] = "approved"
    data["metadata"]["reviewer"] = {"name": "A. Example", "date": "2026-02-01"}
    data["metadata"]["approver"] = {"name": "B. Example", "date": "2026-02-02"}
    data["verification"] = {
        "checker": "C. Example",
        "date": "2026-02-03",
        "method": "Synthetic comparison",
        "status": "verified",
    }
    input_path = _write_input(tmp_path, data)

    markdown, html = _generate_both(input_path, tmp_path)

    assert "Reviewer: A. Example (2026-02-01)" in markdown
    assert "Approver: B. Example (2026-02-02)" in markdown
    assert "**Checker:** C. Example (2026-02-03)" in markdown
    assert "<strong>Reviewer</strong>A. Example (2026-02-01)" in html
    assert "<strong>Approver</strong>B. Example (2026-02-02)" in html
    assert "<strong>Checker:</strong> C. Example (2026-02-03)" in html


def test_datetime_yaml_values_omit_roles_and_statuses(tmp_path, capsys):
    input_path = tmp_path / "input.yaml"
    input_path.write_text(
        """
metadata:
  title: Synthetic Check
  doc_id: SYN-001
  revision: 1
  date: '2026-01-01'
  status: approved
  reviewer:
    name: A. Example
    date: 2026-02-01 01:02:03
  approver:
    name: B. Example
    date: 2026-02-02 01:02:03
inputs:
  - name: Load
    symbol: P
    value: 100
    unit: kN
methodology:
  description: Synthetic method.
  standard: Synthetic criterion
  equations:
    - id: 1
      name: Unity
      latex: UC = P/R
      description: Synthetic ratio.
outputs:
  - name: Unity
    symbol: UC
    value: 0.5
    unit: '-'
verification:
  checker: C. Example
  date: 2026-02-03 01:02:03
  method: Synthetic comparison
  status: verified
""",
        encoding="utf-8",
    )

    markdown, html = _generate_both(input_path, tmp_path)

    assert "Reviewer:" not in markdown
    assert "Approver:" not in markdown
    assert "**Status:** APPROVED" not in markdown
    assert "**Checker:**" not in markdown
    assert "\n**Status:** verified" not in markdown
    assert "Synthetic comparison" in markdown
    assert "<strong>Reviewer</strong>" not in html
    assert "<strong>Approver</strong>" not in html
    assert "<strong>Status</strong><span" not in html
    assert "<strong>Checker:</strong>" not in html
    assert "<strong>Status:</strong> verified" not in html
    assert "Synthetic comparison" in html
    warning = capsys.readouterr().err
    assert warning.count("metadata.status") == 2
    assert warning.count("verification.status") == 2


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
