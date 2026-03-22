YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-1321: Two-Tier Folder-Skill Architecture

## Mission

Restructure the work-queue's 3 overlapping skill trees (28 skills), 20 bare stage micro-skills, and 72 flat scripts into a robust, two-tier folder-skill architecture following Anthropic best practices. OUT: changing stage logic, modifying contracts, or altering the 20-stage lifecycle itself. The migration must be atomic and idempotent to ensure the workspace remains in a functional state at every step.

## What / Why

The work-queue workflow is spread across 3 overlapping skill trees, 20 bare micro-skills, 20 YAML contracts, and 72 flat scripts. Agents don't know which skill to load when. Rules are scattered. Scripts have no clear mapping to stages, increasing the risk of path-resolution failures and brittle automation.

Anthropic's official skill authoring best practices (March 2026) define a skill as "a folder with SKILL.md + scripts/ + references/" using progressive disclosure. This aligns with the two-tier design proposed here, encapsulating domain knowledge and execution logic together.

## Acceptance Criteria

- [ ] AC1: Orchestrator folder-skill created with lean SKILL.md (<50 lines), scripts/, references/
- [ ] AC2: All 20 stages converted from bare .md to folder-skills (`stage-NN-name/SKILL.md`)
- [ ] AC3: Stage-specific scripts co-located in each stage folder's `scripts/`
- [ ] AC4: On-demand `hooks.yaml` per stage folder
- [ ] AC5: `gotchas.md` in each stage folder (from 11+ documented operational lessons)
- [ ] AC6: Old overlapping skills and flat scripts removed ONLY AFTER new paths are verified (Copy -> Redirect -> Delete pattern)
- [ ] AC7: All orchestration scripts (`dispatch-run.sh`, `exit_stage.py`, etc.) updated and functioning with new paths
- [ ] AC8: Python imports and Bash `source` directives within moved scripts successfully resolved relative to their new locations
- [ ] AC9: Progressive disclosure working — metadata loaded at startup, SKILL.md on-demand
- [ ] AC10: Migration scripts are idempotent (safe to run multiple times without corrupting state)

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `migrate-stage-to-folder.sh` | Scaffold a stage folder-skill from bare .md + contract YAML. Must be idempotent. | stage number | `stage-NN-name/` directory | child-b |
| `migrate-scripts-to-stages.sh` | Safely copy scripts to stage folders and update their internal relative imports. | script mapping YAML | copied & patched files | child-c |
| `validate-folder-skill.sh` | Verify a folder-skill has the required structure and parsable YAML/Markdown. | skill path | pass/fail | child-b |
| `update-orchestration-paths.py` | Update import/execution paths in global orchestration scripts, agent configs, and hooks using AST/Regex. | old→new mapping | patched files | child-d |

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Scaffold Orchestrator folder-skill | Build Tier 1 `work-queue-orchestrator/` with lean SKILL.md, stage FSM references, and copy prep/close scripts. | — | claude | |
| child-b | Scaffold 20 Stage folder-skills | Idempotently transform bare `stage-NN.md` files into `stage-NN-name/` folders with SKILL.md, `contract.yaml`, `gotchas.md`, `hooks.yaml`. | child-a | claude | |
| child-c | Distribute Scripts (Copy & Patch) | Copy stage-specific scripts to stage folders and patch their internal relative imports/source paths, leaving originals intact. | child-b | claude | |
| child-d | Cutover and Cleanup | Patch orchestration tools to point to new paths, run full lifecycle tests, and only then delete old flat scripts and deprecated skills. | child-c | claude | |

### Child: child-a — Scaffold Orchestrator Folder-Skill

**Files/skills needed (entry_reads):**
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `scripts/work-queue/dispatch-run.sh`
- `scripts/work-queue/exit_stage.py`

**Acceptance Criteria:**
- [ ] Orchestrator SKILL.md exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] SKILL.md body under 50 lines with stage FSM overview and dynamic stage discovery logic
- [ ] `scripts/` dir contains `prep_stage.py`, `close_stage.py` (copied, not moved yet)
- [ ] `references/` dir contains `stage-gate-policy.md`, transitions reference
- [ ] `hooks.yaml` with "no bypassing stage machinery" rule

### Child: child-b — Scaffold 20 Stage Folder-Skills

**Files/skills needed (entry_reads):**
- `.claude/skills/workspace-hub/stages/stage-*.md` (all 20)
- `scripts/work-queue/stages/stage-*.yaml` (all 20 contracts)
- `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md` (9 gatepass sub-skills)

**Acceptance Criteria:**
- [ ] 20 directories: `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] Each folder contains: SKILL.md, `contract.yaml`, `gotchas.md`, `hooks.yaml`
- [ ] Gatepass sub-skill content distributed to relevant stage folders
- [ ] `migrate-stage-to-folder.sh` script created, executed, and verified idempotent
- [ ] `validate-folder-skill.sh` passes for all 20 stages

### Child: child-c — Distribute Scripts (Copy & Patch)

**Files/skills needed (entry_reads):**
- `scripts/work-queue/*.sh` (43 scripts)
- `scripts/work-queue/*.py` (29 scripts)
- Stage folders from child-b

**Acceptance Criteria:**
- [ ] Script-to-stage mapping YAML created
- [ ] Stage-specific scripts COPIED (not moved) to `stage-NN-name/scripts/`
- [ ] Internal relative imports (`import sys; sys.path.append(...)`) and bash sources (`source ../../...`) patched in the new copies to account for increased directory depth
- [ ] Shared/orchestration scripts identified to remain in `scripts/work-queue/`
- [ ] Original scripts remain untouched to ensure CI/existing agents don't break during migration

### Child: child-d — Cutover and Cleanup

**Files/skills needed (entry_reads):**
- All orchestration scripts (`dispatch-run.sh`, `run-plan.sh`, `exit_stage.py`, etc.)
- Old skill trees and flat scripts
- `.github/workflows/`, `.pre-commit-config.yaml`, and agent configs

**Acceptance Criteria:**
- [ ] `update-orchestration-paths.py` successfully updates global dispatchers to use the new nested paths
- [ ] `dispatch-run.sh` works with new stage folder paths
- [ ] `exit_stage.py` discovers stage contracts in new locations
- [ ] Full lifecycle test (`/work run` on a test WRK) succeeds
- [ ] Pre-commit hooks updated and passing
- [ ] Old flat scripts in `scripts/work-queue/` (that were moved) safely deleted
- [ ] Old skill trees removed: `coordination/work-queue`, `workflow-gatepass`, bare `stage-*.md` files

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator SKILL.md structure | happy | SKILL.md <50 lines, `scripts/` and `references/` present |
| Stage folder completeness | happy | All 20 stages have SKILL.md, `contract.yaml`, `gotchas.md`, `hooks.yaml` |
| Idempotency of migration scripts | robust | Running migration scripts twice results in 0 changes and exit code 0 |
| Python Import / Bash Source Resolution | robust | Running `python stage-NN-name/scripts/foo.py --help` succeeds without `ModuleNotFoundError` |
| `dispatch-run.sh` with new paths | happy | Successfully dispatches a WRK through stages using the new architecture |
| Missing stage folder | error | Clear error message from orchestrator, not a silent failure |
| Progressive disclosure | happy | Only triggered stage SKILL.md loaded into context |
| Global Path References Check | edge | `grep -r "scripts/work-queue/stages"` returns empty after cleanup |

---

## Gemini Notes

### 1. Failure Modes & Robustness
- **Mid-Air Collisions:** The original draft moved scripts in `child-c` and updated paths in `child-d`. If the agent pauses or fails between C and D, the workspace is fundamentally broken for all other agents. I modified the approach to "Copy & Patch" in `child-c` and "Cutover & Delete" in `child-d`. This guarantees the workspace remains usable at every git commit.
- **Idempotency:** Migration scripts must be able to be re-run safely if an agent crashes mid-execution. Added this explicitly to ACs and the Test Plan.
- **Import/Source Path Breakage:** Moving a script from `scripts/work-queue/` to `.claude/skills/workspace-hub/stages/stage-01-triage/scripts/` changes its relative depth. Python scripts relying on relative `sys.path.append` or bash scripts using `source ../shared.sh` will break instantly. Added a specific patching step in `child-c` and an import resolution test in the Test Plan.

### 2. Backward Compatibility
- **Agent Memory/Prompts:** Existing agents might have hardcoded paths to `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` in their memory or system prompts. During the cutover (`child-d`), it may be wise to leave behind a temporary symlink or a markdown file with a forwarding notice (`This skill has moved to...`) instead of an outright deletion, depending on how strict the agent ecosystem is.
- **CI/CD and Git Hooks:** `.pre-commit-config.yaml` or `.github/workflows/` often reference these flat scripts. I added a requirement in `child-d` to explicitly update these integration points.

### 3. Decomposition Enhancements
- The children were logically sound, but I tightened the boundaries. `child-c` is strictly about preparing the new executable state. `child-d` is the "flip the switch" phase. This separation of concerns makes it much easier to validate the new structure before destroying the old one.

### 4. Automation Risks
- The `update-script-paths.py` in the original draft is risky if it relies on simple string replacement. I renamed it to `update-orchestration-paths.py` and recommended AST parsing (for Python) or Regex with boundary checks to prevent accidental partial replacements in unrelated files. A global `grep` check was added to the test plan to verify no dangling old references remain.
