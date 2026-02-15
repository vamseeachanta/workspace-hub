# Work Queue Process

> Operational reference for the two-phase work queue system.
> For the full skill definition, see `../.claude/skills/coordination/workspace/work-queue/SKILL.md`.

## Overview

The work queue tracks features, bugs, and tasks across all workspace-hub repositories. Items flow through a five-stage pipeline: **Capture, Triage, Plan, Process, Archive**. The workspace-hub queue is the master; repo-local copies are synced mirrors.

State is tracked in `state.yaml` (counters), individual `WRK-NNN.md` files (item detail), and `INDEX.md` (generated listing).

## Pipeline Stages

### 1. Capture

**Trigger**: `/work add <description>` or batch add.

- Parser determines single vs. multi-item input.
- Duplicate check against pending/working/blocked directories.
- Initial complexity classification: simple (<50 words), medium (50-200), complex (>200 or 3+ features).
- File created in `pending/` using the frontmatter template (see Conventions below).
- Large inputs get a context document in `assets/`.
- `state.yaml` `last_id` counter incremented.
- INDEX.md regenerated: `python3 scripts/generate-index.py`.

### 2. Triage

**Trigger**: `/work run` or `/work` selects next item by priority.

- Priority: `high > medium > low`.
- Complexity confirmed or reclassified: `simple | medium | complex`.
- Dependencies checked: `blocked_by` items must be archived before processing.
- Complexity determines routing:

| Route | Complexity | Criteria |
|-------|-----------|----------|
| A | simple | Single config/value change, 1 repo, <50 words |
| B | medium | Clear outcome, 1-2 repos, 50-200 words |
| C | complex | Architectural, 3+ repos, >200 words |

### 3. Plan

**Every item requires an approved plan before implementation.**

| Route | Plan location | Depth | Review |
|-------|--------------|-------|--------|
| A | `## Plan` section in item body | 3-5 bullet points | Self-review |
| B | `## Plan` section in item body | Numbered steps with file paths and test strategy | Cross-review (3 agents) |
| C | Separate spec in `specs/modules/` linked via `spec_ref` | Full spec from template | Cross-review (3 agents) |

**Plan gate workflow**:
1. Check if plan/spec already exists (auto-detected from `spec_ref` or `## Plan` body section).
2. If missing, generate plan at appropriate depth.
3. Present to user, wait for explicit approval.
4. Update item: add plan content (A/B) or link spec (C), set `plan_approved: true`.
5. No implementation begins until plan is confirmed.

**Spec naming**: `wrk-NNN-<short-description>.md` (not random codenames).

**Cross-review** (Route B/C): Submit to Claude (inline), Codex CLI, and Gemini CLI. Minimum 3 reviewers. Fix MAJOR findings before proceeding; document MINOR deferrals.

### 4. Process

**Trigger**: Plan approved, item auto-claimed.

**Wrapper enforcement (required)**:

```bash
scripts/agents/session.sh init --provider <claude|codex|gemini>
scripts/agents/work.sh --provider <orchestrator> run
scripts/agents/plan.sh --provider <orchestrator> WRK-NNN
scripts/agents/execute.sh --provider <orchestrator> WRK-NNN
scripts/agents/review.sh WRK-NNN --all-providers
```

- Session-started provider is orchestrator for that session.
- Non-orchestrator providers run as subagents and cannot bypass plan gates.

- Item moved from `pending/` to `working/`, frontmatter `status` updated.
- INDEX.md regenerated.
- Pre-check: repo-readiness on `target_repos`.
- Implementation follows TDD (tests before code).
- Route B/C: per-phase cross-review after each implementation phase.
- Commits use format: `feat(scope): WRK-NNN - description`.
- 3 attempts before marking `status: failed`.
- Batch mode: `/work run --batch` processes all Route A items in sequence.

**Testing tiers**:
- Pre-commit: `scripts/test/test-commit.sh` (changed files only)
- Per-task: `scripts/test/test-task.sh <module>` (module under work)
- Full session: `scripts/test/test-session.sh` (regression before push)

### 5. Archive

**Trigger**: All acceptance criteria met, or manual `/work archive WRK-NNN`.

- Script: `scripts/archive-item.sh WRK-NNN`
  1. Updates `status: archived`, sets `completed_at`.
  2. Moves file to `archive/YYYY-MM/`.
  3. Runs `on-complete-hook.sh` (checks brochure status, outputs recommended tasks).
  4. Regenerates INDEX.md.
- `state.yaml` `total_archived` counter updated.
- Repo-local copies also moved to target repo `archive/YYYY-MM/`.
- Archived items auto-set to `percent_complete: 100` in INDEX.md.

## Directory Structure

```
.claude/work-queue/
  INDEX.md              # Auto-generated listing (do not edit)
  process.md            # This file
  state.yaml            # Counters: last_id, last_processed, stats
  pending/              # Items awaiting processing
  working/              # Items currently being executed (max 1-2)
  blocked/              # Items awaiting dependencies
  archive/              # Completed items
    YYYY-MM/            #   Organized by month
  assets/               # Context files, screenshots
  scripts/
    generate-index.py   # Regenerate INDEX.md from all items
    archive-item.sh     # Move item to archive with hooks
    on-complete-hook.sh # Post-archive brochure tracking
```

## State Management

**`state.yaml`** tracks:
- `last_id`: Highest WRK-NNN assigned (monotonically increasing).
- `last_processed`: Most recently processed item ID.
- `stats.total_captured`, `stats.total_processed`, `stats.total_archived`.

**`INDEX.md`** is regenerated (not edited) after every mutation:
```bash
python3 .claude/work-queue/scripts/generate-index.py
```
This scans all directories, parses frontmatter, and produces multi-view tables (by status, priority, complexity, repository, dependencies). Runs in <2 seconds for 100+ items.

**Resync**: If INDEX.md drifts from reality, delete it and regenerate. The script is idempotent.

## Commands

| Command | Action |
|---------|--------|
| `/work add <desc>` | Capture one or more items |
| `/work run` or `/work` | Process next item by priority |
| `/work list` | Display INDEX.md (filter by repo/status/priority) |
| `/work status WRK-NNN` | Show specific item details |
| `/work prioritize` | Interactive priority adjustment |
| `/work archive WRK-NNN` | Manually archive an item |
| `/work report` | Queue health summary |
| `python3 scripts/generate-index.py` | Regenerate INDEX.md |
| `scripts/archive-item.sh WRK-NNN` | Archive with hooks |

## Conventions

### Frontmatter (required fields)

```yaml
---
id: WRK-NNN
title: Brief descriptive title
status: pending          # pending | working | blocked | archived | failed
priority: medium         # high | medium | low
complexity: medium       # simple | medium | complex
created_at: 2026-01-29T00:00:00Z
target_repos:
  - repo-name
target_module:           # module within repo (e.g. bsee, hse, marine_safety, hull_library)
commit:                  # SHA after implementation
spec_ref:                # path to spec file (Route C)
related: []              # related WRK IDs
blocked_by: []           # WRK IDs that must complete first
plan_reviewed: false     # true after cross-review
plan_approved: false     # true after user approval
percent_complete: 0      # 0-100
brochure_status:         # pending | updated | synced | n/a
---
```

### Body structure

```markdown
# Title

## What
[1-3 sentence description]

## Why
[Rationale]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Plan
[Added during Plan stage]

---
*Source: [verbatim original request]*
```

### Commit messages for work items

```
feat(scope): WRK-NNN - description
fix(scope): WRK-NNN - description
chore(work-queue): archive WRK-NNN, update submodules
```

### Cross-review log format (in spec or item body)

```markdown
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1   | 2026-02-12 | Claude | MINOR | 4: ... | 4/4 |
```
