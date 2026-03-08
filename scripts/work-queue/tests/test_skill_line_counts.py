"""T40-T44: Skill file line count and structure tests."""
from pathlib import Path
import yaml

BASE = Path("/mnt/local-analysis/workspace-hub")


def count_lines(rel_path):
    p = BASE / rel_path
    if not p.exists():
        return None
    return len(p.read_text().splitlines())


def test_T40_work_queue_skill_under_250_lines():
    """T40: work-queue/SKILL.md must be ≤250 lines."""
    n = count_lines(".claude/skills/coordination/workspace/work-queue/SKILL.md")
    assert n is not None, "work-queue/SKILL.md not found"
    assert n <= 250, f"work-queue/SKILL.md has {n} lines (limit: 250)"


def test_T41_work_queue_workflow_skill_under_250_lines():
    """T41: work-queue-workflow/SKILL.md ≤250 lines (relaxed from 200 due to new content)."""
    n = count_lines(".claude/skills/workspace-hub/work-queue-workflow/SKILL.md")
    assert n is not None, "work-queue-workflow/SKILL.md not found"
    assert n <= 250, f"work-queue-workflow/SKILL.md has {n} lines (limit: 250)"


def test_T42_workflow_gatepass_skill_under_200_lines():
    """T42: workflow-gatepass/SKILL.md ≤200 lines."""
    n = count_lines(".claude/skills/workspace-hub/workflow-gatepass/SKILL.md")
    assert n is not None, "workflow-gatepass/SKILL.md not found"
    assert n <= 200, f"workflow-gatepass/SKILL.md has {n} lines (limit: 200)"


def test_T43_workflow_html_skill_under_400_lines():
    """T43: workflow-html/SKILL.md ≤400 lines."""
    n = count_lines(".claude/skills/workspace-hub/workflow-html/SKILL.md")
    assert n is not None, "workflow-html/SKILL.md not found"
    assert n <= 400, f"workflow-html/SKILL.md has {n} lines (limit: 400)"


def test_T44_wrk_resume_has_version_field():
    """T44: wrk-resume.md has version: field in frontmatter."""
    path = BASE / ".claude/commands/workspace-hub/wrk-resume.md"
    if not path.exists():
        import pytest; pytest.skip("wrk-resume.md not found")
    content = path.read_text()
    assert "version:" in content, "wrk-resume.md missing version: field"
