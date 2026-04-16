from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "weekly-governance-check.sh"


def test_weekly_governance_check_counts_lowercase_fail_status():
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "c.get('status') == 'fail'" in content
    assert "c.get('status') == 'FAIL'" not in content


def test_weekly_governance_check_uses_existing_repo_labels():
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    assert '--label "bug,priority:medium,domain:knowledge-management"' in content
    assert '--label "bug,priority:medium,cat:document-intelligence"' in content
    assert 'gh issue list --label "conformance"' not in content
    assert 'gh issue list --label "registry-health"' not in content
