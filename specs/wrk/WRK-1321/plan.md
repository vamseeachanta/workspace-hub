# WRK-1321: Two-Tier Folder-Skill Architecture

## Mission

Restructure the work-queue's 3 overlapping skill trees (28 skills), 20 bare stage micro-skills, and 72 flat scripts into a two-tier folder-skill architecture following Anthropic best practices. OUT: changing stage logic, modifying contracts, or altering the 20-stage lifecycle itself. The migration must be atomic and idempotent, keeping the workspace functional at every commit.

## What / Why

The current work-queue behavior is split across overlapping skill trees, bare stage micro-skills, YAML contracts, and flat scripts. That creates three concrete problems:

1. Skill selection is ambiguous: agents can load multiple overlapping skills for the same stage.
2. Runtime ownership is unclear: scripts, hooks, contracts, and guidance are not co-located.
3. Refactors are high-risk: path changes can silently break dispatch, exit, pre-commit, or cron-driven workflows.

Anthropic's official skill authoring best practices (March 2026) define a skill as "a folder with SKILL.md + scripts/ + references/" using progressive disclosure. This aligns with the two-tier design. The migration optimizes for compatibility first, then cleanup: introduce new structure in parallel, verify runtime, then remove old trees.

## Acceptance Criteria

- [ ] AC1: Tier-1 orchestrator folder-skill exists at `.claude/skills/workspace-hub/work-queue-orchestrator/` with `SKILL.md`, `scripts/`, `references/`, and `hooks.yaml`
- [ ] AC2: All 20 stages are represented as folder-skills under `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] AC3: Each stage folder contains at minimum `SKILL.md`, `contract.yaml`, `gotchas.md`, and `hooks.yaml`
- [ ] AC4: Stage-specific scripts are co-located under the owning stage folder's `scripts/`, while shared orchestration scripts remain under `scripts/work-queue/`
- [ ] AC5: Existing runtime entrypoints (`dispatch-run.sh`, `exit_stage.py`, checklist/gate helpers, hooks, and any cron-invoked flows) resolve new paths correctly
- [ ] AC6: Old overlapping skills are removed only after compatibility verification passes (Copy → Redirect → Delete pattern)
- [ ] AC7: Progressive disclosure remains intact: startup metadata points to folder-skills, and stage content is loaded on demand
- [ ] AC8: Migration is idempotent: rerunning scaffold/move/validate scripts does not duplicate files or corrupt stage folders
- [ ] AC9: Error handling is explicit for missing stage folders, missing `contract.yaml`, malformed `hooks.yaml`, and stale path references
- [ ] AC10: All Python invocations added or modified by this WRK use `uv run --no-project python ...` unless documented exception
- [ ] AC11: Full lifecycle verification passes against a disposable test WRK and does not regress pre-commit or nightly automation
- [ ] AC12: TDD evidence exists for migration helpers and path-resolution changes before implementation cleanup begins

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `migrate-stage-to-folder.sh` | Scaffold one stage folder from bare .md + contract YAML; must be idempotent | stage number | `stage-NN-name/` directory | child-b |
| `migrate-scripts-to-stages.sh` | Copy stage-owned scripts to stage folders and patch internal imports; supports dry-run | mapping YAML | copied & patched files + report | child-c |
| `validate-folder-skill.sh` | Validate required folder-skill structure and content references; fail loudly | skill path | pass/fail + diagnostics | child-b |
| `update-orchestration-paths.py` | Patch path lookups in runtime scripts — AST for .py, regex for .sh; mandatory --dry-run mode, atomic backup per file, --rollback sub-command | old→new mapping | patched files + summary + diff | child-d |
| `generate-stage-mapping.py` | Build canonical stage-number → stage-folder-name mapping | stage metadata sources | mapping artifact | child-a |
| `audit-old-paths.sh` | Find stale references to removed skill/script paths before cleanup | repo root | report of unresolved references | child-d |

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Create orchestrator folder-skill and migration metadata | Build Tier 1 orchestrator plus canonical stage mapping and compatibility rules needed by later phases | — | claude | |
| child-b | Convert 20 stages to folder-skills | Scaffold and populate all stage folders from existing stage docs/contracts with validation; no runtime cutover yet | child-a | claude | |
| child-c | Copy & patch scripts to stage folders | Classify scripts (4 buckets), copy stage-owned to stage folders, patch imports, leave originals intact | child-b | claude | |
| child-d | Cutover, verify, then cleanup | Switch runtime lookups to new paths, run end-to-end verification, audit stale refs, only then delete old trees | child-c | claude | |

### Child: child-a — Create Orchestrator Folder-Skill and Migration Metadata

**Files/skills needed (entry_reads):**
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `scripts/work-queue/dispatch-run.sh`
- `scripts/work-queue/exit_stage.py`
- `scripts/work-queue/verify-gate-evidence.py`

**Acceptance Criteria:**
- [ ] Orchestrator exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] `SKILL.md` is lean (<50 lines) and references, rather than embeds, detailed material
- [ ] `scripts/` contains orchestrator-owned helpers only; no stage-specific leakage
- [ ] `references/` contains stage-gate-policy.md, transitions reference, canonical stage mapping
- [ ] `hooks.yaml` is valid and documents no-bypass constraints
- [ ] `references/hooks-schema.yaml` defines the hooks.yaml schema for child-b validation
- [ ] Canonical stage-number → stage-folder-name mapping artifact exists
- [ ] Tests exist for mapping generation/resolution

### Child: child-b — Convert 20 Stages to Folder-Skills

**Files/skills needed (entry_reads):**
- `.claude/skills/workspace-hub/stages/stage-*.md` (all 20)
- `scripts/work-queue/stages/stage-*.yaml` (all 20 contracts)
- `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md` (9 gatepass sub-skills)

**Acceptance Criteria:**
- [ ] 20 directories: `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] Each folder contains: SKILL.md, contract.yaml, gotchas.md, hooks.yaml
- [ ] contract.yaml copied from current source without semantic drift
- [ ] hooks.yaml validates against contract.yaml
- [ ] Gatepass content distributed by relevance, no duplicated conflicting rules
- [ ] `migrate-stage-to-folder.sh` created, tested, and rerunnable (idempotent)
- [ ] `validate-folder-skill.sh` passes for all 20 stages
- [ ] hooks.yaml validated against `references/hooks-schema.yaml` from child-a
- [ ] Partial scaffold (e.g. 12/20 stages) is a valid intermediate state — idempotency handles resume
- [ ] No runtime entrypoint is switched to new folders during this child

**Edge Cases:**
- Missing or malformed stage contract YAML
- Stage doc with no obvious canonical name
- Duplicate stage names after slug normalization
- Missing operational lesson input for gotchas.md
- hooks.yaml generation where a stage has no hooks

### Child: child-c — Copy & Patch Scripts to Stage Folders

**Files/skills needed (entry_reads):**
- `scripts/work-queue/*.sh` (43 scripts)
- `scripts/work-queue/*.py` (29 scripts)
- Stage folders from child-b

**Acceptance Criteria:**
- [ ] Script classification artifact exists: stage-owned, shared-runtime, shared-library, unknown/manual-review
- [ ] Path-pattern discovery step completed: grep all path idioms (`os.path`, `pathlib`, `__file__`, `BASH_SOURCE`, `source`, `${REPO_ROOT}`, hardcoded `scripts/work-queue` strings) → coverage matrix produced
- [ ] Only stage-owned scripts copied into `stage-NN-name/scripts/`
- [ ] ALL discovered path patterns patched (not just `sys.path.append` and `source ../`)
- [ ] Shared runtime/orchestration scripts remain in `scripts/work-queue/`
- [ ] `migrate-scripts-to-stages.sh` supports dry-run and is idempotent
- [ ] Unknown/ambiguous scripts not moved automatically; if >20% unknown → pause for human review
- [ ] Original scripts remain untouched (workspace stays functional)
- [ ] Path-pattern coverage matrix exported as explicit input artifact for child-d

### Child: child-d — Cutover, Verify, Then Cleanup

**Files/skills needed (entry_reads):**
- All orchestration scripts (dispatch-run.sh, run-plan.sh, exit_stage.py, etc.)
- Hook configurations, `.pre-commit-config.yaml`, `.github/workflows/`
- Old skill trees targeted for removal

**Acceptance Criteria:**
- [ ] `update-orchestration-paths.py` updates global dispatchers: AST for Python, regex for bash (no blind string replace)
- [ ] `update-orchestration-paths.py` supports --dry-run (emits diff without writing), atomic backup per file, and --rollback
- [ ] `dispatch-run.sh` works with new stage folder paths
- [ ] `exit_stage.py` finds stage contracts in new locations
- [ ] `verify-gate-evidence.py` and checklist helpers work with new locations
- [ ] Pre-commit hooks pass with no stale path references
- [ ] Nightly/cron-invoked flows audited for path assumptions
- [ ] `audit-old-paths.sh` reports zero unresolved references before deletion (scans dotfiles/hidden dirs too)
- [ ] In-flight WRK queue state inspected for stale path references before cleanup
- [ ] Old skill trees removed only after all verification passes
- [ ] Shared scripts syntax-checked after old script deletion (no broken source/import to deleted files)
- [ ] Full lifecycle test using disposable WRK succeeds end to end
- [ ] Rollback path documented; `--rollback` subcommand tested separately from git revert

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator structure validation | happy | SKILL.md, scripts/, references/, hooks.yaml present and valid |
| Stage mapping generation | happy | Canonical mapping is stable, unique, reproducible |
| Stage folder completeness | happy | All 20 stages have required files and pass validator |
| Stage scaffold idempotency | edge | Re-running scaffold produces 0 changes, exit code 0 |
| Contract/hook consistency | edge | contract.yaml and hooks.yaml agree on hook presence |
| Script classification review | happy | Every script classified; unknowns blocked from auto-move |
| Script migration dry-run | happy | Planned copies reported without filesystem mutation |
| Script migration rerun | edge | Second run is no-op |
| Python import / bash source resolution | robust | `python stage-NN/scripts/foo.py --help` succeeds |
| dispatch-run.sh with new paths | happy | Successfully dispatches disposable WRK |
| exit_stage.py contract resolution | happy | Finds contract in stage folder |
| Missing stage folder | error | Clear non-zero failure with actionable message |
| Missing contract.yaml | error | Clear failure with stage path in message |
| Malformed hooks.yaml | error | Validation fails before runtime cutover |
| Old path audit | edge | Stale references enumerated before deletion |
| Progressive disclosure (structural) | happy | Orchestrator SKILL.md does not inline stage content; stages reachable only via references |
| Pre-commit integration | happy | Existing hooks pass with new paths |
| Global path references check | edge | `grep -r "scripts/work-queue/stages"` returns empty after cleanup (incl. dotfiles) |
| In-flight WRK state check | edge | Active WRK queue files have no stale path references |
| Shared scripts post-cleanup | robust | All shared scripts in `scripts/work-queue/` pass syntax-check after old deletions |
| Full lifecycle run | happy | `/work run` on test WRK succeeds start to close |
| `--rollback` subcommand | edge | `update-orchestration-paths.py --rollback` restores files from atomic backups |
| Git revert rollback | edge | Reverting cutover commit leaves workspace functional |
| Unknown bucket sanity | edge | If >20% scripts classified as unknown, migration pauses for human review |

TDD sequencing:
- Write validator tests before scaffold script
- Write mapping/path-resolution tests before runtime patches
- Write migration dry-run/idempotency tests before file copies
- Write integration tests before deleting old skill trees

## Pseudocode

```text
# Phase 0: Preflight
1. Verify WRK-1321 exists and gate evidence requirements are known
2. Inventory current stage docs, contracts, scripts, hooks, path consumers
3. Define canonical stage mapping artifact
4. Write tests for mapping resolution, scaffold validation, runtime path lookup

# Phase 1: Orchestrator (child-a)
1. Create .claude/skills/workspace-hub/work-queue-orchestrator/
2. Write lean SKILL.md: stage FSM, dispatch entry point, sub-skill index
3. Add references/: transition policy, gate policy, stage mapping
4. Add orchestrator-owned scripts only (copied, not moved)
5. Validate hooks.yaml and orchestrator structure

# Phase 2: Stage Conversion (child-b)
1. For each stage, derive canonical folder name from mapping artifact
2. Scaffold stage-NN-name/ with SKILL.md, contract.yaml, gotchas.md, hooks.yaml
3. Copy/adapt stage content without changing contract semantics
4. Validate each stage folder
5. Do NOT switch runtime path consumers yet

# Phase 3: Script Copy & Patch (child-c)
1. Classify each script: stage-owned, shared-runtime, shared-library, unknown
2. Generate mapping YAML; flag unknowns for manual review
3. Copy only stage-owned scripts into stage folders
4. Patch sys.path / source paths for new depth
5. Run dry-run and idempotency checks
6. Leave originals untouched

# Phase 4: Cutover (child-d, part 1)
1. Patch runtime path resolution using canonical mapping (AST/regex)
2. Update docs/tests/configs referencing old paths
3. Run unit/integration tests for dispatch, exit, hooks, gate evidence
4. Audit .pre-commit-config.yaml, .github/workflows/, nightly/cron consumers

# Phase 5: Cleanup (child-d, part 2)
1. Run audit-old-paths.sh until zero unresolved references
2. Remove deprecated overlapping skill trees
3. Remove original scripts that were copied to stage folders
4. Run full disposable WRK lifecycle test
5. Record rollback instructions and final verification evidence
```

## Synthesis Notes

This plan merges the best of 3 agent reviews:
- **Codex:** 12 ACs, 4-bucket script classification, audit-old-paths.sh, TDD sequencing, rollback planning
- **Gemini:** Copy-first-then-delete (workspace never broken), import/source path patching, CI/CD file awareness
- **Claude:** Original decomposition, Anthropic best practices research, progressive disclosure design
