---
name: gsd:autonomous
description: Run all remaining phases autonomously — discuss→plan→execute per phase
argument-hint: "[--from N]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - Task
---
<objective>
Execute all remaining milestone phases autonomously. For each phase: discuss → plan → execute. Pauses only for user decisions (grey area acceptance, blockers, validation requests).

Uses ROADMAP.md phase discovery and Skill() flat invocations for each phase command. After all phases complete: milestone audit → complete → cleanup.

**Creates/Updates:**
- `.planning/STATE.md` — updated after each phase
- `.planning/ROADMAP.md` — progress updated after each phase
- Phase artifacts — CONTEXT.md, PLANs, SUMMARYs per phase

**After:** Milestone is complete and cleaned up.
</objective>

<execution_context>
@/mnt/local-analysis/workspace-hub/.claude/get-shit-done/workflows/autonomous.md
@/mnt/local-analysis/workspace-hub/.claude/get-shit-done/references/ui-brand.md
</execution_context>

<context>
Optional flag: `--from N` — start from phase N instead of the first incomplete phase.

Project context, phase list, and state are resolved inside the workflow using init commands (`gsd-tools.cjs init milestone-op`, `gsd-tools.cjs roadmap analyze`). No upfront context loading needed.
</context>

<process>
Execute the autonomous workflow from @/mnt/local-analysis/workspace-hub/.claude/get-shit-done/workflows/autonomous.md end-to-end.
Preserve all workflow gates (phase discovery, per-phase execution, blocker handling, progress display).
</process>
