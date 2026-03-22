# WRK-1321: Two-Tier Folder-Skill Architecture

## Mission

Restructure the work-queue's 3 overlapping skill trees (28 skills), 20 bare stage micro-skills, and 72 flat scripts into a two-tier folder-skill architecture following Anthropic best practices. OUT: changing stage logic, modifying contracts, or altering the 20-stage lifecycle itself.

## What / Why

The work-queue workflow is spread across 3 overlapping skill trees, 20 bare micro-skills, 20 YAML contracts, and 72 flat scripts. Agents don't know which skill to load when. Rules are scattered. Scripts have no clear mapping to stages.

Anthropic's official skill authoring best practices (March 2026) define a skill as "a folder with SKILL.md + scripts/ + references/" using progressive disclosure. This aligns with the two-tier design proposed here.

## Acceptance Criteria

- [ ] AC1: Orchestrator folder-skill created with lean SKILL.md (<50 lines), scripts/, references/
- [ ] AC2: All 20 stages converted from bare .md to folder-skills (stage-NN-name/SKILL.md)
- [ ] AC3: Stage-specific scripts co-located in each stage folder's scripts/
- [ ] AC4: On-demand hooks.yaml per stage folder
- [ ] AC5: Gotchas.md in each stage folder (from 11+ documented operational lessons)
- [ ] AC6: Old overlapping skills removed (coordination/work-queue sub-skills, workflow-gatepass sub-skills)
- [ ] AC7: All existing scripts (dispatch-run.sh, exit_stage.py, etc.) work with new paths
- [ ] AC8: Progressive disclosure working — metadata loaded at startup, SKILL.md on-demand

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| migrate-stage-to-folder.sh | Scaffold a stage folder-skill from bare .md + contract YAML | stage number | stage-NN-name/ directory | child-b |
| migrate-scripts-to-stages.sh | Move scripts from flat scripts/ to stage folders | script mapping YAML | moved files | child-c |
| validate-folder-skill.sh | Verify a folder-skill has required structure | skill path | pass/fail | child-b |
| update-script-paths.py | Update import paths in orchestration scripts | old→new mapping | patched files | child-d |

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Create orchestrator folder-skill | Build Tier 1 work-queue-orchestrator/ with lean SKILL.md, stage FSM references, prep/close scripts | — | claude | |
| child-b | Convert 20 stages to folder-skills | Transform bare stage-NN.md files into stage-NN-name/ folders with SKILL.md, contract.yaml, gotchas.md, hooks.yaml | child-a | claude | |
| child-c | Redistribute scripts to stage folders | Move stage-specific scripts from flat scripts/work-queue/ into stage folder scripts/ directories | child-b | claude | |
| child-d | Update paths and remove old skills | Patch orchestration scripts for new paths, remove old overlapping skill trees, verify all integrations work | child-c | claude | |

### Child: child-a — Create Orchestrator Folder-Skill

**Files/skills needed (entry_reads):**
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `scripts/work-queue/dispatch-run.sh`
- `scripts/work-queue/exit_stage.py`

**Acceptance Criteria:**
- [ ] Orchestrator SKILL.md exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] SKILL.md body under 50 lines with stage FSM overview
- [ ] `scripts/` dir contains prep_stage.py, close_stage.py (or symlinks)
- [ ] `references/` dir contains stage-gate-policy.md, transitions reference
- [ ] `hooks.yaml` with "no bypassing stage machinery" rule

### Child: child-b — Convert 20 Stages to Folder-Skills

**Files/skills needed (entry_reads):**
- `.claude/skills/workspace-hub/stages/stage-*.md` (all 20)
- `scripts/work-queue/stages/stage-*.yaml` (all 20 contracts)
- `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md` (9 gatepass sub-skills)

**Acceptance Criteria:**
- [ ] 20 directories: `.claude/skills/workspace-hub/stages/stage-NN-name/SKILL.md`
- [ ] Each folder contains: SKILL.md, contract.yaml (from scripts/stages/), gotchas.md, hooks.yaml
- [ ] Gatepass sub-skill content distributed to relevant stage folders
- [ ] migrate-stage-to-folder.sh script created and used
- [ ] validate-folder-skill.sh passes for all 20 stages

### Child: child-c — Redistribute Scripts to Stage Folders

**Files/skills needed (entry_reads):**
- `scripts/work-queue/*.sh` (43 scripts)
- `scripts/work-queue/*.py` (29 scripts)
- Stage folders from child-b

**Acceptance Criteria:**
- [ ] Script-to-stage mapping YAML created
- [ ] Stage-specific scripts moved to `stage-NN-name/scripts/`
- [ ] Shared/orchestration scripts remain in `scripts/work-queue/`
- [ ] No broken imports or references

### Child: child-d — Update Paths and Remove Old Skills

**Files/skills needed (entry_reads):**
- All orchestration scripts (dispatch-run.sh, run-plan.sh, exit_stage.py, etc.)
- Old skill trees to remove
- Hook configurations

**Acceptance Criteria:**
- [ ] dispatch-run.sh works with new stage folder paths
- [ ] exit_stage.py finds stage contracts in new locations
- [ ] verify_checklist.py works with new paths
- [ ] Old skill trees removed: coordination/work-queue sub-skills, workflow-gatepass sub-skills
- [ ] All pre-commit hooks still work
- [ ] Full lifecycle test: `/work run` on a test WRK succeeds

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator SKILL.md structure | happy | SKILL.md <50 lines, scripts/ and references/ present |
| Stage folder completeness | happy | All 20 stages have SKILL.md, contract.yaml, gotchas.md, hooks.yaml |
| dispatch-run.sh with new paths | happy | Successfully dispatches a WRK through stages |
| Missing stage folder | error | Clear error message, not silent failure |
| Progressive disclosure | happy | Only triggered stage SKILL.md loaded into context |
| Old skill paths | edge | References to old paths fail gracefully or redirect |

## Pseudocode

```
# Phase 1: Orchestrator
1. Create .claude/skills/workspace-hub/work-queue-orchestrator/
2. Write lean SKILL.md: stage FSM diagram, dispatch entry point, sub-skill index
3. Move/symlink prep_stage.py, close_stage.py into orchestrator/scripts/
4. Extract gate policy from gatepass into orchestrator/references/

# Phase 2: Stage Conversion (for each stage 1-20)
1. Create .claude/skills/workspace-hub/stages/stage-{NN}-{name}/
2. Merge bare stage-NN.md content + contract YAML into SKILL.md
3. Write gotchas.md from operational lessons
4. Write hooks.yaml from contract pre_exit_hooks
5. Validate with validate-folder-skill.sh

# Phase 3: Script Redistribution
1. Build mapping: script → stage(s) it belongs to
2. For single-stage scripts: move to stage folder scripts/
3. For multi-stage/orchestration scripts: keep in scripts/work-queue/
4. Update any relative imports

# Phase 4: Path Updates + Cleanup
1. Patch orchestration scripts to find contracts in stage folders
2. Remove old coordination/work-queue sub-skills
3. Remove old workflow-gatepass sub-skills
4. Run full lifecycle test
```
