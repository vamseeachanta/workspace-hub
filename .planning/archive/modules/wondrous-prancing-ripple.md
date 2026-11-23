# Implementation Plan: WRK-1083 — Plan-Mode Integration for Work-Queue-Workflow Stages

## Context

EnterPlanMode prevents file writes during deliberative WRK stages, ensuring agents think through
the full approach before committing artifacts. Currently only Stage 4 references it (in prose),
with no declarative schema annotation and no skill that agents can reference at other stages.
This WRK formalizes plan-mode as a first-class lifecycle gate by: annotating stage contract YAMLs,
creating a thin `workspace-hub/plan-mode` skill, and updating `work-queue-workflow/SKILL.md`.

## Architecture

Three-layer change:
1. **Stage contract YAMLs** (`scripts/work-queue/stages/`) — add `plan_mode: required` field
2. **New skill** (`.claude/skills/workspace-hub/plan-mode/SKILL.md`) — explicit triggers + rationale
3. **Skill wiring** — `work-queue-workflow/SKILL.md` references new skill; stage micro-skills updated

No changes to Python scripts (`start_stage.py`/`exit_stage.py`) — enforcement is skill-level prose,
not script-level automation (plan-mode signals are not yet hookable per WRK-305 / placeholder status).

## Stages to Annotate

| Stage | Name | Rationale |
|-------|------|-----------|
| 4 | Plan Draft | Formalize existing prose; deliberates plan structure before writing HTML |
| 6 | Cross-Review | Synthesizes 3-provider findings; premature writes corrupt the verdict |
| 10 | Work Execution | Before implementation commits; plans test + file strategy |
| 13 | Agent Cross-Review | Reviewing implementation quality requires structured analysis |

## Tasks

### Task 1: Add `plan_mode: required` to Stage Contract YAMLs (TDD first)

**Files:**
- Modify: `scripts/work-queue/stages/stage-04-plan-draft.yaml`
- Modify: `scripts/work-queue/stages/stage-06-cross-review.yaml`
- Modify: `scripts/work-queue/stages/stage-10-work-execution.yaml`
- Modify: `scripts/work-queue/stages/stage-13-agent-cross-review.yaml`
- Test: `tests/work-queue/test_plan_mode_annotation.py` (new)

**Step 1: Write failing test**
```python
# tests/work-queue/test_plan_mode_annotation.py
import yaml
from pathlib import Path

STAGES_DIR = Path("scripts/work-queue/stages")
PLAN_MODE_STAGES = {4, 6, 10, 13}

def test_plan_mode_required_annotated():
    for n in PLAN_MODE_STAGES:
        files = list(STAGES_DIR.glob(f"stage-{n:02d}-*.yaml"))
        assert files, f"No contract found for stage {n}"
        data = yaml.safe_load(files[0].read_text())
        assert data.get("plan_mode") == "required", \
            f"Stage {n} ({files[0].name}) missing plan_mode: required"

def test_non_deliberative_stages_not_annotated():
    """Stages 1-3,5,7-9,11-12,14-20 should NOT have plan_mode: required."""
    skip = PLAN_MODE_STAGES
    for f in STAGES_DIR.glob("stage-*.yaml"):
        order = int(f.stem.split("-")[1])
        if order in skip:
            continue
        data = yaml.safe_load(f.read_text())
        assert data.get("plan_mode") != "required", \
            f"Stage {order} ({f.name}) has unexpected plan_mode: required"
```

**Step 2: Run test — expect FAIL**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v
# Expected: FAIL — plan_mode field missing
```

**Step 3: Add `plan_mode: required` to each contract**
Insert after `context_budget_kb:` line in each of the 4 YAMLs:
```yaml
plan_mode: required
```

**Step 4: Run test — expect PASS**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v
# Expected: PASS
```

**Step 5: Commit**
```bash
git add scripts/work-queue/stages/stage-{04,06,10,13}-*.yaml \
        tests/work-queue/test_plan_mode_annotation.py
git commit -m "feat(WRK-1083): add plan_mode: required to stages 4,6,10,13"
```

---

### Task 2: Create `workspace-hub/plan-mode` Skill

**Files:**
- Create: `.claude/skills/workspace-hub/plan-mode/SKILL.md`
- Test: `tests/work-queue/test_plan_mode_annotation.py` — extend with skill reference check

**Step 1: Write failing test**
```python
# Append to tests/work-queue/test_plan_mode_annotation.py
def test_plan_mode_skill_exists():
    skill = Path(".claude/skills/workspace-hub/plan-mode/SKILL.md")
    assert skill.exists(), "plan-mode skill missing"
    text = skill.read_text()
    assert "EnterPlanMode" in text
    for n in PLAN_MODE_STAGES:
        assert f"Stage {n}" in text or f"stage {n}" in text.lower(), \
            f"Stage {n} not mentioned in plan-mode skill"
```

**Step 2: Run test — expect FAIL**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py::test_plan_mode_skill_exists -v
```

**Step 3: Create the skill**
Content: name, description, triggers (stages 4/6/10/13), invocation pattern (call EnterPlanMode
before first artifact write), rationale table, link to `writing-plans` for plan structure.
Keep under 80 lines (this is a thin orchestration skill, not a planning methodology).

**Step 4: Run test — expect PASS**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v
```

**Step 5: Commit**
```bash
git add .claude/skills/workspace-hub/plan-mode/SKILL.md \
        tests/work-queue/test_plan_mode_annotation.py
git commit -m "feat(WRK-1083): add workspace-hub/plan-mode skill"
```

---

### Task 3: Wire Skill into `work-queue-workflow/SKILL.md` and Stage Micro-Skills

**Files:**
- Modify: `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- Modify: `.claude/skills/workspace-hub/stages/stage-06-cross-review.md`
- Modify: `.claude/skills/workspace-hub/stages/stage-10-work-execution.md`
- Modify: `.claude/skills/workspace-hub/stages/stage-13-agent-cross-review.md`
- Test: `tests/work-queue/test_plan_mode_annotation.py` — extend with wiring checks

**Step 1: Write failing test**
```python
def test_work_queue_workflow_references_plan_mode():
    skill = Path(".claude/skills/workspace-hub/work-queue-workflow/SKILL.md")
    text = skill.read_text()
    assert "plan-mode" in text.lower() or "plan_mode" in text.lower(), \
        "work-queue-workflow/SKILL.md does not reference plan-mode skill"

def test_stage_micro_skills_reference_plan_mode():
    for n in [6, 10, 13]:
        files = list(Path(".claude/skills/workspace-hub/stages").glob(f"stage-{n:02d}-*.md"))
        assert files, f"No micro-skill for stage {n}"
        text = files[0].read_text()
        assert "EnterPlanMode" in text or "plan.mode" in text.lower(), \
            f"Stage {n} micro-skill missing EnterPlanMode reference"
```

**Step 2: Run tests — expect FAIL**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v
```

**Step 3: Update `work-queue-workflow/SKILL.md`**
Add a `## Plan-Mode Gates` section after the Stage Gate Policy table that lists
stages 4, 6, 10, 13 and references `workspace-hub/plan-mode` skill.

**Step 4: Update stage micro-skills (6, 10, 13)**
Prepend step 1 of each stage checklist: "EnterPlanMode before first artifact write".

**Step 5: Run tests — expect PASS**
```bash
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v
```

**Step 6: Commit**
```bash
git add .claude/skills/workspace-hub/work-queue-workflow/SKILL.md \
        .claude/skills/workspace-hub/stages/stage-{06,10,13}-*.md \
        tests/work-queue/test_plan_mode_annotation.py
git commit -m "feat(WRK-1083): wire plan-mode skill into workflow + stage micro-skills"
```

---

## Critical Files

| File | Change |
|------|--------|
| `scripts/work-queue/stages/stage-04-plan-draft.yaml` | Add `plan_mode: required` |
| `scripts/work-queue/stages/stage-06-cross-review.yaml` | Add `plan_mode: required` |
| `scripts/work-queue/stages/stage-10-work-execution.yaml` | Add `plan_mode: required` |
| `scripts/work-queue/stages/stage-13-agent-cross-review.yaml` | Add `plan_mode: required` |
| `.claude/skills/workspace-hub/plan-mode/SKILL.md` | **Create** (new skill) |
| `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | Add `## Plan-Mode Gates` section |
| `.claude/skills/workspace-hub/stages/stage-06-cross-review.md` | Add EnterPlanMode step |
| `.claude/skills/workspace-hub/stages/stage-10-work-execution.md` | Add EnterPlanMode step |
| `.claude/skills/workspace-hub/stages/stage-13-agent-cross-review.md` | Add EnterPlanMode step |
| `tests/work-queue/test_plan_mode_annotation.py` | **Create** (TDD test file) |

## Notes on `writing-plans` Skill

Reviewed: `.claude/skills/development/planning/writing-plans/SKILL.md` (v1.0.0, obra/superpowers).
It covers plan artifact structure (tasks, code snippets, 2-5 min granularity) — not WRK-stage
invocation triggers. The new `workspace-hub/plan-mode` skill will reference it for plan format
guidance. No changes to `writing-plans` itself are needed (AC satisfied: "wire it in").

## Verification

```bash
# Run all TDD tests
uv run --no-project python -m pytest tests/work-queue/test_plan_mode_annotation.py -v

# Verify gate evidence
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1083

# Manual check: 4 stage YAMLs have plan_mode: required
grep "plan_mode" scripts/work-queue/stages/stage-{04,06,10,13}-*.yaml

# Manual check: skill exists + references correct stages
grep -c "Stage" .claude/skills/workspace-hub/plan-mode/SKILL.md
```
