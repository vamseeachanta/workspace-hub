---
# =============================================================================
# PLAN METADATA — WRK-094
# =============================================================================

title: "Plan, reassess, and improve the workspace-hub workflow"
description: "Comprehensive workflow overhaul: fix queue health, build cross-review tooling, improve throughput, clean skill ecosystem"
version: "1.0"
module: "workflow-improvement"
source_work_item: WRK-094

session:
  id: "2026-02-03-wrk094"
  agent: "claude-opus-4-5"

review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
    claude:
      status: "pending"
      iteration: 0
      feedback: ""
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  ready_for_next_step: false

status: "draft"
progress: 0
priority: "high"
tags: [workflow, meta, cross-review, queue-health, throughput]

created: "2026-02-03"
updated: "2026-02-03"
target_completion: ""

links:
  spec: "specs/modules/workflow-improvement/plan.md"
  branch: "chore/wrk-094-workflow-improvement"
---

# Plan, Reassess, and Improve the Workspace-Hub Workflow

> **Module**: workflow-improvement | **Status**: draft | **WRK-094** | **2026-02-03**

## Summary

The workspace-hub workflow has accumulated 94 work items with only 17% throughput (16 processed). Cross-review with Codex/Gemini is mandated but not implemented. The skill ecosystem has dead weight. This plan addresses all of these through 5 phases, each with mandatory cross-review gates.

---

## Diagnosis

| Metric | Value | Assessment |
|--------|-------|------------|
| Items captured | 94 | High capture rate |
| Items processed | 16 (17%) | **Critical — queue is a backlog, not a pipeline** |
| Pending items | 77 | Unmanageable without triage |
| Complex (Route C) | 50% of pending | Heavy process overhead |
| High priority | 41% of pending | Priority inflation — everything is "high" |
| Cross-review tooling | 0% implemented | Mandated in CLAUDE.md, never built |
| Skill stubs (<150 lines) | 46 skills | 17% of 272 skills are incomplete |
| Registry files | 3 separate | Fragmented source of truth |
| state.yaml drift | last_id was 9 behind | No validation on counter |

**Root cause**: The workflow optimizes for _capture_ but creates friction at _processing_. Route C items (50% of queue) require a 6-step pipeline that's never been automated.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: 3 review iterations by Claude, OpenAI Codex, and Google Gemini before implementation begins. Each task implementation gets 1 cross-review. Each commit gets 3 cross-reviews.

### Plan Review Status

| Gate | Status |
|------|--------|
| Legal Sanity | ⬜ pending |
| Iterations (>= 3) | ⬜ 0/3 |
| Claude | ⬜ pending |
| OpenAI Codex | ⬜ pending |
| Google Gemini | ⬜ pending |
| **Ready** | ⬜ false |

### Plan Review Log

| Iter | Date | Reviewer | Status | Feedback Summary |
|------|------|----------|--------|------------------|
| 1 | | Claude | Pending | |
| 1 | | Codex | Pending | |
| 1 | | Gemini | Pending | |
| 2 | | Claude | Pending | |
| 2 | | Codex | Pending | |
| 2 | | Gemini | Pending | |
| 3 | | Claude | Pending | |
| 3 | | Codex | Pending | |
| 3 | | Gemini | Pending | |

---

## Phases

### Phase 1: Queue Triage & State Fix (Simple — Route A)

**Goal**: Reduce pending queue from 77 to a manageable backlog. Fix state management.

- [ ] **1.1** Bulk triage all 77 pending items into categories:
  - **Keep**: Still relevant, correctly prioritized
  - **Reprioritize**: Priority inflation fix (high→medium, medium→low)
  - **Merge**: Duplicate or overlapping items → combine
  - **Archive-stale**: Items >30 days old with no progress or relevance
  - **Defer**: Valid but not actionable now → mark `priority: low`
- [ ] **1.2** Fix state.yaml validation — add a check in `next-id.sh` that scans all dirs for max ID
- [ ] **1.3** Regenerate INDEX.md with accurate counts post-triage
- [ ] **1.4** Normalize complexity field — replace non-standard values (`high`, `low`, `moderate`) with `simple`/`medium`/`complex`

**Files to modify**:
- `/mnt/github/workspace-hub/.claude/work-queue/pending/WRK-*.md` (bulk edits)
- `/mnt/github/workspace-hub/.claude/work-queue/state.yaml`
- `/mnt/github/workspace-hub/.claude/skills/coordination/workspace/work-queue/scripts/next-id.sh`
- `/mnt/github/workspace-hub/.claude/work-queue/INDEX.md` (regenerated)

**Acceptance**: Pending count ≤ 30. All items use standard complexity values. state.yaml matches actual max ID.

**Cross-review**: 1x post-implementation (Claude reviews triage decisions)

---

### Phase 2: Cross-Review Tooling (Medium — Route B)

**Goal**: Build the missing cross-review infrastructure so that plans, implementations, and commits can be reviewed by Claude + Codex + Gemini.

- [ ] **2.1** Create `scripts/review/cross-review.sh` — a unified script that:
  - Accepts a file path (plan, diff, or commit range)
  - Accepts reviewer target (`claude`, `codex`, `gemini`, `all`)
  - Formats content for review submission
  - Records feedback in structured format
  - Updates review metadata in plan frontmatter
- [ ] **2.2** Create `scripts/review/submit-to-codex.sh` — pipes content to `codex` CLI with review prompt, captures stdout as structured feedback
- [ ] **2.3** Create `scripts/review/submit-to-gemini.sh` — pipes content to `gemini` CLI with review prompt, captures stdout as structured feedback
- [ ] **2.4** Create review prompt templates at `scripts/review/prompts/`:
  - `plan-review.md` — for reviewing plans/specs
  - `implementation-review.md` — for reviewing code changes
  - `commit-review.md` — for reviewing commits before push
- [ ] **2.5** Update work queue process action to integrate cross-review gates:
  - Plan phase: 3 iterations before proceeding
  - Implementation: 1 review before commit
  - Commit: 3 reviews before marking done

**Files to create**:
- `scripts/review/cross-review.sh`
- `scripts/review/submit-to-codex.sh`
- `scripts/review/submit-to-gemini.sh`
- `scripts/review/prompts/plan-review.md`
- `scripts/review/prompts/implementation-review.md`
- `scripts/review/prompts/commit-review.md`

**Files to modify**:
- `/mnt/github/workspace-hub/.claude/skills/coordination/workspace/work-queue/actions/process.md`

**Acceptance**: Running `scripts/review/cross-review.sh <file> all` submits to all 3 reviewers and records feedback. Review gates block progression until thresholds met.

**Cross-review**: 1x post-implementation + 3x on commit

---

### Phase 3: Process Pipeline Streamlining (Medium — Route B)

**Goal**: Reduce friction in the process phase to improve throughput from 17% toward 50%+.

- [ ] **3.1** Simplify Route C pipeline — merge "Explore" into "Plan" phase (reduce 6 steps to 5):
  ```
  Current:  Plan → Explore → Implement → Test → Review → Archive
  Proposed: Plan+Explore → Implement → Test → Review → Archive
  ```
- [ ] **3.2** Add auto-claim — when `/work run` starts, automatically move item to `working/` and update frontmatter (currently manual)
- [ ] **3.3** Add auto-archive — when all acceptance criteria checked and reviews pass, auto-move to `archive/YYYY-MM/`
- [ ] **3.4** Add batch processing mode — `/work run --batch` processes all Route A (simple) items in sequence without manual intervention
- [ ] **3.5** Fix dependency enforcement — before claiming an item, check `blocked_by` field and skip if blockers are unresolved

**Files to modify**:
- `/mnt/github/workspace-hub/.claude/skills/coordination/workspace/work-queue/SKILL.md` (update pipeline docs)
- `/mnt/github/workspace-hub/.claude/skills/coordination/workspace/work-queue/actions/process.md`
- `/mnt/github/workspace-hub/.claude/skills/coordination/workspace/work-queue/scripts/archive-item.sh`

**Acceptance**: Route A items can be batch-processed. Route C pipeline is 5 steps. Blocked items are skipped automatically.

**Cross-review**: 1x post-implementation + 3x on commit

---

### Phase 4: Skill Ecosystem Cleanup (Simple — Route A)

**Goal**: Reduce dead weight, consolidate registries, improve signal-to-noise.

- [ ] **4.1** Audit 46 under-documented skills (<150 lines) — classify each as:
  - **Complete**: Flesh out to ≥150 lines
  - **Archive**: Move to `_archive/` with deprecation note
  - **Delete**: Remove if truly empty/unused
- [ ] **4.2** Consolidate 3 registry files into single source of truth:
  - Keep `skills-index.yaml` as master
  - Generate `skill-registry.yaml` and `agent-library/registry.yaml` from it (or remove them)
- [ ] **4.3** Convert 81 scattered TODOs into work queue items (batch `/work add`)
- [ ] **4.4** Document archived agents — add "why deprecated" notes to `_archive/` README

**Files to modify**:
- `/mnt/github/workspace-hub/.claude/skills/` (46 skills audited)
- `/mnt/github/workspace-hub/.claude/skills-index.yaml` (master registry)
- `/mnt/github/workspace-hub/.claude/skill-registry.yaml` (deprecate or auto-generate)
- `/mnt/github/workspace-hub/.claude/agent-library/registry.yaml` (deprecate or auto-generate)
- `/mnt/github/workspace-hub/.claude/agent-library/_archive/README.md`

**Acceptance**: No skills under 50 lines remain. Single authoritative registry. TODO count reduced by 50%+.

**Cross-review**: 1x post-implementation + 3x on commit

---

### Phase 5: Documentation & Verification (Simple — Route A)

**Goal**: Document the revised workflow. Verify all changes end-to-end.

- [ ] **5.1** Write revised workflow doc at `specs/modules/workflow-improvement/workflow-v2.md`
- [ ] **5.2** Update CLAUDE.md if any cross-review or pipeline conventions changed
- [ ] **5.3** Run end-to-end verification:
  - Capture a test item: `/work add Test item for verification`
  - Process it: `/work run`
  - Verify cross-review gates trigger
  - Verify auto-claim and auto-archive work
  - Verify state.yaml stays in sync
  - Archive test item
- [ ] **5.4** Run `/work report` and confirm queue health metrics improved

**Files to create**:
- `specs/modules/workflow-improvement/workflow-v2.md`

**Files to modify**:
- `/mnt/github/workspace-hub/CLAUDE.md` (if conventions changed)

**Acceptance**: E2E test passes. Queue report shows improved metrics. Documentation complete.

**Cross-review**: 3x on final commit (Claude + Codex + Gemini)

---

## Task Dependencies

```
Phase 1 (Queue Triage)
  ↓
Phase 2 (Cross-Review Tooling)  ← enables review gates for Phase 3-5
  ↓
Phase 3 (Pipeline Streamlining) ← uses cross-review from Phase 2
  ↓
Phase 4 (Skill Cleanup)         ← independent, but benefits from streamlined pipeline
  ↓
Phase 5 (Documentation & E2E)   ← must be last, verifies everything
```

## Review Protocol Per Phase

| Phase | Plan Review | Implementation Review | Commit Review |
|-------|-------------|----------------------|---------------|
| 1 (Triage) | N/A (bulk edit) | 1x Claude | 3x (Claude + Codex + Gemini) |
| 2 (Cross-Review) | 3x iterations | 1x per task | 3x |
| 3 (Pipeline) | N/A | 1x per task | 3x |
| 4 (Skill Cleanup) | N/A | 1x Claude | 3x |
| 5 (Docs & E2E) | N/A | 1x Claude | 3x |

**Overall plan**: 3 iterations (this document) before any implementation begins.

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Plan Review Iteration 1 | Pending | |
| Plan Review Iteration 2 | Pending | |
| Plan Review Iteration 3 | Pending | |
| Plan Approved | Pending | |
| Phase 1: Queue Triage | Pending | |
| Phase 2: Cross-Review Tooling | Pending | |
| Phase 3: Pipeline Streamlining | Pending | |
| Phase 4: Skill Cleanup | Pending | |
| Phase 5: Documentation & E2E | Pending | |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-03 | 2026-02-03-wrk094 | claude-opus-4-5 | Plan created from 3 exploration agents + 1 plan agent |
