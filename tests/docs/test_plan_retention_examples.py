"""Execute the plan retention examples against independent calendar expectations."""

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = REPO_ROOT / "docs/plans/_template-issue-plan.md"
POLICY = "../document-intelligence/durable-vs-transient-knowledge-boundary.md"
BASIS = f"{POLICY}#81-retention-schedule"


def _retention_section():
    text = TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"^## Retention\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, "The plan template needs a Retention section"
    return match.group(1)


def _example():
    section = _retention_section()
    json_blocks = re.findall(r"^```json\n(.*?)^```", section, re.M | re.S)
    python_blocks = re.findall(r"^```python\n(.*?)^```", section, re.M | re.S)
    assert len(json_blocks) == len(python_blocks) == 1
    return json.loads(json_blocks[0]), python_blocks[0]


def _execute(metadata, code):
    namespace = {"metadata": metadata}
    exec(compile(code, str(TEMPLATE), "exec"), namespace)
    return namespace["archive_eligible_on"]


def test_plan_template_has_retention_basis():
    section = " ".join(_retention_section().split())
    assert f"]({BASIS})" in section
    assert (TEMPLATE.parent / POLICY).is_file()
    assert "advisory pending #2237" in section.lower()
    assert "no conformance check" in section.lower()
    metadata, _ = _example()
    assert metadata["issue"] == "#NNN"
    assert metadata["artifact_class"] == "plan"
    assert metadata["retention_basis"] == BASIS
    assert metadata["retention_status"] == "advisory"
    # Boundary policy, section 8.1, plan-files row: issue lifetime + 30 days.
    assert metadata["retention_days"] == 30
    assert metadata["disposition"] == "archive"


def test_plan_retention_closed_issue_example():
    metadata, code = _example()
    assert metadata["issue_state"] == "closed"
    assert metadata["closed_on"] == "2024-01-31"
    # Independent hand calculation: January 31 + February's 29 leap-year
    # days + March 1 = 30 days. No date arithmetic from the example is reused.
    assert _execute(metadata, code) == "2024-03-01"
    metadata["closed_on"] = None
    assert _execute(metadata, code) is None


@pytest.mark.parametrize("closed_on", [None, "2024-01-31"])
def test_plan_retention_open_issue_has_no_expiry(closed_on):
    metadata, code = _example()
    metadata.update(issue_state="open", closed_on=closed_on)
    # An open or reopened issue has no fixed date, even with a stale closure.
    assert _execute(metadata, code) is None


def test_plan_retention_preserves_marker_policy():
    section = _retention_section()
    assert ".planning/plan-approved/" in section
    assert ".planning/verified/" in section
    assert "permanent for closed issues" in section.lower()
    assert "does not authorize deletion" in section.lower()
