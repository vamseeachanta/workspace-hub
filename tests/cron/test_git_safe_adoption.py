"""Static checks for git-safe adoption in scheduled cron workflows (#1715)."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
SKILL_AUTORESEARCH = REPO_ROOT / "scripts" / "cron" / "skill-autoresearch-nightly.sh"


def test_schedule_no_longer_inlines_git_for_targeted_tasks():
    text = SCHEDULE.read_text()
    for forbidden in [
        "git pull origin main --rebase &&",
        "(git commit -m 'chore: weekly architecture scan report' && git push origin main)",
        "(git commit -m 'chore: weekly staleness scan freshness dashboard' && git push origin main)",
        "(git commit -m 'chore(solver): daily dashboard regeneration' && git push origin main)",
    ]:
        assert forbidden not in text


def test_skill_autoresearch_uses_git_safe_commit():
    text = SKILL_AUTORESEARCH.read_text()
    assert "git_safe_commit" in text
    assert "git commit -m" not in text
