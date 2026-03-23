# WRK-5111: Convert 20 Stages to Folder-Skills

## Context

The 20 stage micro-skills are bare .md files with contracts living separately. WRK-5110 established the orchestrator folder-skill pattern. This WRK converts each stage into a self-contained folder-skill following the same pattern. Parent: WRK-1321 (child-b).

**Note:** max_files_changed (5) is exceeded, but this is already a child of Feature WRK-1321 — properly decomposed.

## Plan

### Phase 1: Create migration script (`migrate-stage-to-folder.sh`)

Script inputs: stage number (01-20)
Script actions:
1. Read `stage-mapping.yaml` to get slug for the stage number
2. Create folder: `.claude/skills/workspace-hub/stages/stage-{NN}-{slug}/`
3. Generate `SKILL.md` from bare `stage-{NN}-{slug}.md` content + frontmatter template
4. Copy `scripts/work-queue/stages/stage-{NN}-{slug}.yaml` → `contract.yaml` in folder
5. Generate `gotchas.md` (empty template — populated manually per stage)
6. Extract `pre_enter_hooks` + `pre_exit_hooks` from contract → `hooks.yaml`
7. Remove bare `stage-{NN}-{slug}.md`

### Phase 2: Create validation script (`validate-folder-skill.sh`)

Script inputs: stage folder path
Checks:
- SKILL.md exists and has valid frontmatter
- contract.yaml exists and is valid YAML
- gotchas.md exists
- hooks.yaml exists and has pre_exit_hooks array

### Phase 3: Run migration for all 20 stages

```bash
for i in $(seq -w 1 20); do
  bash scripts/work-queue/migrate-stage-to-folder.sh "$i"
done
```

### Phase 4: Distribute gatepass content to gotchas.md

| Source sub-skill | Target stage gotchas.md |
|-----------------|------------------------|
| no-bypass-rules | stage-01, stage-05, stage-07, stage-17 |
| close-gate-minimum | stage-19 |
| stage-15-to-stage-17-rule | stage-15 |
| operational-lessons-wrk-690 | stage-06 |

### Phase 5: Validate all 20

```bash
for dir in .claude/skills/workspace-hub/stages/stage-*/; do
  bash scripts/work-queue/validate-folder-skill.sh "$dir"
done
```

## Scripts to Create

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `scripts/work-queue/migrate-stage-to-folder.sh` | Scaffold one stage folder-skill | stage number | stage folder with SKILL.md, contract.yaml, gotchas.md, hooks.yaml |
| `scripts/work-queue/validate-folder-skill.sh` | Verify folder-skill structure | folder path | exit 0/1 |

## Key Files

- Source stages: `.claude/skills/workspace-hub/stages/stage-NN-*.md` (20 files)
- Source contracts: `scripts/work-queue/stages/stage-NN-*.yaml` (20 files)
- Stage mapping: `.claude/skills/workspace-hub/work-queue-orchestrator/references/stage-mapping.yaml`
- Hooks schema: `.claude/skills/workspace-hub/work-queue-orchestrator/references/hooks-schema.yaml`
- Gatepass sub-skills: `.claude/skills/workspace-hub/workflow-gatepass/*/SKILL.md` (9 files)

## SKILL.md Template

```markdown
---
name: stage-{NN}-{slug}
description: "Stage {NN}: {Name} — {one-line from contract}"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: {NN}
invocation: {invocation}
weight: {weight}
human_gate: {true/false}
---

{content from bare stage-NN-slug.md}
```

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| migrate-stage-to-folder.sh on stage 01 | happy | Creates folder with 4 required files |
| validate-folder-skill.sh on migrated stage | happy | Exits 0 |
| validate-folder-skill.sh on empty folder | error | Exits 1 with missing file message |
| All 20 stages migrated | happy | 20 folders, each with SKILL.md + contract.yaml + gotchas.md + hooks.yaml |
| Bare .md files removed | happy | No stage-NN-*.md files remain in stages/ root |
| Gatepass content in gotchas | happy | stage-19/gotchas.md contains close-gate content |

## Pseudocode

```
# migrate-stage-to-folder.sh
1. Parse stage number from arg
2. Read stage-mapping.yaml → get slug, name
3. Set SRC_MD=stages/stage-${NN}-${slug}.md
4. Set SRC_YAML=scripts/work-queue/stages/stage-${NN}-${slug}.yaml
5. Set DEST=stages/stage-${NN}-${slug}/
6. mkdir -p $DEST
7. Generate SKILL.md: frontmatter (name, desc, version, category, type, stage_order, invocation, weight, human_gate) + body from SRC_MD
8. cp $SRC_YAML $DEST/contract.yaml
9. Extract hooks from contract YAML → write hooks.yaml
10. Write gotchas.md template
11. rm $SRC_MD

# validate-folder-skill.sh
1. Check SKILL.md exists
2. Check contract.yaml exists and parses as YAML
3. Check gotchas.md exists
4. Check hooks.yaml exists
5. Exit 0 if all pass, exit 1 with errors otherwise
```

## Verification

1. Run `validate-folder-skill.sh` on all 20 stage folders
2. Confirm no bare `stage-NN-*.md` files remain in stages/ root
3. Confirm `contract.yaml` in each folder matches original content
4. Confirm gatepass content distributed to correct gotchas.md files
5. Run `dispatch-run.sh` on a test WRK to confirm stage loading still works (deferred to WRK-5113)
