# Work Queue Skill for workspace-hub

> Inspired by [bladnman/do-work](https://github.com/bladnman/do-work) - adapted for multi-repo orchestration.

## Summary

Create a `/work` skill that maintains a queue of work items (features, bugs, tasks) across workspace-hub repositories. Two-phase system: **Capture** (rapidly log items) and **Process** (triage + delegate to subagents by complexity).

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage location | Centralized: `.claude/work-queue/` | Follows existing pattern (state/skills centralized in workspace-hub) |
| Git tracking | Queue dirs gitignored; archive optionally tracked | Active queue is ephemeral; archive provides audit trail |
| Command name | `/work` | Matches do-work convention, concise |
| Item format | YAML frontmatter + markdown body | Consistent with specs/plan templates |
| ID scheme | `WRK-NNN-slug.md` | Sequential, human-readable |

## Files to Create

### Skill Definition (3 files)

1. **`.claude/skills/coordination/workspace/work-queue/SKILL.md`**
   - Metadata: name, version, triggers, capabilities, tools
   - Command routing table (`/work add`, `/work run`, `/work list`, etc.)
   - Full documentation following claude-reflect SKILL.md pattern

2. **`.claude/skills/coordination/workspace/work-queue/actions/capture.md`**
   - Parsing input: single vs. multi-request detection
   - Duplicate checking against pending/working/blocked
   - Complexity classification (simple <200 words; complex >500 words or 3+ features)
   - File creation in `pending/` with proper template
   - Context document creation for large inputs (`CONTEXT-NNN-slug.md`)

3. **`.claude/skills/coordination/workspace/work-queue/actions/process.md`**
   - Select next item by priority from `pending/`
   - Triage: classify complexity -> Route A/B/C
   - Claim: move to `working/`, update frontmatter
   - Pre-check: repo-readiness on target repos
   - Delegate to subagents per route
   - Test, commit, archive pipeline
   - Failure handling (3 attempts -> mark failed)

### Scripts (4 files)

4. **`scripts/next-id.sh`** - Scan all queue dirs for max WRK-NNN, return next
5. **`scripts/queue-status.sh`** - Report counts per state (pending/working/blocked/archived)
6. **`scripts/archive-item.sh`** - Move to `archive/YYYY-MM/` with completion metadata
7. **`scripts/queue-report.sh`** - Generate summary for reflect integration

### Templates (3 files)

8. **`templates/work-item-simple.md`** - Basic work item (id, title, status, priority, complexity, target_repos, acceptance criteria)
9. **`templates/work-item-complex.md`** - Extends simple with detailed requirements, constraints, architecture notes, open questions
10. **`templates/context-document.md`** - Companion doc for large inputs (preserves verbatim request, links to extracted WRK items)

All skill files under: `.claude/skills/coordination/workspace/work-queue/`

### Queue Directory Structure (created at runtime)

```
.claude/work-queue/
  pending/          # Items awaiting processing
  working/          # Currently being processed (max 1-2)
  blocked/          # Awaiting dependencies (repo dirty, PR pending, etc.)
  archive/YYYY-MM/  # Completed items with full audit trail
  assets/           # Screenshots, context files
  state.yaml        # Counters, stats, last processed
```

## Files to Modify

1. **`.gitignore`** - Add `.claude/work-queue/` exceptions (queue dirs ignored, archive optionally tracked)
2. **`.claude/skills/coordination/workspace/claude-reflect/scripts/daily-reflect.sh`** - Add checklist item `r) Work queue status` (pending/working/blocked counts, stale items)

## Command Interface

| Command | Action | Description |
|---------|--------|-------------|
| `/work add <desc>` | Capture | Log one or more work items |
| `/work run` or `/work` | Process | Process next item in queue |
| `/work list` | Status | Show all pending/working/blocked items |
| `/work status WRK-NNN` | Detail | Show specific item details |
| `/work prioritize` | Reorder | Interactive priority adjustment |
| `/work archive WRK-NNN` | Archive | Manually archive an item |
| `/work report` | Report | Queue health summary |

**Smart routing**: Action verbs (run, go, start) -> Process. Descriptive content -> Capture.

## Processing Pipeline (Complexity Routing)

```
Route A (Simple):  Triage -> Implement -> Test -> Archive
Route B (Medium):  Triage -> Explore -> Implement -> Test -> Archive
Route C (Complex): Triage -> Plan (spec) -> Explore -> Implement -> Test -> Review -> Archive
```

| Complexity | Criteria | Route |
|------------|----------|-------|
| Simple | Single config/value change, clear files, <50 words, 1 repo | A |
| Medium | Clear outcome, unknown files, 1-2 repos, 50-200 words | B |
| Complex | Architectural, 3+ repos, ambiguous scope, >200 words | C |

Route C items generate a spec in `specs/modules/` using existing plan templates. Linked via `spec_ref` field.

## Work Item Format

```yaml
---
id: WRK-001
title: Brief descriptive title
status: pending  # pending | claimed | in_progress | testing | done | failed | blocked
priority: medium # high | medium | low
complexity: simple # simple | medium | complex
created_at: 2026-01-28T10:00:00Z
target_repos:
  - aceengineer-website
commit:
spec_ref:
related: []
blocked_by: []
---

# Title

## What
[1-3 sentence description]

## Why
[Rationale]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---
*Source: [verbatim original request]*
```

## Multi-Repo Handling

- Each item has `target_repos` field listing affected repositories
- Pre-check via repo-readiness on each target repo before processing
- If repo has dirty state or failing tests -> item moves to `blocked/` with reason
- Route C items get a cross-repo implementation sequence from Plan agent
- Commits per-repo with work item ID: `feat(work-queue): WRK-NNN - description`
- Workspace-hub submodule refs updated after all repos committed

## Integration Points

| System | Integration |
|--------|-------------|
| claude-reflect | New checklist item: queue counts, stale item alerts (>7 days blocked) |
| skill-learner | Post-archive feedback: triage accuracy tracking via route field |
| repo-readiness | Pre-check before processing each work item |
| specs/modules | Route C items generate plan files with bidirectional linking |

## Implementation Phases

### Phase 1: Foundation
- Create skill directory structure and SKILL.md
- Implement `next-id.sh` and `queue-status.sh`
- Write `capture.md` action (single-item capture)
- Write `process.md` action (Route A only)
- Create work item templates
- Test end-to-end with a simple single-repo item

### Phase 2: Full Pipeline
- Add Route B and Route C to `process.md`
- Multi-request detection in capture
- Context document creation for complex inputs
- `blocked/` state management
- Multi-repo coordination logic
- `archive-item.sh` with audit metadata
- Spec generation for Route C items

### Phase 3: Integration
- Add work queue checklist to `daily-reflect.sh` (section r)
- `queue-report.sh` for reflect integration
- Wire repo-readiness pre-check
- Update `.gitignore`

## Verification

1. **Capture test**: `/work add Fix login redirect in aceengineer-website` -> creates `WRK-001-fix-login-redirect.md` in `pending/`
2. **List test**: `/work list` -> shows pending items with priority and target repos
3. **Process test**: `/work run` -> triages item, delegates to subagent, archives on completion
4. **Multi-item test**: `/work add` with multiple features -> creates separate WRK files
5. **Script test**: `bash scripts/queue-status.sh` -> outputs correct counts
6. **Reflect test**: After adding checklist item, `daily-reflect.sh` reports queue health
