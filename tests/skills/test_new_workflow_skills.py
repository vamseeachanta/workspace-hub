"""Checks for newly added workflow skills (#1727, #1723)."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text()


def test_reporting_workflow_skill_exists_and_mentions_validation():
    text = _read('.claude/skills/development/workflows/reporting-workflow/SKILL.md')
    assert 'html-report-verify' in text
    assert 'Run Report-Focused Tests' in text
    assert 'Generate the Report' in text


def test_cron_job_management_skill_exists_and_mentions_git_safe_and_setup_cron():
    text = _read('.claude/skills/operations/automation/cron-job-management/SKILL.md')
    assert 'git-safe.sh' in text
    assert 'setup-cron.sh --dry-run' in text
    assert 'config/scheduled-tasks/schedule-tasks.yaml' in text
