"""Renderer CLI regressions using independently authored review examples.

The review objects and literal Markdown expectations below are synthetic test
examples authored together. No expected result is obtained from the renderer,
provider output, existing fixtures, submitters, or validators.

Scope is limited to this test file; the renderer is exercised unchanged.
Two valid examples across four representations provide eight exact-output cases.
Eleven invalid examples across three representations provide 33 rejection cases.
Acceptance requires successful status, literal Markdown equality and no stderr
for valid input. Rejection requires nonzero status, no stdout and a diagnostic.

Offline command (direct temporary files to external scratch with --basetemp):
uv run --offline --no-project --with pytest python -m pytest
tests/review/test_render_structured_review.py -q -rA -p no:cacheprovider
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


RENDERER = (
    Path(__file__).resolve().parent.parent.parent
    / "scripts"
    / "review"
    / "render-structured-review.py"
)

REVIEW = {
    "verdict": "MAJOR",
    "summary": "The input contract needs a correction.",
    "issues_found": [
        "An empty document can conceal a missing review.",
        "A partial document lacks the required summary.",
    ],
    "suggestions": ["Reject incomplete documents before rendering."],
    "questions_for_author": ["Is the failure status preserved by the caller?"],
}

EXPECTED_REVIEW = """### Verdict: MAJOR

### Summary
The input contract needs a correction.

### Issues Found
- An empty document can conceal a missing review.
- A partial document lacks the required summary.

### Suggestions
- Reject incomplete documents before rendering.

### Questions for Author
- Is the failure status preserved by the caller?
"""

CLEAN_REVIEW = {
    "verdict": "APPROVE",
    "summary": "The supplied review is complete.",
    "issues_found": [],
    "suggestions": [],
    "questions_for_author": [],
}

EXPECTED_CLEAN_REVIEW = """### Verdict: APPROVE

### Summary
The supplied review is complete.

### Issues Found
- None.

### Suggestions
- None.

### Questions for Author
- None.
"""


def _supplied_text(review_text: str, representation: str) -> str:
    if representation in {"fenced", "envelope-fenced"}:
        review_text = f"```json\n{review_text}\n```"
    if representation in {"envelope", "envelope-fenced"}:
        return json.dumps({"response": review_text})
    return review_text


def _render(tmp_path: Path, supplied_text: str) -> subprocess.CompletedProcess[str]:
    input_file = tmp_path / "review-input.txt"
    input_file.write_text(supplied_text, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            "--provider",
            "gemini",
            "--input",
            str(input_file),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("review", "expected"),
    [
        pytest.param(REVIEW, EXPECTED_REVIEW, id="findings"),
        pytest.param(CLEAN_REVIEW, EXPECTED_CLEAN_REVIEW, id="clean"),
    ],
)
@pytest.mark.parametrize(
    "representation", ["plain", "fenced", "envelope", "envelope-fenced"]
)
def test_gemini_envelope_and_fenced_review(tmp_path, review, expected, representation):
    supplied_text = _supplied_text(json.dumps(review), representation)

    result = _render(tmp_path, supplied_text)

    # os.EX_OK names the standard successful process status without a magic value.
    assert result.returncode == os.EX_OK
    assert result.stdout == expected
    assert not result.stderr


@pytest.mark.parametrize("representation", ["plain", "envelope", "envelope-fenced"])
@pytest.mark.parametrize(
    "review_text",
    [
        pytest.param("", id="empty"),
        pytest.param(" \n\t", id="whitespace"),
        pytest.param("Review service is unavailable.", id="banner"),
        pytest.param('{"verdict":', id="malformed"),
        pytest.param("{}", id="empty-object"),
        pytest.param('{"verdict": "APPROVE"}', id="verdict-only"),
        *[
            pytest.param(
                json.dumps({key: value for key, value in REVIEW.items() if key != missing}),
                id=f"missing-{missing}",
            )
            for missing in (
                "verdict",
                "summary",
                "issues_found",
                "suggestions",
                "questions_for_author",
            )
        ],
    ],
)
def test_invalid_review_cannot_become_success(tmp_path, review_text, representation):
    result = _render(tmp_path, _supplied_text(review_text, representation))

    # Snapshot only status and presence so assertion introspection cannot expose
    # rejected text through the captured process representation.
    returncode = result.returncode
    has_output = bool(result.stdout)
    has_diagnostic = bool(result.stderr)

    assert returncode != os.EX_OK
    # Reject any partial output, including an apparently valid Verdict section.
    assert not has_output
    # Do not compare diagnostics with rejected input bytes or echo them on failure.
    assert has_diagnostic
