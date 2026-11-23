"""TDD: verify plan_mode annotations on stage contracts and skill wiring (WRK-1083)."""
import yaml
from pathlib import Path

STAGES_DIR = Path(".claude/skills/workspace-hub/stages")
PLAN_MODE_STAGES = {4, 6, 10, 13}


def test_plan_mode_required_annotated():
    """Stages 4, 6, 10, 13 must have plan_mode: required in their contract YAML."""
    for n in PLAN_MODE_STAGES:
        files = list(STAGES_DIR.glob(f"stage-{n:02d}-*/contract.yaml"))
        assert files, f"No contract found for stage {n}"
        data = yaml.safe_load(files[0].read_text())
        assert data.get("plan_mode") == "required", (
            f"Stage {n} ({files[0].name}) missing plan_mode: required"
        )


def test_non_deliberative_stages_not_annotated():
    """Stages outside {4,6,10,13} must NOT have plan_mode: required."""
    for f in STAGES_DIR.glob("stage-*/contract.yaml"):
        parent = f.parent.name
        order = int(parent.split("-")[1])
        if order in PLAN_MODE_STAGES:
            continue
        data = yaml.safe_load(f.read_text())
        assert data.get("plan_mode") != "required", (
            f"Stage {order} ({parent}) has unexpected plan_mode: required"
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


def test_orchestrator_references_plan_mode():
    """work-queue-orchestrator/SKILL.md must reference the plan-mode skill."""
    skill = Path(".claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md")
    text = skill.read_text()
    assert "plan-mode" in text.lower() or "plan_mode" in text.lower(), (
        "work-queue-orchestrator/SKILL.md does not reference plan-mode skill"
    )


def test_stage_folder_skills_reference_plan_mode():
    """Stage 6, 10, 13 folder-skills must reference EnterPlanMode."""
    for n in [6, 10, 13]:
        files = list(STAGES_DIR.glob(f"stage-{n:02d}-*/SKILL.md"))
        assert files, f"No folder-skill for stage {n}"
        text = files[0].read_text()
        assert "EnterPlanMode" in text or "plan-mode" in text.lower(), (
            f"Stage {n} folder-skill missing EnterPlanMode reference"
        )
