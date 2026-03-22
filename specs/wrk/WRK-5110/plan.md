# WRK-5110: Create Orchestrator Folder-Skill

Parent: WRK-1321 (child-a)

## Mission

Build Tier 1 `work-queue-orchestrator/` folder-skill with lean SKILL.md, canonical stage mapping, hooks schema, and orchestrator-owned scripts.

## Acceptance Criteria

- [ ] AC1: Orchestrator exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] AC2: `SKILL.md` is lean (<50 lines), references detailed material
- [ ] AC3: `scripts/` contains orchestrator-owned helpers only
- [ ] AC4: `references/` contains stage-gate-policy.md, transitions reference, canonical stage mapping
- [ ] AC5: `references/hooks-schema.yaml` defines hooks.yaml schema
- [ ] AC6: `hooks.yaml` is valid with no-bypass constraints
- [ ] AC7: Canonical stage-number → stage-folder-name mapping artifact exists
- [ ] AC8: Tests exist for mapping generation/resolution

## Implementation Steps

1. Read existing skills: coordination/work-queue SKILL.md, work-queue-workflow SKILL.md, workflow-gatepass SKILL.md
2. Create `.claude/skills/workspace-hub/work-queue-orchestrator/` directory structure
3. Write lean SKILL.md (<50 lines): stage FSM overview, dispatch entry, sub-skill index
4. Create `scripts/generate-stage-mapping.py` — builds canonical mapping from stage contracts
5. Create `references/stage-gate-policy.md` — extracted from gatepass skills
6. Create `references/hooks-schema.yaml` — schema for per-stage hooks.yaml
7. Create `references/stage-mapping.yaml` — canonical output of generate-stage-mapping.py
8. Create `hooks.yaml` — no-bypass rules
9. Write tests for mapping generation

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator SKILL.md exists and <50 lines | happy | File exists, wc -l < 50 |
| scripts/ dir has no stage-specific scripts | happy | Only orchestrator-owned |
| references/ has required files | happy | 3 files present |
| generate-stage-mapping.py produces valid YAML | happy | 20 stages mapped |
| hooks-schema.yaml is valid YAML | happy | Parseable |
| hooks.yaml validates against schema | happy | Pass |
