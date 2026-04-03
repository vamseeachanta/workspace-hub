"""Static safety checks for review-audit issue handling.

ABOUTME: Verifies review-audit.sh checks gh auth, avoids duplicate backlog issue
creation, and records auth status in JSON output metadata.
"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_AUDIT_SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "review-audit.sh"


def test_review_audit_checks_gh_auth_before_issue_mutation():
    script = REVIEW_AUDIT_SCRIPT.read_text()
    assert "gh auth status" in script


def test_review_audit_checks_for_existing_review_backlog_issue():
    script = REVIEW_AUDIT_SCRIPT.read_text()
    assert "gh issue list" in script
    assert "review-backlog" in script


def test_review_audit_records_auth_status_in_json_summary():
    script = REVIEW_AUDIT_SCRIPT.read_text()
    assert "gh_authenticated" in script
