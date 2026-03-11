---
name: work-queue
description: Maintains a queue of work items (features, bugs, tasks) across workspace-hub repositories with two-phase capture and process pipeline
version: 1.8.0
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
tools: [Read, Write, Edit, Bash, Grep, Glob, Task, EnterPlanMode, ExitPlanMode]
related_skills: [claude-reflect, skill-learner, repo-sync, session-start, session-end, workflow-gatepass, wrk-lifecycle-testpack, work-queue-workflow, comprehensive-learning]
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
see_also: [session-start, workflow-gatepass, wrk-lifecycle-testpack, work-queue-workflow]
---

# Work Queue Skill

> Two-phase work queue system: **Capture** rapidly logs items, **Process** triages and delegates
> by complexity. See `work-queue-workflow/SKILL.md` for full lifecycle and stage contracts.

## Quick Start

```bash
scripts/agents/session.sh init --provider claude  # once per session
/work add <description>                           # capture
/work run                                         # process next item
/work list [--by-category] [--category <n>]       # browse queue
/work status WRK-NNN                              # inspect item
```

## Command Interface

| Command | Action |
|---------|--------|
| `/work add <desc>` | Capture — log work items |
| `/work run` | Process — run next stage (auto-loads checkpoint.yaml) |
| `/work list` | Status — read INDEX.md |
| `/work list --by-category` | Category-grouped view (HIGH first) |
| `/work list --category <name> [--subcategory <sub>]` | Narrow by category |
| `/work status WRK-NNN` | Detail for one item |
| `/work archive WRK-NNN` | Manually archive |
| `/work report` | Queue health summary |

Smart routing: action verbs (run/go/start) → Process; descriptive content → Capture.

## Canonical 20-Stage Lifecycle

```
1  Capture              2  Resource Intelligence   3  Triage
4  Plan Draft (4a: Ideation via EnterPlanMode → 4b: Artifact write)
5  User Review Plan Draft  6  Cross-Review
7  User Review Plan Final  8  Claim/Activation     9  Work-Queue Routing
10 Work Execution       11 Artifact Generation     12 TDD / Eval
13 Agent Cross-Review   14 Verify Gate Evidence    15 Future Work Synthesis
16 Resource Intelligence Update  17 User Review Implementation
18 Reclaim              19 Close                   20 Archive
```

Full stage contracts and gate policy: `scripts/work-queue/stages/stage-NN-*.yaml`
Gate evidence verifier: `scripts/work-queue/verify-gate-evidence.py WRK-NNN`

## Stage Contracts (summary)

| Stage | Key exit artifact(s) | Gate |
|-------|----------------------|------|
| 1 | `evidence/user-review-capture.yaml` (`scope_approved: true`) | HARD |
| 2 | `evidence/resource-intelligence.yaml` | — |
| 3 | WRK frontmatter triage fields | — |
| 4a | `EnterPlanMode` + explicit coverage instruction → text draft → `ExitPlanMode` | — |
| 4b | Draft plan spec + self-verification pass + HTML artifact | — |
| 5 | `evidence/user-review-plan-draft.yaml`; HTML opened in browser | **HARD — user must respond** |
| 6 | Multi-provider review outputs (`cross-review-*.md`) | — |
| 7 | `evidence/plan-final-review.yaml` (`confirmed_by` human) | **HARD — R-25** |
| 8 | `claim-evidence.yaml` + `activation.yaml` | HARD — R-26 |
| 9 | Routing log | — |
| 10 | Execution commits; `execute.yaml` | — |
| 11 | Lifecycle HTML | — |
| 12 | `ac-test-matrix.md` (≥3 PASS, 0 FAIL) | — |
| 13 | Cross-review finding closure notes | — |
| 14 | `gate-evidence-summary.{md,json}` (PASS) | — |
| 15 | `future-work.yaml` | — |
| 16 | `resource-intelligence-update.yaml` | — |
| 17 | `evidence/user-review-close.yaml` (`reviewer` human) | **HARD — R-27** |
| 18 | `reclaim.yaml` (if continuity broke) | — |
| 19 | `scripts/work-queue/close-item.sh WRK-NNN <hash>` | — |
| 20 | `scripts/work-queue/archive-item.sh WRK-NNN` | — |

Stage 5 exit (ALL required before Stage 6): HTML opened (`xdg-open`) + pushed; section walk-through done; user explicitly responded; `user-review-plan-draft.yaml` written; plan artifacts updated.
Stage 7 exit (ALL required before Stage 8): HTML opened + pushed; `plan-final-review.yaml` written; `confirmed_by` in allowlist; `claim-item.sh --stage7-check` → PASS.
Stage 17 exit (ALL required before Stage 19): HTML opened + pushed; `user-review-close.yaml` written; `reviewer` in allowlist; `close-item.sh --stage17-check` → PASS.

## Complexity Routing

| Complexity | Criteria | Route |
|------------|----------|-------|
| Simple | Single change, clear files, <50 words, 1 repo | A — light execution |
| Medium | Clear outcome, 1-2 repos, 50-200 words | B — standard execution |
| Complex | Architectural, 3+ repos, >200 words | C — deep + stricter closure |

All routes share stages 1-9 and 13-20. Routes differ in execution depth (10-12).
Route A: single cross-review pass at Stage 6.
Route B/C: multi-provider cross-review (Claude + Codex + Gemini).

See `work-queue-workflow/SKILL.md` §Complexity Routing for full detail.

## Cross-Review (Route B/C)

After each implementation phase:
1. Write `scripts/review/results/wrk-NNN-phase-N-review-input.md`
2. Submit: `scripts/review/cross-review.sh <file> all` (Codex is hard gate)
3. Collect verdicts: APPROVE / MINOR / MAJOR
4. Fix MAJOR findings before next phase; document deferred MINORs

Codex: `scripts/review/submit-to-codex.sh --file <path>`
Gemini: `scripts/review/submit-to-gemini.sh --file <path>`

## Planning Requirement

Every WRK item must have an approved plan before implementation begins.

| Route | Plan location | Depth |
|-------|--------------|-------|
| A | `## Plan` inline | 3-5 bullet points |
| B | `## Plan` inline | Steps + test strategy |
| C | `specs/wrk/WRK-NNN/` | Full spec from template |

Plan naming: `wrk-NNN-<short-description>.md` (kebab-case, 3-5 words, NOT random codenames).

Pre-move-to-working gates (hard — never skip):
- `plan_approved: true` — user explicitly approved
- `plan_reviewed: true` — Codex + Gemini verdict received (Route B/C)
- `spec_ref` non-empty (Route C)
- `computer:`, `plan_workstations:`, `execution_workstations:` all set

## Checkpoint & Resume

`checkpoint.sh WRK-NNN` writes `.claude/work-queue/assets/WRK-NNN/checkpoint.yaml`.

`/work run` auto-loads checkpoint.yaml via `start_stage.py` — no manual `/wrk-resume` needed.
Use `/wrk-resume WRK-NNN` only for diagnostic inspection of checkpoint state.

Checkpoint required fields: `wrk_id`, `stage`, `next_action`, `context_summary`, `updated_at`
(validated non-blocking by `exit_stage.py` after each stage exit).

## Work Item Format

Required frontmatter fields: `id`, `title`, `status` (pending|working|blocked|done), `priority` (high|medium|low), `complexity` (simple|medium|complex), `created_at`, `target_repos`, `computer`, `plan_workstations`, `execution_workstations`, `category`, `subcategory`. Route C also requires `spec_ref`. Body: `## Mission` (one-sentence scope boundary) + `## What / Why / Acceptance Criteria`.

## Workstation Routing

| Keyword / pattern | Machine |
|-------------------|---------|
| `orcaflex`, `ansys`, `aqwa` | `acma-ansys05` |
| `openfoam`, `blender`, `gmsh`, `calculix`, `fenics` | `ace-linux-2` |
| `heavy-compute`, `cfd-hpc`, `fea-hpc` | `gali-linux-compute-1` |
| `worldenergydata`, `workspace-hub`, hub docs/skills | `ace-linux-1` |
| `digitalmodel`, `assetutilities`, `assethold` | `ace-linux-1` |
| Windows-only (`solidworks`, `excel-macro`) | `acma-ws014` |
| Everything else | `ace-linux-1` |

Bulk-assign: `uv run --no-project python scripts/work-queue/assign-workstations.py [--apply]`

### Machine WRK ID Ranges

Each machine owns a non-overlapping numeric range (canonical: `config/work-queue/machine-ranges.yaml`).
`next-id.sh` reads this table and enforces the floor automatically.

| Machine | Floor | Ceiling | Notes |
|---------|-------|---------|-------|
| `ace-linux-1` | 1 | 4999 | Primary; current IDs ~1114 |
| `acma-ansys05` | 5000 | 9999 | Windows / orcaflex |
| `ace-linux-2` | 10000 | 14999 | Reserved |
| `gali-linux-compute-1` | 15000 | 19999 | Reserved |

Re-allocation: bump floor/ceiling when within 50 of ceiling.

## Queue Directory Structure

```
.claude/work-queue/
  pending/        # awaiting processing
  working/        # active (max 1-2)
  blocked/        # awaiting dependencies
  archive/YYYY-MM/
  assets/WRK-NNN/ # evidence, checkpoint, HTML
  state.yaml
```

INDEX.md is source of truth for listing. Regenerate after any mutation:
```bash
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `next-id.sh` | Return next WRK-NNN id |
| `queue-status.sh` | Report counts per state |
| `archive-item.sh WRK-NNN` | Move to archive/, run completion hook |
| `close-item.sh WRK-NNN <hash>` | Close with gate verification |
| `verify-gate-evidence.py WRK-NNN` | Validate all gate evidence |
| `generate-html-review.py WRK-NNN --lifecycle` | Regenerate lifecycle HTML |
| `checkpoint.sh [WRK-NNN]` | Write checkpoint.yaml |
| `start_stage.py WRK-NNN N` | Stage entry (auto-prints resume block) |
| `exit_stage.py WRK-NNN N` | Stage exit validation |

## Parallel Work Policy

- Independent tasks: separate WRKs with separate evidence packages.
- Parallel related tasks: each agent modifies files only in its active WRK scope.
- Out-of-scope side effects from another agent: log, do not revert, continue.

## Archival Safety

Never archive or mark done until user explicitly confirms completion. Check all ACs are met — partial completion is NOT done.

## Integration Points

| System | Integration |
|--------|-------------|
| `resource-intelligence` | Mandatory Stage 2 before planning |
| `workflow-gatepass/SKILL.md` | Full gate policy (R-25/R-26/R-27) |
| `workflow-html/SKILL.md` | Lifecycle HTML generation |
| `comprehensive-learning` | Post-archive feedback, phase 7 |
| `session-start` | Top unblocked item per category at session start |

## Version History

- **1.9.0** (2026-03-10): Stage 4a plan-mode ideation sub-stage + explicit coverage instruction (WRK-1014)
- **1.8.0** (2026-03-08): Pruned to ≤250 lines; checkpoint validation; auto-resume (WRK-1035)
- **1.7.0** (2026-03-07): Stage 7/17 hard blocking gates (WRK-1034)
