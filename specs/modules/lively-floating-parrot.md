# WRK-5110 Implementation Plan — Work-Queue Orchestrator Folder-Skill

## Context

The work-queue orchestration logic is split across 3 skills: `coordination/workspace/work-queue/`, `workspace-hub/work-queue-workflow/`, and `workspace-hub/workflow-gatepass/`. WRK-5110 creates a unified `work-queue-orchestrator/` folder-skill with lean SKILL.md, canonical stage mapping, hooks schema, and tests.

## Directory Structure

```
.claude/skills/workspace-hub/work-queue-orchestrator/
├── SKILL.md                              # AC1, AC2: lean <50 lines
├── hooks.yaml                            # AC6: no-bypass constraints
├── scripts/
│   └── generate-stage-mapping.py         # AC3, AC7: builds canonical mapping
└── references/
    ├── stage-gate-policy.md              # AC4: extracted gate policy
    ├── stage-transitions.md              # AC4: stage transition rules
    ├── stage-mapping.yaml                # AC4, AC7: canonical output
    └── hooks-schema.yaml                 # AC5: hooks.yaml schema
```

## Implementation Steps (TDD)

### Step 1: Write tests first (Red)

Create `tests/work-queue/test_stage_mapping.py`:
- `test_generate_mapping_produces_20_stages` — output has exactly 20 entries
- `test_mapping_stage_numbers_sequential` — orders 1-20 present
- `test_mapping_names_match_contracts` — names match stage YAML `name` field
- `test_mapping_output_valid_yaml` — parseable YAML
- `test_hooks_yaml_valid` — hooks.yaml parseable and has required keys
- `test_hooks_schema_valid_yaml` — hooks-schema.yaml parseable

### Step 2: Create `scripts/generate-stage-mapping.py`

- Read all 20 `scripts/work-queue/stages/stage-NN-*.yaml` files
- Extract: order, name, slug (from filename), weight, human_gate, invocation
- Output YAML to stdout (or write to references/stage-mapping.yaml)
- Pattern: `glob("scripts/work-queue/stages/stage-*-*.yaml")`

### Step 3: Create reference files

**`references/stage-mapping.yaml`** — generated output:
```yaml
stages:
  - order: 1
    name: Capture
    slug: capture
    contract: scripts/work-queue/stages/stage-01-capture.yaml
    micro_skill: .claude/skills/workspace-hub/stages/stage-01-capture.md
    weight: light
    human_gate: false
    invocation: human_interactive
  # ... 20 entries
```

**`references/stage-gate-policy.md`** — extracted from work-queue-workflow SKILL.md:
- Hard gates (stages 1, 5, 7, 17)
- R-25, R-26, R-27 rules
- Plan-mode gates (stages 4, 6, 10, 13)

**`references/stage-transitions.md`** — chained stages, group boundaries:
- PLAN (1-4), REVIEW (5-7), EXECUTE (8-16), CLOSE (17-20)
- Chained: 2→3→4, 8→9

**`references/hooks-schema.yaml`** — schema for per-stage hooks:
```yaml
type: object
properties:
  pre_enter_hooks: {type: array, items: {type: object, ...}}
  pre_exit_hooks: {type: array, items: {type: object, ...}}
required: [pre_exit_hooks]
```

### Step 4: Create `hooks.yaml`

No-bypass constraints for the orchestrator:
- dispatch-run.sh must be called before group runners
- Human gates cannot be skipped
- Evidence artifacts must exist before stage exit

### Step 5: Create SKILL.md

Lean (<50 lines) referencing sub-materials. Pattern follows `workflow-gatepass/SKILL.md`.

### Step 6: Run tests (Green), commit, push

## Key Files to Read/Reuse

- `scripts/work-queue/stages/stage-*.yaml` — source data for mapping
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md` — folder-skill pattern
- `.claude/skills/workspace-hub/workflow-gatepass/no-bypass-rules/SKILL.md` — no-bypass pattern
- `scripts/work-queue/start_stage.py` — existing stage resolution logic to reuse
- `scripts/work-queue/dispatch-run.sh` — group routing logic

## Verification

1. `uv run pytest tests/work-queue/test_stage_mapping.py -v` — all 6+ tests pass
2. `uv run python scripts/generate-stage-mapping.py` — produces valid YAML with 20 stages
3. `wc -l .claude/skills/workspace-hub/work-queue-orchestrator/SKILL.md` — under 50
4. `python -c "import yaml; yaml.safe_load(open('...hooks.yaml'))"` — valid YAML
5. Verify no stage-specific scripts leaked into orchestrator scripts/
