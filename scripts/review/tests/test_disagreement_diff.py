"""Direct renderer regressions for issue #3537; all review data is synthetic.

The date and issue fixture tokens follow test_disagreement_report_captures_unique_finding
in test_plan_review_fanout.sh. Expected reports are composed by hand: both
reviews declare MAJOR and share a finding, so only the alpha finding is unique.
No fanout, submitter or provider executable is invoked.
"""

import subprocess
from pathlib import Path

import pytest


RENDERER = Path(__file__).resolve().parent.parent / "lib/disagreement-diff.sh"
DATE = "2026-04-17"
ISSUE = "8888"
HEADING_CASES = [
    ("Verdict", "Findings"),
    ("VERDICT", "FINDINGS"),
    ("verdict", "findings"),
    ("vErDiCt ", "fInDiNgS\t"),
    ("VeRdIcT\t ", "FiNdInGs \t"),
]


def render(tmp_path, reviews):
    for provider, review in reviews.items():
        (tmp_path / f"{DATE}-plan-{ISSUE}-{provider}.md").write_text(
            review, encoding="utf-8"
        )
    return subprocess.run(
        ["bash", str(RENDERER), str(tmp_path), DATE, ISSUE],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


@pytest.mark.parametrize("verdict_heading,findings_heading", HEADING_CASES)
def test_heading_cases_render_identical_verdicts_and_findings(
    tmp_path, verdict_heading, findings_heading
):
    common = f"## {verdict_heading}\n\nMAJOR\n\n## {findings_heading}\n- Shared finding\n"
    report = render(
        tmp_path,
        {"alpha": common + "- Alpha finding\n", "beta": common},
    )
    assert report == f"""# Disagreement report — plan #{ISSUE} ({DATE})

## Verdicts

| Provider | Verdict |
|---|---|
| alpha | MAJOR |
| beta | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### alpha

- Alpha finding

### beta

(no findings unique to this provider)

"""


@pytest.mark.parametrize(
    "heading",
    ["", "Verdict", "Text mentions ## Verdict", "## Verdictology", "## VERDICT notes"],
)
def test_missing_or_inexact_verdict_heading_stays_unknown(tmp_path, heading):
    report = render(tmp_path, {"alpha": f"{heading}\nMAJOR\n\n## Findings\n(none)\n"})
    assert "| alpha | UNKNOWN |" in report
    assert "| alpha | MAJOR |" not in report


@pytest.mark.parametrize(
    "heading",
    ["", "Findings", "Text mentions ## Findings", "## Findingsology", "## FINDINGS notes"],
)
def test_missing_or_inexact_findings_heading_has_no_findings(tmp_path, heading):
    report = render(
        tmp_path,
        {"alpha": f"## Verdict\nMINOR\n\n{heading}\n- Alpha finding\n"},
    )
    assert "| alpha | MINOR |" in report
    assert "- Alpha finding" not in report
    assert "### alpha\n\n(no findings unique to this provider)\n" in report


@pytest.mark.parametrize("verdict_heading,findings_heading", HEADING_CASES)
def test_empty_verdict_stops_at_next_section(tmp_path, verdict_heading, findings_heading):
    report = render(
        tmp_path,
        {"alpha": f"## {verdict_heading}\n\n## {findings_heading}\nMAJOR\n"},
    )
    assert "| alpha | UNKNOWN |" in report
    assert "| alpha | MAJOR |" not in report


@pytest.mark.parametrize("verdict_heading,findings_heading", HEADING_CASES)
def test_findings_stop_at_next_section(tmp_path, verdict_heading, findings_heading):
    report = render(
        tmp_path,
        {
            "alpha": (
                f"## {verdict_heading}\nMINOR\n\n## {findings_heading}\n"
                "- Alpha finding\n\n## Notes\nUnrelated section text\n"
            )
        },
    )
    assert "| alpha | MINOR |" in report
    assert "- Alpha finding" in report
    assert "Unrelated section text" not in report
    assert "## Notes" not in report
