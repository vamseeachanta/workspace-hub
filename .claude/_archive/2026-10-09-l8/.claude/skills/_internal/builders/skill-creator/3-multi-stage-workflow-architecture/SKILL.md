---
name: skill-creator-3-multi-stage-workflow-architecture
description: 'Sub-skill of skill-creator: 3. Multi-Stage Workflow Architecture (+1).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# 3. Multi-Stage Workflow Architecture (+1)

## 3. Multi-Stage Workflow Architecture


**Problem:** A monolithic SKILL.md for a workflow with N stages is only loaded when explicitly invoked — NOT at the moment each stage executes. Rules written there won't fire at execution time.

**Pattern: per-stage micro-skills auto-loaded at entry**

```
skills/my-workflow/
  SKILL.md                    ← index + cross-cutting rules only (≤150 lines)
  stages/
    stage-01-intake.md        ← complete rules for stage 1
    stage-02-planning.md      ← complete rules for stage 2

*See sub-skills for full details.*

## 4. Actionable Content


Every section should guide action:

```markdown
