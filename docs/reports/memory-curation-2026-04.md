# MEMORY.md Curation — 2026-04

> Generated for #2324. Auto-memory target: `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/` on dev-secondary (NOT git-tracked — this report is the durable cross-machine record).

## Summary

| Metric | Before | After |
|---|---|---|
| MEMORY.md lines | 46 | 48 |
| Files on disk (`*.md`, excl MEMORY.md) | 53 | 52 (1 archived to `_archive/`) |
| Files referenced via proper index entries | 39 | 41 |
| Files referenced via group-header shorthand only | 5 | 5 |
| True orphans (not referenced via any mechanism) | 3 | 0 |
| Missing (index entry referring to non-existent file) | 0 | 0 |
| Archived (moved to `_archive/`) | n/a | 1 |

Line budget: current 48/200 cap — no truncation pressure. Curation motivated by staleness + orphan cleanup, not line budget.

## Per-entry dispositions

### Promoted from orphan → proper index entry

| File | Action | Reason |
|---|---|---|
| `data_format_guidelines.md` | **ADDED** to Feedback section | Present on disk, not referenced in MEMORY.md. Content: when to use YAML vs JSON vs Markdown for agent-readable data. Still load-bearing (default-YAML rule actively applied across the repo). |
| `feedback_cross_machine_execution.md` | **ADDED** to Feedback section | Present on disk, not referenced in MEMORY.md. Content: cross-machine tasks must spawn independent per-machine tasks, not use SSH/rsync. Still load-bearing (applies to every multi-machine workflow). |

### Archived

| File | Action | Reason |
|---|---|---|
| `project_auto_sync_risk.md` | **ARCHIVED** to `_archive/` (plain `mv`; dir is not git-tracked) | File itself marked RESOLVED 2026-03-25 post-GSD migration. Residual caution is already encoded in current workflow. No remaining consumer references it. |

### Group-header shorthand references (left as-is)

These files are on disk AND referenced via `> feedback_*:` / `> project_...` group-header lines at the top of each section. Left as shorthand — promoting each to a proper entry would add ~5 lines for minor additional discoverability. If any becomes frequently consulted, promote individually.

- `feedback_no_jargon.md`
- `feedback_repo_scope.md`
- `feedback_research_skill_sources.md`
- `feedback_specs_plans_location.md`
- `feedback_uv_run_isolation.md`

### Entries kept as-is (verification)

All 39 pre-curation proper index entries verified against their linked files: every link resolves (0 missing). Three GH issue cross-checks spot-checked:
- #1977 (memory ecosystem follow-ups) — OPEN; entry remains accurate.
- #2076 (field-dev econ follow-up) — OPEN; entry remains accurate.
- #2327 (CAD tooling review) — OPEN; entry remains accurate.

Exhaustive issue-status cross-check across every referenced issue is NOT performed in this pass — out of scope for a T1 editorial curation. Future work if the cost proves worthwhile.

## Execution-time revisions (from the plan)

Plan-v1 contradictions resolved before execution, per `.planning/plan-approved/2324.md`:

1. **Memory dir is NOT git-tracked** (verified via `git rev-parse` returning "not a git repository"). Plan's `git mv` references replaced with plain `mv`. No CI-checkable AC for paths outside the repo.
2. **"Cross-machine sync" is a false premise.** Plan conflated two memory systems; the project-local auto-memory is single-machine. No sync coordination.
3. **Line-budget urgency is vestigial.** Current 48/200 lines — curation value is staleness detection, not space pressure.
4. **Report is the durable record.** Since target dir is not git-tracked, this file in the workspace-hub repo is the only artifact that propagates cross-machine.

## What's next

- If other machines (ace-linux-1, licensed-win-1) have their own auto-memory dirs, run a similar curation there separately. Each machine's MEMORY.md is independent.
- Related: #1977 (memory ecosystem — backup/rollback), #2231 (memory regression coverage).
