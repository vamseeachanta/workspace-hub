---
title: "Workflow V2 — Post WRK-094 Improvements"
description: "Revised workspace-hub workflow after queue triage, cross-review tooling, pipeline streamlining, and skill cleanup"
version: "2.0"
module: "workflow-improvement"
created: "2026-02-03"
---

# Workflow V2 — Post WRK-094 Improvements

## Overview

WRK-094 conducted a comprehensive review and improvement of the workspace-hub workflow across five phases. This document captures the revised workflow, new tooling, and operational improvements.

## Changes Summary

### Phase 1: Queue Triage & State Fix

The work queue had grown to 78 pending items with only 16 processed (17% throughput). State.yaml had drifted out of sync (last_id: 85 vs actual highest WRK-093).

Actions taken:
- **12 items archived** (completed, superseded, or no longer relevant)
- **13 items reprioritized** (high-priority inflation reduced from 46% to ~23%)
- **12 items deferred** (moved to low priority with clear rationale)
- **10 items complexity-normalized** (reassigned complexity based on actual scope)
- **5 merge groups identified** (overlapping items consolidated)
- **next-id.sh rebuilt** with auto-correction: scans all queue directories (pending, working, blocked, archive) for the actual max WRK-NNN ID and auto-corrects state.yaml if it drifts behind
- **INDEX.md regenerated** with accurate counts (89 total: 63 pending, 23 archived at time of generation)
- **state.yaml fixed** to last_id: 95 with total_processed: 29, total_archived: 29

### Phase 2: Cross-Review Tooling

The CLAUDE.md mandated cross-review with OpenAI Codex and Google Gemini, but no tooling existed to support it.

New scripts created in `scripts/review/`:
- **cross-review.sh** — Unified entry point. Accepts a file or git diff range, a reviewer target (claude, codex, gemini, or all), and a review type (plan, implementation, commit). Results saved to `scripts/review/results/`.
- **submit-to-codex.sh** — Submits content to OpenAI Codex API for review.
- **submit-to-gemini.sh** — Submits content to Google Gemini API for review.
- **3 prompt templates** in `scripts/review/prompts/`:
  - `plan-review.md` — For reviewing specs and plans
  - `implementation-review.md` — For reviewing code changes
  - `commit-review.md` — For reviewing commit diffs

Usage:
```bash
# Review a spec with all three reviewers
./scripts/review/cross-review.sh specs/modules/my-feature/plan.md all --type plan

# Review a git diff with Codex only
./scripts/review/cross-review.sh "main..feature-branch" codex --type implementation

# Review latest commit with Gemini
./scripts/review/cross-review.sh "HEAD~1..HEAD" gemini --type commit
```

### Phase 3: Pipeline Streamlining

Route C (the standard work item processing pipeline) was reduced from 6 steps to 5 by merging Plan and Explore into a single step.

**New 5-step Route C pipeline:**

| Step | Action | Description |
|------|--------|-------------|
| 1 | **Plan+Explore** | Combined planning and codebase exploration in a single pass |
| 2 | **Implement** | Write code following the plan |
| 3 | **Test** | TDD cycle: write tests, verify, refactor |
| 4 | **Review** | Cross-review using `scripts/review/cross-review.sh` |
| 5 | **Archive** | Mark complete, archive work item |

New process features added:
- **Auto-claim**: When a work item moves to "working", it auto-assigns the current agent
- **Auto-archive**: Completed items with passing tests auto-move to archive
- **Batch processing mode**: Process multiple related items in a single session
- **Dependency enforcement**: Items with `blocked_by` entries cannot be claimed until dependencies resolve

### Phase 4: Skill Ecosystem Cleanup

Audited 12 skills with fewer than 50 lines of content. All were deemed valuable and retained.

Registry consolidation:
- **skills-index.yaml** is now the single authoritative registry (222 skills across 27 categories)
- **skill-registry.yaml** — deprecated with header notice, will be removed in future cleanup
- **agent-library/registry.yaml** — deprecated with header notice, will be removed in future cleanup
- Archive README verified complete and accurate

## Queue Health Report

| Metric | Before (WRK-094) | After (WRK-094) |
|--------|-------------------|------------------|
| Pending items | 78 | 63 |
| Processed items | 16 | 29 |
| Throughput | 17% | 30%+ |
| High-priority items | 46% | ~23% |
| state.yaml accuracy | Drifted (last_id: 85 vs actual 93) | Validated (last_id: 95, auto-correct enabled) |
| Cross-review tooling | None (mandate only) | Full tooling (3 scripts, 3 templates) |
| Registries | 3 separate (skill-registry.yaml, agent-library/registry.yaml, skills-index.yaml) | 1 authoritative (skills-index.yaml) |
| Pipeline steps (Route C) | 6 | 5 |
| Auto-claim | No | Yes |
| Auto-archive | No | Yes |
| Batch mode | No | Yes |
| Dependency enforcement | No | Yes |

## Authoritative References

| Asset | Location |
|-------|----------|
| Skills registry | `.claude/skills-index.yaml` |
| Cross-review scripts | `scripts/review/` |
| Queue state | `.claude/work-queue/state.yaml` |
| Queue index | `.claude/work-queue/INDEX.md` |
| Next ID generator | `scripts/work-queue/next-id.sh` |
| Work items (pending) | `.claude/work-queue/pending/` |
| Work items (archive) | `.claude/work-queue/archive/` |
