---
title: Compound Engineering Skill
description: Implement Every.to's compound engineering methodology as a new workspace-hub skill
version: 1.0.0
module: compound-engineering
session:
  id: flickering-rolling-rossum
  agent: claude-opus-4.5
review: complete
implemented: 2026-01-31
commits:
  - 0ff6a8b  # feat(compound-engineering): add skill and command
  - 69f67c3  # chore(submodules): symlink propagation to 19 repos
sources:
  - https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents
  - https://github.com/EveryInc/compound-engineering-plugin
  - https://lethain.com/everyinc-compound-engineering/
---

# Plan: Compound Engineering Skill

## Summary

Create a new `compound-engineering` skill that implements Every.to's 4-phase loop (Plan -> Work -> Review -> Compound) as a unified orchestrator. The skill delegates to existing workspace-hub skills rather than duplicating them, adding three key innovations:

1. **Research-driven planning** - Codebase archaeology + internet best practices before plan creation
2. **12-perspective parallel review** - Spawns 12 isolated reviewer subagents vs current 5-category sequential review
3. **Per-session compounding** - Immediate knowledge capture after each task (not just daily cron)

## Files to Create

### 1. `.claude/skills/coordination/workspace/compound-engineering/SKILL.md`

Core skill definition. Key sections:

**Frontmatter**: name, description, version, capabilities, tools, related_skills

**4 Phases**:

| Phase | Effort | What It Does | Delegates To |
|-------|--------|-------------|--------------|
| Plan | 40% | Knowledge retrieval + codebase archaeology + WebSearch research + plan synthesis | knowledge-manager (advise), core-planner |
| Work | 10% | Convert plan to tasks, TDD implementation | core-coder |
| Review | 40% | 12 parallel perspective-specific reviewer subagents + aggregation | 12x Task subagents, core-reviewer for aggregation |
| Compound | 10% | Extract patterns/gotchas/tips, store as knowledge entries | knowledge-manager (capture), skill-learner |

**12 Review Perspectives**: Security, Performance, Correctness, Maintainability, Testability, Scalability, Accessibility, Error Handling, Dependencies, Consistency, Documentation, Deployment

**Self-improving loop**: Compound phase stores PAT-*/GOT-*/TIP-* entries -> Plan phase retrieves via `/knowledge advise` -> Each feature benefits from prior learnings

**Session checkpoints**: `.claude/compound-state/[session-id].yaml` for resume capability

### 2. `.claude/commands/workspace-hub/compound.md`

Command wrapper with smart routing:

```
/compound "Add OAuth to website"       # Full loop
/compound plan "Add OAuth"             # Plan only
/compound work                         # Work only
/compound review                       # Review only
/compound learn                        # Compound only
/compound resume WRK-055               # Resume from checkpoint
```

Aliases: `compound-engineering`, `ce`

## Files to Modify

### 3. `.claude/skills/coordination/workspace/work-queue/SKILL.md`

Add compound integration to Route C:
- Add `compound: true` frontmatter field to work item format
- Route C items with `compound: true` delegate to `/compound` instead of standard pipeline
- Add `/work add --compound "description"` variant

Changes are minimal - add a section under "Complexity Routing" and update the work item format template.

### 4. `.claude/skill-registry.yaml`

Register the new skill:
```yaml
- name: "coordination/compound-engineering"
  description: "Every.to's compound engineering - 4-phase loop (Plan->Work->Review->Compound) where each feature makes the next easier"
  archived: false
  path: ".claude/commands/workspace-hub/compound.md"
```

## Storage Locations

```
.claude/compound-state/          # Session checkpoints (ephemeral)
.claude/compound-reviews/        # Multi-perspective review reports
.claude/knowledge/entries/       # Reuses existing knowledge structure
specs/modules/<module>/plan.md   # Reuses existing spec location
```

No new storage paradigms - reuses existing directories.

## Integration Points

| Existing Skill | Integration |
|----------------|-------------|
| knowledge-manager | Plan phase calls `/knowledge advise`; Compound phase calls `/knowledge capture` |
| work-queue | Route C items with `compound: true` delegate to compound loop |
| core-planner | Plan phase delegates task breakdown |
| core-coder | Work phase delegates TDD implementation |
| core-reviewer | Review phase delegates aggregation logic |
| skill-learner | Compound phase triggers if pattern score > 0.7 |
| claude-reflect | Daily reflect incorporates compound session data |

## What This Does NOT Do

- Does not duplicate existing skill logic (orchestrates only)
- Does not create shell scripts (skill is prompt-driven via Task tool, not bash-driven)
- Does not change existing skill behavior (additive only)
- Does not require new dependencies

## Verification

1. Run `/compound plan "test feature"` - should produce a research-informed plan
2. Run `/compound review` after any code change - should spawn parallel reviewers and aggregate
3. Run `/compound learn` after completing work - should create knowledge entries
4. Verify `/knowledge advise "test feature"` returns entries from step 3
5. Verify work-queue recognizes `compound: true` items
