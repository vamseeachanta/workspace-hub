"""TDD: verify plan_mode annotations on stage contracts and skill wiring (WRK-1083)."""
import yaml
from pathlib import Path

STAGES_DIR = Path("scripts/work-queue/stages")
PLAN_MODE_STAGES = {4, 6, 10, 13}


def test_plan_mode_required_annotated():
    """Stages 4, 6, 10, 13 must have plan_mode: required in their contract YAML."""
    for n in PLAN_MODE_STAGES:
        files = list(STAGES_DIR.glob(f"stage-{n:02d}-*.yaml"))
        assert files, f"No contract found for stage {n}"
        data = yaml.safe_load(files[0].read_text())
        assert data.get("plan_mode") == "required", (
            f"Stage {n} ({files[0].name}) missing plan_mode: required"
        )


def test_non_deliberative_stages_not_annotated():
    """Stages outside {4,6,10,13} must NOT have plan_mode: required."""
    for f in STAGES_DIR.glob("stage-*.yaml"):
        order = int(f.stem.split("-")[1])
        if order in PLAN_MODE_STAGES:
            continue
        data = yaml.safe_load(f.read_text())
        assert data.get("plan_mode") != "required", (
            f"Stage {order} ({f.name}) has unexpected plan_mode: required"
        )


def test_plan_mode_skill_exists():
    """The workspace-hub/plan-mode skill must exist and reference all trigger stages."""
    skill = Path(".claude/skills/workspace-hub/plan-mode/SKILL.md")
    assert skill.exists(), "plan-mode skill missing"
    text = skill.read_text()
    assert "EnterPlanMode" in text, "skill must mention EnterPlanMode"
    for n in PLAN_MODE_STAGES:
        assert f"Stage {n}" in text or f"stage {n}" in text.lower(), (
            f"Stage {n} not mentioned in plan-mode skill"
        )


def test_work_queue_workflow_references_plan_mode():
    """work-queue-workflow/SKILL.md must reference the plan-mode skill."""
    skill = Path(".claude/skills/workspace-hub/work-queue-workflow/SKILL.md")
    text = skill.read_text()
    assert "plan-mode" in text.lower() or "plan_mode" in text.lower(), (
        "work-queue-workflow/SKILL.md does not reference plan-mode skill"
    )


def test_stage_micro_skills_reference_plan_mode():
    """Stage 6, 10, 13 micro-skills must reference EnterPlanMode."""
    for n in [6, 10, 13]:
        files = list(Path(".claude/skills/workspace-hub/stages").glob(f"stage-{n:02d}-*.md"))
        assert files, f"No micro-skill for stage {n}"
        text = files[0].read_text()
        assert "EnterPlanMode" in text or "plan-mode" in text.lower(), (
            f"Stage {n} micro-skill missing EnterPlanMode reference"
        )
