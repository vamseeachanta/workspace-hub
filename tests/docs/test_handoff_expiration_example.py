"""Execute the documentation recipe; dates below use independent calendar sums.

Retention authority: durable-vs-transient-knowledge-boundary.md, sections 8.1
and 8.4. All timestamps and issue references are synthetic fixtures.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


EXAMPLE = (
    Path(__file__).resolve().parents[2]
    / "docs/document-intelligence/handoff-expiration-example.md"
)


@pytest.fixture
def run_recipe(tmp_path):
    text = EXAMPLE.read_text(encoding="utf-8")
    recipes = re.findall(r"^```python\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    assert len(recipes) == 1, "The example must contain one executable recipe"

    def run(rows):
        result = subprocess.run(
            [sys.executable, "-c", recipes[0]],
            input=json.dumps(rows), text=True, capture_output=True,
            cwd=tmp_path, check=True, timeout=10,
        )
        assert not result.stderr
        assert not list(tmp_path.iterdir()), "The recipe must not write files"
        return json.loads(result.stdout)

    return run


def row(**changes):
    item = {
        "handoff_at": "2028-01-01T06:00:00Z",
        "issue_ref": "synthetic-issue",
        "issue_state": "open",
        "closed_at": None,
    }
    return item | changes


def expected(state, expires_at=None):
    return {
        "state": state, "expires_at": expires_at, "advisory": True,
        "cleanup_eligibility": "not_assessed", "cleanup_authority": False,
    }


def test_open_issue_has_no_expiry(run_recipe):
    assert run_recipe([row()]) == [expected("open_issue")]


def test_closed_issue_retention_date(run_recipe):
    # Section 8.1: 30 days. Jan 31 -> Feb 29 = 29 days in leap year 2028;
    # the remaining day reaches Mar 1, preserving the UTC time of day.
    item = row(issue_state="closed", closed_at="2028-01-31T12:00:00Z")
    assert run_recipe([item]) == [
        expected("closed_issue", "2028-03-01T12:00:00Z")
    ]


def test_no_issue_fallback_date(run_recipe):
    # Sections 8.1/8.4: 90 days. Nov 30 -> Dec 31 (31), -> Jan 31 (31),
    # -> Feb 28 (28): 31 + 31 + 28 = 90, across the year boundary.
    item = row(
        handoff_at="2027-11-30T06:00:00Z", issue_ref=None, issue_state=None,
    )
    assert run_recipe([item]) == [
        expected("no_issue_fallback", "2028-02-28T06:00:00Z")
    ]


@pytest.mark.parametrize("timestamp", [
    None, "unknown", "2028-02-30T12:00:00Z", "2028-01-31T12:00:00", 42,
])
@pytest.mark.parametrize("basis", ["closure", "handoff"])
def test_unknown_timestamp_has_no_date_or_cleanup_authority(
    run_recipe, timestamp, basis,
):
    if basis == "closure":
        item = row(issue_state="closed", closed_at=timestamp)
    else:
        item = row(handoff_at=timestamp, issue_ref=None, issue_state=None)
    assert run_recipe([item]) == [expected("unknown")]


@pytest.mark.parametrize("changes", [
    {"closed_at": "2028-01-31T12:00:00Z"},
    {"issue_ref": None},
    {"issue_ref": None, "issue_state": None,
     "closed_at": "2028-01-31T12:00:00Z"},
])
def test_conflicting_metadata_has_no_date_or_authority(run_recipe, changes):
    assert run_recipe([row(**changes)]) == [expected("conflicting_metadata")]


@pytest.mark.parametrize("state", [None, "unknown", "unexpected"])
def test_unknown_linked_issue_state_does_not_use_fallback(run_recipe, state):
    assert run_recipe([row(issue_state=state)]) == [expected("unknown")]


@pytest.mark.parametrize("reference", ["", " ", 42])
def test_ambiguous_reference_is_not_no_issue(run_recipe, reference):
    item = row(issue_ref=reference, issue_state=None)
    assert run_recipe([item]) == [expected("unknown")]


def test_missing_reference_is_not_no_issue(run_recipe):
    item = row(issue_state=None)
    del item["issue_ref"]
    assert run_recipe([item]) == [expected("unknown")]


def test_offset_is_normalized_to_utc(run_recipe):
    # Same independent leap-year sum as the closed-issue case; +02:00 means
    # 14:00 local is 12:00 UTC, so the expected UTC instant remains unchanged.
    item = row(issue_state="closed", closed_at="2028-01-31T14:00:00+02:00")
    assert run_recipe([item]) == [
        expected("closed_issue", "2028-03-01T12:00:00Z")
    ]


def test_documented_input_output_rows_match_recipe(run_recipe):
    text = EXAMPLE.read_text(encoding="utf-8")
    blocks = re.findall(r"^```json\n(.*?)^```$", text, re.MULTILINE | re.DOTALL)
    inputs, outputs = map(json.loads, blocks)
    assert outputs == [
        expected("open_issue"),
        expected("closed_issue", "2028-03-01T12:00:00Z"),
        expected("no_issue_fallback", "2028-02-28T06:00:00Z"),
        expected("unknown"),
        expected("conflicting_metadata"),
    ]
    assert run_recipe(inputs) == outputs
