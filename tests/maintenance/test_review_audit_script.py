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
    assert "gh_auth_error" in script


def test_review_audit_checks_auth_before_main_logic():
    """Auth check must appear before the main audit logic, not just in the issue-creation block."""
    script = REVIEW_AUDIT_SCRIPT.read_text()
    auth_pos = script.index("gh auth status")
    main_logic_pos = script.index("# ── Main Logic")
    assert auth_pos < main_logic_pos, "gh auth status must be checked before main logic"


def test_review_audit_searches_existing_issues_by_title():
    """Issue dedup should search by title, not just label."""
    script = REVIEW_AUDIT_SCRIPT.read_text()
    assert "--search" in script, "gh issue list should use --search to match by title"


def test_review_audit_handles_missing_gh_cli():
    """Script should handle missing gh CLI gracefully."""
    script = REVIEW_AUDIT_SCRIPT.read_text()
    assert "command -v gh" in script, "Should check if gh CLI is installed"
