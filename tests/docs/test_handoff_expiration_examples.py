"""Execute the template examples against the cited advisory retention policy."""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "docs/templates/session-handoff.md"
POLICY = "../document-intelligence/durable-vs-transient-knowledge-boundary.md"


def read_template():
    return TEMPLATE.read_text(encoding="utf-8")


def run_example(template, heading, tmp_path):
    section = template.split(f"### {heading}\n", 1)[1].split("\n### ", 1)[0]
    blocks = re.findall(r"^```python\n(.*?)^```$", section, flags=re.M | re.S)
    assert len(blocks) == 1, f"Expected one standalone example for {heading}"
    result = subprocess.run(
        [sys.executable, "-I", "-c", blocks[0]],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert not result.stderr
    metadata = json.loads(result.stdout)
    assert set(metadata) == {
        "issue_reference", "issue_state", "created_at", "closed_at",
        "expected_lifetime", "expires_at", "advisory_basis",
    }
    assert metadata["advisory_basis"] == f"{POLICY}#81-retention-schedule"
    assert datetime.fromisoformat(metadata["created_at"]).utcoffset().total_seconds() == 0
    return metadata


def test_handoff_open_issue_expiration_is_pending(tmp_path):
    template = read_template()
    metadata = run_example(template, "Open issue", tmp_path)
    assert metadata["issue_reference"] == "<issue-reference>"
    assert metadata["issue_state"] == "open"
    assert metadata["created_at"] == "2026-01-15T12:00:00+00:00"
    assert metadata["closed_at"] is None
    assert metadata["expires_at"] is None
    assert metadata["expected_lifetime"] == "until issue closure plus 30 days"


def test_handoff_closed_issue_expiration(tmp_path):
    template = read_template()
    metadata = run_example(template, "Closed issue", tmp_path)
    assert metadata["issue_reference"] == "<issue-reference>"
    assert metadata["issue_state"] == "closed"
    assert metadata["created_at"] == "2026-01-15T12:00:00+00:00"
    assert metadata["closed_at"] == "2026-01-31T12:00:00+00:00"
    assert metadata["expected_lifetime"] == "until issue closure plus 30 days"
    # Policy Section 8.1: 30 days after closure. Independent calendar count:
    # January 31 through February 28 is 28 days; two more days gives March 2.
    assert metadata["expires_at"] == "2026-03-02T12:00:00+00:00"


def test_handoff_without_issue_expiration(tmp_path):
    template = read_template()
    metadata = run_example(template, "No issue", tmp_path)
    assert metadata["issue_reference"] is None
    assert metadata["issue_state"] == "none"
    assert metadata["created_at"] == "2026-01-31T12:00:00+00:00"
    assert metadata["closed_at"] is None
    assert metadata["expected_lifetime"] == "90 days from creation"
    # Policy Sections 8.1 and 8.4: 90 days from the handoff date.
    # Independent count: February 28 + March 31 + April 30 = 89; May 1 = 90.
    assert metadata["expires_at"] == "2026-05-01T12:00:00+00:00"


def test_handoff_expiration_metadata_has_policy_source():
    template = read_template()
    expiration = template.split("## Expiration\n", 1)[1]
    for field in (
        "issue_reference", "issue_state", "created_at", "closed_at",
        "expected_lifetime", "expires_at", "advisory_basis",
    ):
        assert f"`{field}`" in expiration
    for anchor in (
        "81-retention-schedule", "84-metadata-dependency-codex-finding-c4",
        "101-templates-and-conventions",
    ):
        assert f"]({POLICY}#{anchor})" in template
    policy = (TEMPLATE.parent / POLICY).read_text(encoding="utf-8")
    assert "advisory pending" in policy
    assert "closed for 30 days (fall-back: 90 days if no issue reference)" in policy
    assert "advisory" in expiration.lower()
    assert "not approval" in template.lower()
    assert "no automatic archive or delete" in template.lower()
    assert "explicitly absent" in expiration
    assert "unknown" in expiration
    assert '"issue_reference": None' in expiration
