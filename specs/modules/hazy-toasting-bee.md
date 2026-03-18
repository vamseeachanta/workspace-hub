# WRK-1316: Stage Transition Hardening — Implementation Plan

## Context

After 40-60 engineering hours across 20+ WRKs building the 20-stage lifecycle, stage transitions remain the weakest link. Rules exist in prose but aren't enforced by scripts. `pre_checks` is defined in stage YAML but never invoked. Human gates get blown through. HTML opens redundantly. No checklist enforcement. WRK-1316 fixes this by adding declarative hooks, mandatory checklists, tool activation, and gate timing — all as scripts (L2+), not prose (L0).

## What Changes

### New Files (3)

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/work-queue/run_hooks.py` | ~100 | Generic hook runner — executes hook list from YAML, respects gate/timeout, writes evidence |
| `scripts/work-queue/verify_checklist.py` | ~120 | Checklist engine — reads checklist from stage YAML, checks completion state, returns structured blockers |
| `tests/work-queue/test_transition_hardening.py` | ~180 | TDD tests for hooks + checklists (12+ test cases) |

### Modified Files (5)

| File | Change | Lines Added |
|------|--------|-------------|
| `scripts/work-queue/start_stage.py` | Wire pre_enter hooks + tool activation + refine HTML auto-open | ~20 (imports + calls) |
| `scripts/work-queue/exit_stage.py` | Wire pre_exit hooks + checklist enforcement + gate timing | ~30 |
| `scripts/work-queue/stages/stage-*.yaml` (all 20) | Add `checklist`, `pre_exit_hooks`, `pre_enter_hooks`, `tools_activated` fields | ~15 per file |
| `.claude/skills/workspace-hub/stages/stage-02-resource-intelligence.md` | Add online research + docu-intel instructions | ~5 |
| `scripts/work-queue/generate_transition_table.py` | Read new fields into transitions.yaml | ~10 |

### Enhanced Stage YAML Schema (4 new fields)

```yaml
# Existing fields unchanged (order, name, weight, etc.)

# NEW — R1: Hooks
pre_exit_hooks:                          # scripts that must pass before stage exit
  - script: scripts/work-queue/check-acs-pass.sh WRK-NNN
    description: "All ACs marked [x]"
    gate: hard                           # hard = block | soft = warn
    timeout_s: 30

pre_enter_hooks:                         # scripts that must pass before stage entry
  - script: scripts/work-queue/verify-log-presence.sh WRK-NNN
    description: "Previous stage log exists"
    gate: soft
    timeout_s: 10

# NEW — R2: Checklists
checklist:
  - id: CL-10-1
    text: "Tests written before implementation (TDD)"
    requires_human: false                # true = needs approved_by field
  - id: CL-10-2
    text: "No regressions in existing suite"
    requires_human: false

# NEW — R4: Tool/skill activation
tools_activated:
  - type: skill
    ref: superpowers/test-driven-development
  - type: skill
    ref: superpowers/systematic-debugging
```

Backward compat: existing `pre_checks` field merged into `pre_exit_hooks` automatically.

### Hook Evidence Format

Written to `assets/WRK-NNN/evidence/hooks-{phase}-{stage}.yaml`:

```yaml
phase: pre_exit
stage: 10
hooks:
  - script: check-acs-pass.sh WRK-1316
    gate: hard
    returncode: 0
    duration_s: 1.2
    passed: true
summary:
  total: 1
  passed: 1
  failed_hard: 0
  blocked: false
```

### Checklist State Format

Written to `assets/WRK-NNN/evidence/checklist-{NN}.yaml`:

```yaml
stage: 10
items:
  - id: CL-10-1
    completed: true
    completed_at: "2026-03-17T14:30:00Z"
    completed_by: agent
```

### HTML Auto-Open Refinement (R3)

- Stage 5: `xdg-open` lifecycle + plan HTML (the ONE open)
- Stages 7, 17: regenerate HTML only — 30s `<meta refresh>` handles updates
- All stages: regenerate at both entry and exit (already happens)

### Gate Timing (R5)

- `start_stage.py` writes `gate_wait_start` to stage-evidence.yaml for human-gate stages
- `exit_stage.py` writes `gate_approved_at` after human approval
- Duration computed and logged in hook evidence

## Build Sequence (7 phases)

### Phase 1: Foundation (no behavior change)
1. Write `test_transition_hardening.py` — RED tests for run_hooks and verify_checklist
2. Create `run_hooks.py` — generic hook runner
3. Create `verify_checklist.py` — checklist engine
4. Tests GREEN

### Phase 2: Wire hooks into exit path
5. Add `pre_exit_hooks` to stage-07 and stage-17 YAML (migrating existing `pre_checks`)
6. Modify `exit_stage.py` to call `run_hooks` for pre_exit hooks
7. Backward compat test: stage-07/17 behave identically

### Phase 3: Wire hooks into entry path
8. Modify `start_stage.py` to call `run_hooks` for pre_enter hooks
9. Add `pre_enter_hooks` to stage-10 YAML as proving ground

### Phase 4: Checklists
10. Add `checklist:` to stage-10, stage-12, stage-17 YAML
11. Modify `exit_stage.py` to call `verify_checklist.py` before exit
12. Test end-to-end

### Phase 5: Tool activation + HTML
13. Add `tools_activated` to stage-02, stage-05, stage-10 YAML
14. Add `_surface_tools_activated()` to start_stage.py
15. Refine HTML: `xdg-open` only at stage 5
16. Update `generate_transition_table.py`

### Phase 6: Populate all 20 stages
17. Add all new fields to all 20 stage YAMLs
18. Update stage-02 micro-skill for R0 online research
19. Full regression test

### Phase 7: Gate timing (R5)
20. Add `gate_wait_start` / `gate_approved_at` timestamps
21. Wire into hook evidence

## Key Design Decisions

1. **Minimal disruption**: enhance existing files, don't rewrite — start_stage.py gets ~20 lines, exit_stage.py ~30 lines
2. **Optional fields**: all new YAML fields are optional — stages without them behave as today
3. **TransitionBlocker pattern** (Symfony): structured blocker list with reasons, not binary pass/fail
4. **Scripts over LLM**: every enforcement is a script (L2) — no prose-only rules
5. **Backward compat**: `pre_checks` field merges into `pre_exit_hooks`; existing D-item checks unchanged
6. **Generalizable** (AC7): `run_hooks.py` and `verify_checklist.py` have no stage-specific knowledge — WRK-1317 can reuse them for any workflow

## Verification

1. `uv run --no-project python -m pytest tests/work-queue/test_transition_hardening.py -v` — 12+ tests
2. Existing tests: `uv run --no-project python -m pytest tests/work-queue/ -v` — no regressions
3. Manual: process a real WRK through stages 7→10→12→17 and verify hooks fire, checklists block, HTML refreshes
4. `uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1316` — all gates PASS

## Critical Files

- `scripts/work-queue/start_stage.py` — entry orchestrator (617 lines)
- `scripts/work-queue/exit_stage.py` — exit validator (397 lines)
- `scripts/work-queue/stage_dispatch.py` — D-item dispatcher (pattern to follow)
- `scripts/work-queue/stage_exit_checks.py` — existing gate check functions
- `scripts/work-queue/stages/stage-*.yaml` — 20 stage contracts
- `tests/work-queue/test_stage_lifecycle.py` — existing test patterns
