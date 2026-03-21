---
name: work-queue
description: Maintains a queue of work items (features, bugs, tasks) across workspace-hub
  repositories with two-phase capture and process pipeline
version: 1.8.0
category: coordination
type: skill
trigger: manual
auto_execute: false
capabilities:
- work_item_capture
- complexity_classification
- multi_repo_coordination
- priority_management
- processing_pipeline
- queue_state_management
- archive_audit_trail
- reflect_integration
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
- Task
- EnterPlanMode
- ExitPlanMode
related_skills:
- claude-reflect
- skill-learner
- repo-sync
- session-start
- session-end
- workflow-gatepass
- wrk-lifecycle-testpack
- work-queue-workflow
- comprehensive-learning
scripts:
- next-id.sh
- queue-status.sh
- archive-item.sh
- queue-report.sh
- ../../../../scripts/agents/session.sh
- ../../../../scripts/agents/work.sh
- ../../../../scripts/agents/plan.sh
- ../../../../scripts/agents/execute.sh
- ../../../../scripts/agents/review.sh
requires: []
see_also:
- work-queue-command-interface
- work-queue-canonical-20-stage-lifecycle
- work-queue-stage-contracts-summary
- work-queue-complexity-routing
- work-queue-feature-layer-epic-level-work
- work-queue-cross-review-route-bc
- work-queue-planning-requirement
- work-queue-checkpoint-resume
- work-queue-work-item-format
- work-queue-machine-wrk-id-ranges
- work-queue-queue-directory-structure
- work-queue-key-scripts
- work-queue-work-execution-principle-scripts-over-llm-overhead
- work-queue-parallel-work-policy
- work-queue-scope-discipline
- work-queue-archival-safety
- work-queue-integration-points
tags: []
---

# Work Queue

## Quick Start

```bash
scripts/agents/session.sh init --provider claude  # once per session
/work add <description>                           # capture
/work run                                         # process next item
/work list [--by-category] [--category <n>]       # browse queue
/work status WRK-NNN                              # inspect item
```

## GOTCHA: `/work run` MUST use dispatch-run.sh

**Do NOT call group runners (run-plan.sh, run-execute.sh, etc.) directly.**
Always start with `bash scripts/work-queue/dispatch-run.sh WRK-NNN` and follow its output.
A L3 hook will block group runner calls without a dispatch breadcrumb.

## Version History

- **2.0.0** (2026-03-11): Feature layer section added (WRK-1129)

## Sub-Skills

- [Command Interface](command-interface/SKILL.md)
- [Canonical 20-Stage Lifecycle](canonical-20-stage-lifecycle/SKILL.md)
- [Stage Contracts (summary)](stage-contracts-summary/SKILL.md)
- [Complexity Routing](complexity-routing/SKILL.md)
- [Feature Layer (Epic-level work)](feature-layer-epic-level-work/SKILL.md)
- [Cross-Review (Route B/C)](cross-review-route-bc/SKILL.md)
- [Planning Requirement](planning-requirement/SKILL.md)
- [Checkpoint & Resume](checkpoint-resume/SKILL.md)
- [Work Item Format](work-item-format/SKILL.md)
- [Machine WRK ID Ranges](machine-wrk-id-ranges/SKILL.md)
- [Queue Directory Structure](queue-directory-structure/SKILL.md)
- [Key Scripts](key-scripts/SKILL.md)
- [Work Execution Principle: Scripts Over LLM Overhead](work-execution-principle-scripts-over-llm-overhead/SKILL.md)
- [Parallel Work Policy](parallel-work-policy/SKILL.md)
- [Scope Discipline](scope-discipline/SKILL.md)
- [Archival Safety](archival-safety/SKILL.md)
- [Integration Points](integration-points/SKILL.md)
