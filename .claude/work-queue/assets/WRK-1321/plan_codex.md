OpenAI Codex v0.115.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019d130a-add7-7193-a00b-55e1668c5ca9
--------
user
# Stance: Codex Plan Draft Review

You are a software engineer agent. Your focus is on **implementation correctness, edge cases, and testability**.

You will receive a Claude-authored plan draft. Walk it section-by-section and produce your own refined version.

When reviewing:
1. Challenge any assumptions about implementation approach — is there a simpler or more robust way?
2. Identify edge cases not covered (malformed input, missing fields, timezone/date math, quota exhaustion).
3. Flag AC gaps — things implementable but not covered by the listed tests.
4. Assess integration risks (nightly cron, file writes, CLI availability).
5. Verify uv run --no-project python is used wherever Python is called.

Your output must be a complete refined plan (same structure as the input draft).
Add a "Codex Notes" section at the end with your specific findings.

---
CLAUDE DRAFT PLAN:
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
warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/batch/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/explorer/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

warning: Ignoring malformed agent role definition: failed to deserialize agent role file at /mnt/local-analysis/workspace-hub/.codex/agents/worker/config.toml: invalid type: string "Read(*)", expected struct FilesystemPermissionsToml

mcp startup: no servers
codex
# WRK-1321: Two-Tier Folder-Skill Architecture

## Mission

Restructure the work-queue skill/runtime layout into a two-tier folder-skill architecture without changing stage semantics, contracts, or the 20-stage lifecycle. The migration must preserve CLI behavior, nightly automation, hook execution, and existing WRK gate workflows while making skill discovery deterministic and testable.

## What / Why

The current work-queue behavior is split across overlapping skill trees, bare stage micro-skills, YAML contracts, and flat scripts. That creates three concrete problems:

1. Skill selection is ambiguous: agents can load multiple overlapping skills for the same stage.
2. Runtime ownership is unclear: scripts, hooks, contracts, and guidance are not co-located.
3. Refactors are high-risk: path changes can silently break dispatch, exit, pre-commit, or cron-driven workflows.

A two-tier architecture is the right target, but the migration should optimize for compatibility first, then cleanup. The safest path is:

1. Introduce the new folder-skill structure in parallel.
2. Add path resolution/compatibility shims only where needed.
3. Verify runtime behavior end-to-end.
4. Remove old trees only after all call sites are proven migrated.

Anthropic’s folder-skill guidance supports this structure, but the migration should avoid symlink-heavy solutions unless the repo already relies on them. Plain files or thin wrappers are more portable and easier to test.

## Acceptance Criteria

- [ ] AC1: Tier-1 orchestrator folder-skill exists at `.claude/skills/workspace-hub/work-queue-orchestrator/` with `SKILL.md`, `scripts/`, `references/`, and `hooks.yaml`
- [ ] AC2: All 20 stages are represented as folder-skills under `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] AC3: Each stage folder contains at minimum `SKILL.md`, `contract.yaml`, `gotchas.md`, and `hooks.yaml`
- [ ] AC4: Stage-specific scripts are co-located under the owning stage folder’s `scripts/`, while shared orchestration scripts remain under `scripts/work-queue/`
- [ ] AC5: Existing runtime entrypoints (`dispatch-run.sh`, `exit_stage.py`, checklist/gate helpers, hooks, and any cron-invoked flows) resolve new paths correctly
- [ ] AC6: Old overlapping skills are removed only after compatibility verification passes
- [ ] AC7: Progressive disclosure remains intact: startup metadata points to folder-skills, and stage content is loaded on demand rather than preloaded wholesale
- [ ] AC8: Migration is idempotent: rerunning scaffold/move/validate scripts does not duplicate files or corrupt stage folders
- [ ] AC9: Error handling is explicit for missing stage folders, missing `contract.yaml`, malformed `hooks.yaml`, and stale path references
- [ ] AC10: All Python invocations added or modified by this WRK use `uv run --no-project python ...` unless the script must run inside a project environment and that exception is documented
- [ ] AC11: Full lifecycle verification passes against a disposable test WRK and does not regress pre-commit or nightly automation behavior
- [ ] AC12: TDD evidence exists for migration helpers and path-resolution changes before implementation cleanup begins

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `migrate-stage-to-folder.sh` | Scaffold one stage folder from bare stage doc + contract + metadata template; must be idempotent | stage number/name, source paths | `stage-NN-name/` directory | child-b |
| `migrate-scripts-to-stages.sh` | Move/copy stage-owned scripts based on an explicit mapping file; must support dry-run | mapping YAML, repo root | relocated scripts + report | child-c |
| `validate-folder-skill.sh` | Validate required folder-skill structure and content references; fail loudly | skill path | pass/fail + diagnostics | child-b |
| `update-script-paths.py` | Patch path lookups in runtime scripts/configs using a reviewed mapping table | old→new mapping | patched files + summary | child-d |
| `generate-stage-mapping.py` | Build or verify stage-name/path mapping used by migration/runtime tests | stage metadata sources | canonical mapping artifact | child-a |
| `audit-old-paths.sh` | Find stale references to removed skill/script paths before cleanup | repo root | report of unresolved references | child-d |

Notes:
- Prefer `sh` for shell utilities and `uv run --no-project python` for Python helpers.
- Any Python shebang/wrapper introduced by this WRK must still execute through `uv run --no-project python` in docs/tests/examples.

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Create orchestrator folder-skill and migration metadata | Build Tier 1 orchestrator plus the canonical stage mapping and compatibility rules needed by later phases | — | claude | WRK-1321 |
| child-b | Convert 20 stages to folder-skills | Scaffold and populate all stage folders from existing stage docs/contracts with validation and no runtime cutover yet | child-a | claude | WRK-1321 |
| child-c | Redistribute scripts to stage folders | Classify flat scripts into stage-owned vs shared, migrate stage-owned scripts, and preserve executable behavior | child-b | claude | WRK-1321 |
| child-d | Update paths, verify integrations, then remove old skills | Switch runtime lookups to new paths, run end-to-end verification, and only then delete deprecated skill trees | child-c | claude | WRK-1321 |

### Child: child-a — Create Orchestrator Folder-Skill and Migration Metadata

**Files/skills needed (entry_reads):**
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `scripts/work-queue/dispatch-run.sh`
- `scripts/work-queue/exit_stage.py`
- `scripts/work-queue/verify-gate-evidence.py`
- Any stage name registry/source currently used by dispatch logic

**Acceptance Criteria:**
- [ ] Orchestrator exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] `SKILL.md` is lean and references, rather than embeds, detailed stage/gate material
- [ ] `scripts/` contains orchestrator-owned helpers only; no stage-specific leakage
- [ ] `references/` contains stage transition policy, gate policy, and canonical stage mapping reference
- [ ] `hooks.yaml` is valid and documents no-bypass constraints plus failure behavior
- [ ] A canonical stage-number → stage-folder-name mapping artifact exists and is used by later migration/runtime code
- [ ] Tests exist first for mapping generation/resolution and orchestrator path lookup behavior

**Implementation Notes:**
- Avoid symlinks unless there is an existing cross-platform symlink pattern in the repo.
- If `prep_stage.py` / `close_stage.py` are wrappers, document ownership clearly so future edits do not fork logic unintentionally.
- Define one source of truth for stage naming before any folder creation begins.

### Child: child-b — Convert 20 Stages to Folder-Skills

**Files/skills needed (entry_reads):**
- `.claude/skills/workspace-hub/stages/stage-*.md` or current bare-stage source set
- `scripts/work-queue/stages/stage-*.yaml`
- `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md`
- Any operational lessons source used to populate `gotchas.md`

**Acceptance Criteria:**
- [ ] 20 stage folders exist under `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] Each stage folder contains `SKILL.md`, `contract.yaml`, `gotchas.md`, and `hooks.yaml`
- [ ] `contract.yaml` is copied/rendered from the current contract source without semantic drift
- [ ] `hooks.yaml` is syntactically valid and consistent with `contract.yaml`
- [ ] Gatepass content is distributed by relevance, with no duplicated conflicting rules across stages
- [ ] `migrate-stage-to-folder.sh` is created, tested, and rerunnable
- [ ] `validate-folder-skill.sh` passes for all 20 stages
- [ ] No runtime entrypoint is yet switched to depend solely on the new folders during this child

**Edge Cases to Cover:**
- Missing or malformed stage contract YAML
- Stage doc with no obvious canonical stage name
- Duplicate stage names after slug normalization
- Missing operational lesson input for `gotchas.md`
- `hooks.yaml` generation where a stage has no hooks
- Bare stage docs containing path references that become stale after folderization

### Child: child-c — Redistribute Scripts to Stage Folders

**Files/skills needed (entry_reads):**
- `scripts/work-queue/*.sh`
- `scripts/work-queue/*.py`
- Stage folders from child-b
- Any existing docs/tests that reference script paths

**Acceptance Criteria:**
- [ ] Script classification artifact exists: `stage-owned`, `shared-runtime`, `shared-library`, `unknown/manual-review`
- [ ] Only stage-owned scripts move into `stage-NN-name/scripts/`
- [ ] Shared runtime/orchestration scripts remain in `scripts/work-queue/`
- [ ] Executable bits, shebang expectations, and relative path assumptions are preserved or corrected
- [ ] `migrate-scripts-to-stages.sh` supports dry-run and emits a machine-readable report
- [ ] No imports, shell source statements, or docs references remain broken after migration
- [ ] Unknown/ambiguous scripts are not moved automatically; they require explicit review

**Implementation Notes:**
- Do not assume one script belongs to exactly one stage.
- Multi-stage scripts and libraries should stay centralized even if mostly used by one stage.
- Shell scripts using relative paths are a major regression risk; normalize to repo-root-based resolution where possible.

### Child: child-d — Update Paths, Verify Integrations, Then Remove Old Skills

**Files/skills needed (entry_reads):**
- All orchestration scripts: `dispatch-run.sh`, `run-plan.sh`, `exit_stage.py`, checklist/gate helpers, hook runners
- Hook configurations and pre-commit configs
- Old skill trees targeted for removal
- Any nightly/cron wrappers that touch work-queue files

**Acceptance Criteria:**
- [ ] Runtime path resolution supports new stage folder paths deterministically
- [ ] `dispatch-run.sh` works with new stage folder paths
- [ ] `exit_stage.py` finds stage contracts in new locations
- [ ] `verify-gate-evidence.py` and checklist helpers work with new locations
- [ ] Pre-commit hooks still pass with no stale path references
- [ ] Nightly/cron-invoked flows are audited for path assumptions and either verified or explicitly exempted
- [ ] `audit-old-paths.sh` reports zero unresolved references before old trees are deleted
- [ ] Old overlapping skill trees are removed only after all runtime and test verification passes
- [ ] Full lifecycle test using a disposable WRK succeeds end to end
- [ ] Rollback path is documented: restore old references or revert mapping changes if runtime cutover fails

**Implementation Notes:**
- Cleanup must be the last step, not part of first cutover.
- “Fail gracefully or redirect” for old paths should be decided explicitly. Silent redirect risks masking stale consumers; explicit error with remediation is safer unless compatibility is required by automation.

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator structure validation | happy | `SKILL.md`, `scripts/`, `references/`, `hooks.yaml` present and valid |
| Stage mapping generation | happy | Canonical mapping is stable, unique, and reproducible |
| Stage folder completeness | happy | All 20 stages have required files and pass validator |
| Stage scaffold idempotency | edge | Re-running scaffold does not duplicate files or alter unchanged content |
| Contract/hook consistency | edge | `contract.yaml` and `hooks.yaml` agree on hook presence/names |
| Script classification review | happy | Every migrated script is classified; unknowns are blocked from auto-move |
| Script migration dry-run | happy | Planned moves are reported without filesystem mutation |
| Script migration rerun | edge | Second run is no-op or explicitly safe |
| `dispatch-run.sh` with new paths | happy | Successfully dispatches a disposable WRK through expected stages |
| `exit_stage.py` contract resolution | happy | Finds contract in stage folder and handles missing contract clearly |
| Missing stage folder | error | Clear non-zero failure with actionable message |
| Missing `contract.yaml` | error | Clear non-zero failure with stage path in message |
| Malformed `hooks.yaml` | error | Validation fails before runtime cutover |
| Old path audit | edge | Stale references are enumerated before deletion step |
| Progressive disclosure | happy | Only targeted stage folder skill content is loaded on demand |
| Pre-commit integration | happy | Existing hooks pass with new paths |
| Nightly/cron compatibility audit | edge | Known automation paths are validated or explicitly documented as unaffected |
| Disposable full lifecycle run | happy | `/work run` equivalent succeeds on test WRK from start to close gates |
| Rollback smoke test | edge | Prior state can be restored by reverting mapping/path changes without manual repair |

TDD sequencing:
- Write validator tests before scaffold script.
- Write mapping/path-resolution tests before runtime patches.
- Write migration dry-run/idempotency tests before file moves.
- Write integration tests before deleting old skill trees.

## Pseudocode

```text
# Phase 0: Preflight
1. Verify WRK-1321 exists and gate evidence requirements are known
2. Inventory current stage docs, contracts, scripts, hooks, and path consumers
3. Define canonical stage mapping artifact
4. Add tests for mapping resolution, scaffold validation, and runtime path lookup

# Phase 1: Orchestrator
1. Create .claude/skills/workspace-hub/work-queue-orchestrator/
2. Write lean SKILL.md that points to references instead of embedding long content
3. Add references/: transition policy, gate policy, stage mapping
4. Add orchestrator-owned scripts only
5. Validate hooks.yaml and orchestrator structure

# Phase 2: Stage Conversion
1. For each stage, derive canonical folder name from mapping artifact
2. Scaffold stage-NN-name/ with SKILL.md, contract.yaml, gotchas.md, hooks.yaml
3. Copy/adapt stage content without changing contract semantics
4. Validate each stage folder
5. Do not switch runtime path consumers yet

# Phase 3: Script Redistribution
1. Classify each flat script as stage-owned, shared-runtime, shared-library, or unknown
2. Generate mapping YAML and review unknowns manually
3. Move only stage-owned scripts into stage folders
4. Preserve shared scripts in scripts/work-queue/
5. Run dry-run and idempotency checks, then execute real move

# Phase 4: Runtime Cutover
1. Patch runtime path resolution using canonical mapping
2. Update docs/tests/configs that reference old paths
3. Run unit/integration tests for dispatch, exit, hooks, and gate evidence
4. Audit nightly/cron/pre-commit consumers

# Phase 5: Cleanup
1. Run stale-path audit until zero unresolved references remain
2. Remove deprecated overlapping skill trees
3. Run full disposable WRK lifecycle test
4. Record rollback instructions and final verification evidence
```

## Codex Notes

- The draft removes old skills too early. Cleanup has to happen after runtime cutover and verification, not as part of the same phase.
- Symlinks are a portability risk and were proposed without justification. Prefer real files or thin wrappers unless the repo already standardizes symlink usage.
- The draft assumes every script maps cleanly to one stage. That is unlikely; shared libraries and multi-stage scripts need a separate classification path.
- The draft did not include idempotency requirements. Migration scripts must be safe to rerun.
- `hooks.yaml` generation needs validation against `contract.yaml`; otherwise malformed hook configs can break dispatch/exit later.
- “Progressive disclosure working” is not testable as written. It needs a concrete startup/on-demand loading assertion.
- Integration risks were underspecified: pre-commit, nightly cron, and stale docs/config references are likely failure points.
- The draft omitted rollback planning. Path migrations without rollback instructions are brittle.
- The draft mentioned Python scripts but did not enforce `uv run --no-project python`. Any added or modified invocation should explicitly use that form unless a documented exception exists.
- AC coverage was incomplete around malformed inputs, duplicate stage slug generation, missing operational lessons, broken relative shell paths, and unknown script ownership.
tokens used
121,411
# WRK-1321: Two-Tier Folder-Skill Architecture

## Mission

Restructure the work-queue skill/runtime layout into a two-tier folder-skill architecture without changing stage semantics, contracts, or the 20-stage lifecycle. The migration must preserve CLI behavior, nightly automation, hook execution, and existing WRK gate workflows while making skill discovery deterministic and testable.

## What / Why

The current work-queue behavior is split across overlapping skill trees, bare stage micro-skills, YAML contracts, and flat scripts. That creates three concrete problems:

1. Skill selection is ambiguous: agents can load multiple overlapping skills for the same stage.
2. Runtime ownership is unclear: scripts, hooks, contracts, and guidance are not co-located.
3. Refactors are high-risk: path changes can silently break dispatch, exit, pre-commit, or cron-driven workflows.

A two-tier architecture is the right target, but the migration should optimize for compatibility first, then cleanup. The safest path is:

1. Introduce the new folder-skill structure in parallel.
2. Add path resolution/compatibility shims only where needed.
3. Verify runtime behavior end-to-end.
4. Remove old trees only after all call sites are proven migrated.

Anthropic’s folder-skill guidance supports this structure, but the migration should avoid symlink-heavy solutions unless the repo already relies on them. Plain files or thin wrappers are more portable and easier to test.

## Acceptance Criteria

- [ ] AC1: Tier-1 orchestrator folder-skill exists at `.claude/skills/workspace-hub/work-queue-orchestrator/` with `SKILL.md`, `scripts/`, `references/`, and `hooks.yaml`
- [ ] AC2: All 20 stages are represented as folder-skills under `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] AC3: Each stage folder contains at minimum `SKILL.md`, `contract.yaml`, `gotchas.md`, and `hooks.yaml`
- [ ] AC4: Stage-specific scripts are co-located under the owning stage folder’s `scripts/`, while shared orchestration scripts remain under `scripts/work-queue/`
- [ ] AC5: Existing runtime entrypoints (`dispatch-run.sh`, `exit_stage.py`, checklist/gate helpers, hooks, and any cron-invoked flows) resolve new paths correctly
- [ ] AC6: Old overlapping skills are removed only after compatibility verification passes
- [ ] AC7: Progressive disclosure remains intact: startup metadata points to folder-skills, and stage content is loaded on demand rather than preloaded wholesale
- [ ] AC8: Migration is idempotent: rerunning scaffold/move/validate scripts does not duplicate files or corrupt stage folders
- [ ] AC9: Error handling is explicit for missing stage folders, missing `contract.yaml`, malformed `hooks.yaml`, and stale path references
- [ ] AC10: All Python invocations added or modified by this WRK use `uv run --no-project python ...` unless the script must run inside a project environment and that exception is documented
- [ ] AC11: Full lifecycle verification passes against a disposable test WRK and does not regress pre-commit or nightly automation behavior
- [ ] AC12: TDD evidence exists for migration helpers and path-resolution changes before implementation cleanup begins

## Scripts to Create

| Script | Purpose | Inputs | Outputs | Phase |
|--------|---------|--------|---------|-------|
| `migrate-stage-to-folder.sh` | Scaffold one stage folder from bare stage doc + contract + metadata template; must be idempotent | stage number/name, source paths | `stage-NN-name/` directory | child-b |
| `migrate-scripts-to-stages.sh` | Move/copy stage-owned scripts based on an explicit mapping file; must support dry-run | mapping YAML, repo root | relocated scripts + report | child-c |
| `validate-folder-skill.sh` | Validate required folder-skill structure and content references; fail loudly | skill path | pass/fail + diagnostics | child-b |
| `update-script-paths.py` | Patch path lookups in runtime scripts/configs using a reviewed mapping table | old→new mapping | patched files + summary | child-d |
| `generate-stage-mapping.py` | Build or verify stage-name/path mapping used by migration/runtime tests | stage metadata sources | canonical mapping artifact | child-a |
| `audit-old-paths.sh` | Find stale references to removed skill/script paths before cleanup | repo root | report of unresolved references | child-d |

Notes:
- Prefer `sh` for shell utilities and `uv run --no-project python` for Python helpers.
- Any Python shebang/wrapper introduced by this WRK must still execute through `uv run --no-project python` in docs/tests/examples.

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | Create orchestrator folder-skill and migration metadata | Build Tier 1 orchestrator plus the canonical stage mapping and compatibility rules needed by later phases | — | claude | WRK-1321 |
| child-b | Convert 20 stages to folder-skills | Scaffold and populate all stage folders from existing stage docs/contracts with validation and no runtime cutover yet | child-a | claude | WRK-1321 |
| child-c | Redistribute scripts to stage folders | Classify flat scripts into stage-owned vs shared, migrate stage-owned scripts, and preserve executable behavior | child-b | claude | WRK-1321 |
| child-d | Update paths, verify integrations, then remove old skills | Switch runtime lookups to new paths, run end-to-end verification, and only then delete deprecated skill trees | child-c | claude | WRK-1321 |

### Child: child-a — Create Orchestrator Folder-Skill and Migration Metadata

**Files/skills needed (entry_reads):**
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `scripts/work-queue/dispatch-run.sh`
- `scripts/work-queue/exit_stage.py`
- `scripts/work-queue/verify-gate-evidence.py`
- Any stage name registry/source currently used by dispatch logic

**Acceptance Criteria:**
- [ ] Orchestrator exists at `.claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md`
- [ ] `SKILL.md` is lean and references, rather than embeds, detailed stage/gate material
- [ ] `scripts/` contains orchestrator-owned helpers only; no stage-specific leakage
- [ ] `references/` contains stage transition policy, gate policy, and canonical stage mapping reference
- [ ] `hooks.yaml` is valid and documents no-bypass constraints plus failure behavior
- [ ] A canonical stage-number → stage-folder-name mapping artifact exists and is used by later migration/runtime code
- [ ] Tests exist first for mapping generation/resolution and orchestrator path lookup behavior

**Implementation Notes:**
- Avoid symlinks unless there is an existing cross-platform symlink pattern in the repo.
- If `prep_stage.py` / `close_stage.py` are wrappers, document ownership clearly so future edits do not fork logic unintentionally.
- Define one source of truth for stage naming before any folder creation begins.

### Child: child-b — Convert 20 Stages to Folder-Skills

**Files/skills needed (entry_reads):**
- `.claude/skills/workspace-hub/stages/stage-*.md` or current bare-stage source set
- `scripts/work-queue/stages/stage-*.yaml`
- `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md`
- Any operational lessons source used to populate `gotchas.md`

**Acceptance Criteria:**
- [ ] 20 stage folders exist under `.claude/skills/workspace-hub/stages/stage-NN-name/`
- [ ] Each stage folder contains `SKILL.md`, `contract.yaml`, `gotchas.md`, and `hooks.yaml`
- [ ] `contract.yaml` is copied/rendered from the current contract source without semantic drift
- [ ] `hooks.yaml` is syntactically valid and consistent with `contract.yaml`
- [ ] Gatepass content is distributed by relevance, with no duplicated conflicting rules across stages
- [ ] `migrate-stage-to-folder.sh` is created, tested, and rerunnable
- [ ] `validate-folder-skill.sh` passes for all 20 stages
- [ ] No runtime entrypoint is yet switched to depend solely on the new folders during this child

**Edge Cases to Cover:**
- Missing or malformed stage contract YAML
- Stage doc with no obvious canonical stage name
- Duplicate stage names after slug normalization
- Missing operational lesson input for `gotchas.md`
- `hooks.yaml` generation where a stage has no hooks
- Bare stage docs containing path references that become stale after folderization

### Child: child-c — Redistribute Scripts to Stage Folders

**Files/skills needed (entry_reads):**
- `scripts/work-queue/*.sh`
- `scripts/work-queue/*.py`
- Stage folders from child-b
- Any existing docs/tests that reference script paths

**Acceptance Criteria:**
- [ ] Script classification artifact exists: `stage-owned`, `shared-runtime`, `shared-library`, `unknown/manual-review`
- [ ] Only stage-owned scripts move into `stage-NN-name/scripts/`
- [ ] Shared runtime/orchestration scripts remain in `scripts/work-queue/`
- [ ] Executable bits, shebang expectations, and relative path assumptions are preserved or corrected
- [ ] `migrate-scripts-to-stages.sh` supports dry-run and emits a machine-readable report
- [ ] No imports, shell source statements, or docs references remain broken after migration
- [ ] Unknown/ambiguous scripts are not moved automatically; they require explicit review

**Implementation Notes:**
- Do not assume one script belongs to exactly one stage.
- Multi-stage scripts and libraries should stay centralized even if mostly used by one stage.
- Shell scripts using relative paths are a major regression risk; normalize to repo-root-based resolution where possible.

### Child: child-d — Update Paths, Verify Integrations, Then Remove Old Skills

**Files/skills needed (entry_reads):**
- All orchestration scripts: `dispatch-run.sh`, `run-plan.sh`, `exit_stage.py`, checklist/gate helpers, hook runners
- Hook configurations and pre-commit configs
- Old skill trees targeted for removal
- Any nightly/cron wrappers that touch work-queue files

**Acceptance Criteria:**
- [ ] Runtime path resolution supports new stage folder paths deterministically
- [ ] `dispatch-run.sh` works with new stage folder paths
- [ ] `exit_stage.py` finds stage contracts in new locations
- [ ] `verify-gate-evidence.py` and checklist helpers work with new locations
- [ ] Pre-commit hooks still pass with no stale path references
- [ ] Nightly/cron-invoked flows are audited for path assumptions and either verified or explicitly exempted
- [ ] `audit-old-paths.sh` reports zero unresolved references before old trees are deleted
- [ ] Old overlapping skill trees are removed only after all runtime and test verification passes
- [ ] Full lifecycle test using a disposable WRK succeeds end to end
- [ ] Rollback path is documented: restore old references or revert mapping changes if runtime cutover fails

**Implementation Notes:**
- Cleanup must be the last step, not part of first cutover.
- “Fail gracefully or redirect” for old paths should be decided explicitly. Silent redirect risks masking stale consumers; explicit error with remediation is safer unless compatibility is required by automation.

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Orchestrator structure validation | happy | `SKILL.md`, `scripts/`, `references/`, `hooks.yaml` present and valid |
| Stage mapping generation | happy | Canonical mapping is stable, unique, and reproducible |
| Stage folder completeness | happy | All 20 stages have required files and pass validator |
| Stage scaffold idempotency | edge | Re-running scaffold does not duplicate files or alter unchanged content |
| Contract/hook consistency | edge | `contract.yaml` and `hooks.yaml` agree on hook presence/names |
| Script classification review | happy | Every migrated script is classified; unknowns are blocked from auto-move |
| Script migration dry-run | happy | Planned moves are reported without filesystem mutation |
| Script migration rerun | edge | Second run is no-op or explicitly safe |
| `dispatch-run.sh` with new paths | happy | Successfully dispatches a disposable WRK through expected stages |
| `exit_stage.py` contract resolution | happy | Finds contract in stage folder and handles missing contract clearly |
| Missing stage folder | error | Clear non-zero failure with actionable message |
| Missing `contract.yaml` | error | Clear non-zero failure with stage path in message |
| Malformed `hooks.yaml` | error | Validation fails before runtime cutover |
| Old path audit | edge | Stale references are enumerated before deletion step |
| Progressive disclosure | happy | Only targeted stage folder skill content is loaded on demand |
| Pre-commit integration | happy | Existing hooks pass with new paths |
| Nightly/cron compatibility audit | edge | Known automation paths are validated or explicitly documented as unaffected |
| Disposable full lifecycle run | happy | `/work run` equivalent succeeds on test WRK from start to close gates |
| Rollback smoke test | edge | Prior state can be restored by reverting mapping/path changes without manual repair |

TDD sequencing:
- Write validator tests before scaffold script.
- Write mapping/path-resolution tests before runtime patches.
- Write migration dry-run/idempotency tests before file moves.
- Write integration tests before deleting old skill trees.

## Pseudocode

```text
# Phase 0: Preflight
1. Verify WRK-1321 exists and gate evidence requirements are known
2. Inventory current stage docs, contracts, scripts, hooks, and path consumers
3. Define canonical stage mapping artifact
4. Add tests for mapping resolution, scaffold validation, and runtime path lookup

# Phase 1: Orchestrator
1. Create .claude/skills/workspace-hub/work-queue-orchestrator/
2. Write lean SKILL.md that points to references instead of embedding long content
3. Add references/: transition policy, gate policy, stage mapping
4. Add orchestrator-owned scripts only
5. Validate hooks.yaml and orchestrator structure

# Phase 2: Stage Conversion
1. For each stage, derive canonical folder name from mapping artifact
2. Scaffold stage-NN-name/ with SKILL.md, contract.yaml, gotchas.md, hooks.yaml
3. Copy/adapt stage content without changing contract semantics
4. Validate each stage folder
5. Do not switch runtime path consumers yet

# Phase 3: Script Redistribution
1. Classify each flat script as stage-owned, shared-runtime, shared-library, or unknown
2. Generate mapping YAML and review unknowns manually
3. Move only stage-owned scripts into stage folders
4. Preserve shared scripts in scripts/work-queue/
5. Run dry-run and idempotency checks, then execute real move

# Phase 4: Runtime Cutover
1. Patch runtime path resolution using canonical mapping
2. Update docs/tests/configs that reference old paths
3. Run unit/integration tests for dispatch, exit, hooks, and gate evidence
4. Audit nightly/cron/pre-commit consumers

# Phase 5: Cleanup
1. Run stale-path audit until zero unresolved references remain
2. Remove deprecated overlapping skill trees
3. Run full disposable WRK lifecycle test
4. Record rollback instructions and final verification evidence
```

## Codex Notes

- The draft removes old skills too early. Cleanup has to happen after runtime cutover and verification, not as part of the same phase.
- Symlinks are a portability risk and were proposed without justification. Prefer real files or thin wrappers unless the repo already standardizes symlink usage.
- The draft assumes every script maps cleanly to one stage. That is unlikely; shared libraries and multi-stage scripts need a separate classification path.
- The draft did not include idempotency requirements. Migration scripts must be safe to rerun.
- `hooks.yaml` generation needs validation against `contract.yaml`; otherwise malformed hook configs can break dispatch/exit later.
- “Progressive disclosure working” is not testable as written. It needs a concrete startup/on-demand loading assertion.
- Integration risks were underspecified: pre-commit, nightly cron, and stale docs/config references are likely failure points.
- The draft omitted rollback planning. Path migrations without rollback instructions are brittle.
- The draft mentioned Python scripts but did not enforce `uv run --no-project python`. Any added or modified invocation should explicitly use that form unless a documented exception exists.
- AC coverage was incomplete around malformed inputs, duplicate stage slug generation, missing operational lessons, broken relative shell paths, and unknown script ownership.
