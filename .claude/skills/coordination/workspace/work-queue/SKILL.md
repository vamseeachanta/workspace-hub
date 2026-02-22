---
name: work-queue
description: Maintains a queue of work items (features, bugs, tasks) across workspace-hub repositories with two-phase capture and process pipeline
version: 1.3.0
category: workspace-hub
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
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [claude-reflect, skill-learner, repo-sync]
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
see_also: []
---

# Work Queue Skill

> Two-phase work queue system: **Capture** rapidly logs items, **Process** triages and delegates by complexity. Inspired by bladnman/do-work, adapted for multi-repo orchestration.

## Quick Start

```bash
# Initialize orchestrator for this session (session-started agent rule)
scripts/agents/session.sh init --provider claude

# Capture a work item
/work add Fix login redirect in aceengineer-website

# Process next item in queue
/work run

# List all pending items
/work list

# Check specific item
/work status WRK-001

# Queue health report
/work report
```

## Command Interface

| Command | Action | Description |
|---------|--------|-------------|
| `/work add <desc>` | Capture | Log one or more work items |
| `/work run` or `/work` | Process | Process next item in queue |
| `/work list` | Status | Read and display `.claude/work-queue/INDEX.md` |
| `/work status WRK-NNN` | Detail | Show specific item details |
| `/work prioritize` | Reorder | Interactive priority adjustment |
| `/work archive WRK-NNN` | Archive | Manually archive an item |
| `/work report` | Report | Queue health summary |

Smart routing: Action verbs (run, go, start) -> Process. Descriptive content -> Capture.

## Orchestration Wrappers (Required for /work run)

When `/work run` (or `/work`) enters processing, enforce wrappers in this order:

```bash
# 1) Orchestrator lock (once per session)
scripts/agents/session.sh init --provider <claude|codex|gemini>

# 2) Work orchestration handoff
scripts/agents/work.sh --provider <orchestrator> run

# 3) Plan gate for selected WRK item
scripts/agents/plan.sh --provider <orchestrator> WRK-NNN

# 4) Implementation stage (orchestrator and subagents)
scripts/agents/execute.sh --provider <orchestrator> WRK-NNN
scripts/agents/execute.sh --provider codex WRK-NNN
scripts/agents/execute.sh --provider gemini WRK-NNN

# 5) Review stage
scripts/agents/review.sh WRK-NNN --all-providers
```

Rules:
- Session-started provider is orchestrator for the session.
- Subagents cannot bypass plan gate or change orchestration state.
- Existing `.claude/work-queue/process.md` remains source of truth.

## Two-Phase System

### Phase 1: Capture
- Parse input for single vs multi-request
- Check duplicates against pending/working/blocked
- Classify complexity (simple <50 words; medium 50-200 words; complex >200 words or 3+ features)
- Create file in `pending/` with proper template
- Create context document for large inputs
- Regenerate INDEX.md: run `python3 .claude/work-queue/scripts/generate-index.py`

### Phase 2: Process
- Select next item by priority from `pending/`
- Triage: classify complexity -> Route A/B/C
- Dependency check: verify `blocked_by` items are archived
- **Plan gate (ALL routes)**: create or confirm a plan with the user before implementation (see Planning Requirement below)
- Auto-claim: move to `working/`, update frontmatter (automatic, no manual step)
- Regenerate INDEX.md after status change
- Pre-check: repo-readiness on target repos
- Delegate to subagents per route
- Test, commit, auto-archive pipeline (archives when all acceptance criteria met)
- Regenerate INDEX.md after archiving
- Failure handling (3 attempts -> mark failed)
- Batch mode: `/work run --batch` processes all Route A items in sequence

## Complexity Routing

```
ALL routes: Triage -> Ensemble Gate (9 agents) -> Synthesis -> Plan Gate -> ...
Route A (Simple):  Implement -> Test -> Archive
Route B (Medium):  Explore -> Implement -> Test -> Archive
Route C (Complex): Explore -> Implement -> Test -> Review -> Archive
```

| Complexity | Criteria | Route |
|------------|----------|-------|
| Simple | Single config/value change, clear files, <50 words, 1 repo | A |
| Medium | Clear outcome, unknown files, 1-2 repos, 50-200 words | B |
| Complex | Architectural, 3+ repos, ambiguous scope, >200 words | C |

**All routes require a plan.** The plan depth scales with complexity (see Planning Requirement below).

## Cross-Review by Phase (Route B/C)

**Route B and C work items must be cross-reviewed after each implementation phase.** This catches issues early and prevents compounding errors across phases.

### Review Agents

All available AI agents must review. Minimum 3 reviewers:

| Agent | Method | Fallback |
|-------|--------|----------|
| Claude | Inline review by orchestrating agent | Always available |
| Codex CLI | `codex review --commit <sha>` or `scripts/review/submit-to-codex.sh --file <path>` | NO_OUTPUT acceptable |
| Gemini CLI | `scripts/review/submit-to-gemini.sh --file <path>` | NO_OUTPUT acceptable |

### Per-Phase Review Workflow

1. **Complete phase implementation** — all files created/modified, smoke tests pass
2. **Create review input** — write implementation summary to `scripts/review/results/wrk-NNN-phase-N-review-input.md`
3. **Submit to all agents in parallel** — Claude inline, Codex and Gemini via background Task agents
4. **Collect findings** — each agent returns a verdict (APPROVE / MINOR / MAJOR) and findings list
5. **Fix MAJOR findings** — address critical issues before proceeding to the next phase
6. **Accept or defer MINOR findings** — document rationale for deferred items
7. **Log results in spec** — update the Review Log table in the spec document with all verdicts and findings

### Review Log Format (in spec document)

```markdown
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1   | 2026-02-12 | Claude | MINOR | 4: description... | 4/4 |
| P1   | 2026-02-12 | Codex  | MAJOR | 6: description... | 4/6 |
| P1   | 2026-02-12 | Gemini | MAJOR | 9: description... | 4/9 |
```

### Route A Exception

Route A (simple) items do not require per-phase cross-review — a single post-implementation self-review is sufficient.

## Testing Tiers

When processing work items, use the appropriate test tier:

| Workflow | Script | When to Use |
|----------|--------|-------------|
| Pre-commit | `scripts/test/test-commit.sh` | After each commit — tests only changed files |
| Per-task | `scripts/test/test-task.sh <module>` | During implementation — tests the module being worked on |
| Full session | `scripts/test/test-session.sh` | Before push or session end — full regression |

The `--wrk WRK-NNN` flag on `test-task.sh` reads `target_repos` from the work item to auto-select modules.

## Planning Requirement

**Every work item must have an approved plan before implementation begins.** This ensures sufficient alignment with the user and prevents wasted effort.

### Plan Depth by Route

| Route | Plan Location | Plan Depth | User Approval |
|-------|--------------|------------|---------------|
| A (Simple) | Inline in work item body (`## Plan` section) | 3-5 bullet points: what files change, what the change is, how to verify | User confirms before implementation |
| B (Medium) | Inline in work item body (`## Plan` section) | Exploration summary + numbered steps with file paths, expected changes, and test strategy | User confirms before implementation |
| C (Complex) | Separate spec in `specs/wrk/WRK-NNN/` (linked via `spec_ref`) | Full spec using `specs/templates/plan-template.md` with architecture, implementation sequence, test plan, and cross-review | User approves spec before implementation |

### Plan Gate Workflow

1. **Check `spec_ref`**: If the work item already has an approved plan, proceed to implementation
2. **No plan exists**: Generate a plan at the appropriate depth for the route
3. **Present to user**: Show the plan and wait for explicit approval
4. **User approves**: Update work item with plan content (Route A/B) or link to spec (Route C), then proceed
5. **User requests changes**: Revise the plan and re-present
6. **No implementation without approval**: Never begin coding until the plan is confirmed

### Pre-Move-to-Working Checklist (HARD GATES — never skip)

Before setting `status: working` on any Route B/C item, verify ALL of the following:

| Gate | Field | Route | Rule |
|------|-------|-------|------|
| Plan approved | `plan_approved: true` | A/B/C | User must have explicitly said yes |
| Plan cross-reviewed | `plan_reviewed: true` | B/C | Set ONLY after Codex + Gemini verdict received — NOT at plan creation time |
| Spec exists | `spec_ref` non-empty | C | Spec must be in `specs/wrk/WRK-NNN/` before moving to working |

**Critical distinction:**
- `plan_approved` = user said "looks good, proceed"
- `plan_reviewed` = Codex and/or Gemini have reviewed the plan and returned a verdict

These are independent steps. Setting `plan_reviewed: true` at the same time as writing the plan is a workflow violation.

### Plan Content (Route A/B — Inline)

Add a `## Plan` section to the work item body:

```markdown
## Plan
- **Files**: `src/foo/bar.py` (edit), `tests/test_bar.py` (new)
- **Change**: Update the `process()` function to handle edge case X
- **Test**: Add unit test for edge case X, verify existing tests pass
- **Verify**: Run `pytest tests/test_bar.py -v`

*Approved by user: 2026-02-08*
```

### Plan Content (Route C — Spec File)

Create spec in `specs/wrk/WRK-NNN/plan.md` using existing plan templates. Link via `spec_ref` in frontmatter.

### Plan Naming Convention

**Plan documents must use descriptive, human-readable names** — not random codenames. The filename should make the plan's purpose immediately obvious for future retrieval.

Format: `wrk-NNN-<short-description>.md`

| Example | Good | Bad |
|---------|------|-----|
| Git cleanup plan | `wrk-098-git-history-cleanup.md` | `enumerated-conjuring-cake.md` |
| Benchmark plan | `wrk-031-diffraction-benchmark.md` | `mighty-gliding-lemur.md` |
| OrcaFlex converter | `wrk-064-orcaflex-format-converter.md` | `harmonic-knitting-gizmo.md` |

Rules:
- Prefix with `wrk-NNN-` to link back to the work item
- Use `kebab-case` for the description portion
- Keep the description to 3-5 words that capture the essence
- Existing randomly-named specs can be renamed incrementally as items are processed

### Compound Integration

Route C items with `compound: true` in frontmatter delegate to the compound engineering loop instead of the standard pipeline:

```
Route C (compound): /compound "<title>" → Plan → Work → Review → Compound → Archive
```

To create a compound work item:
```
/work add --compound "Add OAuth2 authentication to website"
```

This sets `compound: true` in the work item frontmatter, causing the process phase to delegate to `/compound` for the full 4-phase loop.

## Queue Directory Structure

### Master Queue (workspace-hub)
```
workspace-hub/.claude/work-queue/
  pending/          # Items awaiting processing
  working/          # Currently being processed (max 1-2)
  blocked/          # Awaiting dependencies
  archive/YYYY-MM/  # Completed items with audit trail
  assets/           # Screenshots, context files
  state.yaml        # Counters, stats, last processed
```

### Repo-Local Queue (each target repo)
```
<target-repo>/.claude/work-queue/
  pending/          # Items targeting this repo
  working/          # Currently being processed in this repo
  archive/YYYY-MM/  # Completed items
  state.yaml        # Repo-local counters
```

### Repo-Local Specs (all routes with external plans)
```
<target-repo>/specs/modules/<module>/
  plan.md           # Full plan synced from workspace-hub
```

**Source of truth**: workspace-hub is the master. Repo-local copies are synced mirrors for local visibility.

## Work Item Format

```yaml
---
id: WRK-001
title: Brief descriptive title
status: pending
priority: medium  # high | medium | low
complexity: simple  # simple | medium | complex
compound: false     # true = route via /compound instead of standard pipeline
created_at: 2026-01-28T10:00:00Z
target_repos:
  - aceengineer-website
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []  # repos where this item has been mirrored
plan_ensemble: false   # true after 9-agent ensemble planning completes
ensemble_consensus_score: null # 0-100 score from synthesis
plan_reviewed: false   # true when plan has been cross-reviewed
plan_approved: false   # true when user has approved the plan
percent_complete: 0    # 0-100, auto-set to 100 on archive
brochure_status:       # pending | updated | synced | n/a
---

# Title

## What
[1-3 sentence description]

## Why
[Rationale]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Agentic AI Horizon

- Does this work boost agentic AI capability in this ecosystem?
- Will an agent handle this better in 3–4 months — if so: (a) wait, (b) invest differently now, (c) park it as a future WRK item to revisit in 1–2 months, or (d) do the groundwork now and park the rest for when capability catches up?
- How should this work be shaped to maximise future leverage, not just complete the task?

---
*Source: [verbatim original request]*
```

## Multi-Repo Handling

- Each item has `target_repos` field listing affected repositories
- Pre-check via repo-readiness on each target repo before processing
- If repo has dirty state or failing tests -> item moves to `blocked/` with reason
- Route C items get cross-repo implementation sequence from Plan agent
- Commits per-repo with work item ID: `feat(work-queue): WRK-NNN - description`
- Workspace-hub submodule refs updated after all repos committed

## Repo-Local Sync

Work items and specs are **synced to target repos** for local visibility:

### On Capture
- Work item created in workspace-hub `pending/` (master)
- Copy synced to each `<target-repo>/.claude/work-queue/pending/`
- Work item `synced_to` field updated with repo list
- Repo-local `state.yaml` updated

### On Process (Route C — Plan Creation)
- Spec created in workspace-hub `specs/modules/<module>/plan.md`
- Spec also copied to `<target-repo>/specs/modules/<module>/plan.md`
- Both copies have `source_work_item: WRK-NNN` and cross-reference each other

### On Archive
- Workspace-hub master item archived to `archive/YYYY-MM/`
- Repo-local copy also moved to `<target-repo>/.claude/work-queue/archive/YYYY-MM/`

### On Status Change
- Any status change (pending → working → blocked → done) updates both master and repo-local copies

### Sync Direction
```
workspace-hub (master) ──sync──> target-repo (mirror)
       ↑                              │
       └──── status/commits ───────────┘
```

Workspace-hub is always the source of truth. If conflicts arise, master wins.

## Integration Points

| System | Integration |
|--------|-------------|
| claude-reflect | Checklist item: queue counts, stale item alerts (>7 days blocked) |
| skill-learner | Post-archive feedback: triage accuracy tracking |
| repo-readiness | Pre-check before processing each work item |
| specs/modules | All routes generate plans; Route C produces full spec files with bidirectional linking |
| aceengineer-website | Completion hook triggers brochure update + portfolio sync |

## Completion Hook — Marketing Brochure

When a work item is archived, the `on-complete-hook.sh` fires automatically:

1. **Reads target repos** from the archived work item
2. **Checks for existing brochures** at `<repo>/docs/marketing/*brochure*.md`
3. **Sets `brochure_status: pending`** on the work item
4. **Outputs recommended tasks**: update module brochure, sync to aceengineer-website

### Brochure Lifecycle

```
Work Item Completed → brochure_status: pending
  ↓
Module brochure updated with new capability → brochure_status: updated
  ↓
aceengineer-website portfolio synced → brochure_status: synced
```

### Brochure Status Values

| Status | Meaning |
|--------|---------|
| *(empty)* | Not yet evaluated |
| `pending` | Completion hook fired, brochure update needed |
| `updated` | Module brochure updated with this capability |
| `synced` | aceengineer-website portfolio reflects this capability |
| `n/a` | No marketing relevance (personal items, etc.) |

### Marketing Brochure Locations

Module brochures live at `<repo>/docs/marketing/` and are read by aceengineer-website to market capabilities. Each engineering module should have a brochure documenting its features, capabilities, and business value.

```
digitalmodel/docs/marketing/dynacard-ai-diagnostics-brochure.md
digitalmodel/docs/marketing/schematics/*.svg
aceengineer-website/docs/marketing/PORTFOLIO_CAPABILITIES.md
```

## Scripts

| Script | Purpose |
|--------|---------|
| `next-id.sh` | Scan queue dirs for max WRK-NNN, return next |
| `queue-status.sh` | Report counts per state |
| `archive-item.sh` | Move to `archive/YYYY-MM/` with metadata, runs completion hook |
| `on-complete-hook.sh` | Post-archive: check brochure status, set pending, recommend tasks |
| `queue-report.sh` | Generate summary for reflect integration |
| `generate-index.py` | Generate `INDEX.md` with multi-view lookup tables |

## Index Management

**INDEX.md is the source of truth for listing.** Never scan individual work item files for a list operation.

### `/work list` Behavior
1. Read `.claude/work-queue/INDEX.md`
2. Display the relevant section (filter by repo/status/priority if args provided)
3. If INDEX.md is missing or empty, regenerate: `python3 .claude/work-queue/scripts/generate-index.py`

### Index Regeneration Triggers
After ANY mutation to work items, regenerate the index:
- `/work add` — after creating the new item file
- `/work archive` — after moving the item to archive/
- Status changes (pending → working, working → done, etc.)
- Priority or complexity changes

Regeneration command:
```
python3 .claude/work-queue/scripts/generate-index.py
```

This is fast (<2s for 100+ items) and ensures INDEX.md stays current.

## Archival Safety (Insights-Validated)

**Never archive or mark a work item as done until the user explicitly confirms completion.** This is the #1 friction point identified across 120 sessions.

- Always present a completion summary listing any remaining gaps before changing status
- Check all acceptance criteria are met — partial completion is NOT done
- Reports, documentation, and secondary deliverables count — don't archive when only code is done
- If uncertain, keep the item in `working/` and ask the user

## Error Handling

### Item Processing Failures
- 3 attempts before marking as failed
- Failed items stay in `working/` with `status: failed`
- Failure reason logged in frontmatter `failure_reason` field

### Blocked Items
- Auto-detect: dirty repo, failing tests, pending PR
- Moved to `blocked/` with `blocked_by` field
- Daily reflect checks for stale blocked items (>7 days)

### State Recovery
- `state.yaml` tracks counters and last processed
- Scripts are idempotent - safe to re-run
- Archive includes full audit trail

## Index Columns

The Master Table in INDEX.md includes these tracking columns:

| Column | Source | Auto-detected? |
|--------|--------|----------------|
| Ensemble?| `plan_ensemble` frontmatter | Yes |
| Plan? | `spec_ref` field or `## Plan` body section | Yes |
| Reviewed? | `plan_reviewed` frontmatter | No — set manually |
| Approved? | `plan_approved` frontmatter | No — set manually |
| % Done | `percent_complete` frontmatter (auto 100% on archive) | Partial |
| Brochure | `brochure_status` frontmatter | Set by completion hook |

## Version History

- **1.4.0** (2026-02-12): Cross-review by phase, testing tiers
  - Route B/C items require per-phase cross-review by Claude, Codex, and Gemini
  - Review log format standardized in spec documents
  - Testing tier integration: `scripts/test/test-{commit,task,session}.sh`
  - `test-task.sh --wrk WRK-NNN` reads target repos from work item
- **1.3.0** (2026-02-09): Plan tracking, brochure lifecycle, completion hook
  - New INDEX.md columns: Plan?, Reviewed?, Approved?, % Done, Brochure
  - Auto-detect plan existence from `spec_ref` or `## Plan` body section
  - Completion hook (`on-complete-hook.sh`) fires on archive, sets `brochure_status: pending`
  - `archive-item.sh` script for full archive workflow with hook integration
  - Plan Tracking summary section in INDEX.md
  - aceengineer-website portfolio sync lifecycle
- **1.2.0** (2026-02-08): Mandatory planning for all routes
  - Plan gate required before implementation on ALL routes (A, B, C) — not just Route C
  - Plan depth scales by complexity: inline bullets (A), inline steps (B), full spec (C)
  - User must explicitly approve plan before implementation begins
  - Descriptive plan naming convention: `wrk-NNN-<short-description>.md` replaces random codenames
  - Existing random-named specs to be renamed incrementally
- **1.1.0** (2026-01-29): Repo-local sync
  - Work items synced to target repo `.claude/work-queue/`
  - Route C specs synced to target repo `specs/modules/`
  - Bidirectional status tracking (master → mirror)
  - `synced_to` frontmatter field added
- **1.0.0** (2026-01-28): Initial release
  - Two-phase capture/process system
  - Complexity routing (A/B/C)
  - Multi-repo coordination
  - Queue state management
  - Reflect integration
