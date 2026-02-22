---
name: comprehensive-learning
description: >
  Single fire-and-forget command that runs the full session learning pipeline:
  insights → reflect → knowledge → improve → action-candidates → report.
  Machine-aware. Safe for cron scheduling. Replaces running 4 skills manually.
version: 1.0.0
updated: 2026-02-22
category: workspace-hub
author: workspace-hub
type: skill
invoke: comprehensive-learning
auto_execute: false
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills:
  - workspace-hub/improve
  - workspace-hub/reflect
  - workspace-hub/insights
  - workspace-hub/knowledge
  - workspace-hub/session-end
  - workspace-hub/workstations
capabilities: [session-learning, ecosystem-improvement, candidate-actioning, cron-safe]
tags: [learning, meta, session-exit, cron, multi-machine]
platforms: [all]
wrk_ref: WRK-299
---
# comprehensive-learning — Session Learning Pipeline

Single fire-and-forget skill that runs the complete learning loop in sequence.
Replaces running `/insights`, `/reflect`, `/knowledge`, `/improve` manually.
Machine-aware: lightweight on acma-ansys05; skips duplicate candidate actioning
on ace-linux-2.

## Machine Routing

Determined at runtime from `hostname`:

```bash
MACHINE=$(hostname | tr '[:upper:]' '[:lower:]')
case "$MACHINE" in
  ace-linux-1)   CL_MACHINE_MODE=full ;;
  ace-linux-2)   CL_MACHINE_MODE=skip-candidates ;;
  acma-ansys05)  CL_MACHINE_MODE=lightweight ;;
  *)             CL_MACHINE_MODE=full ;;
esac
export CL_MACHINE_MODE
```

| Mode | Phases run | Notes |
|------|-----------|-------|
| `full` | 1–6 | Complete pipeline |
| `skip-candidates` | 1–4 + 6 | Skip Phase 5 (avoids duplicate WRK items with ace-linux-1) |
| `lightweight` | 1 + 6 | Phase 1 only; isolated machine with minimal hub access |

`cron_variant` in the workstations skill maps 1:1 to `CL_MACHINE_MODE`.

## Pipeline

Run phases sequentially. Record each result (DONE / SKIPPED / FAILED + reason) for
the Phase 6 report. Non-mandatory phases (2, 3, 5) log failure and continue;
fatal failures in Phases 1, 4, or 6 exit 1.

---

### Phase 1 — Insights  *(mandatory)*

Invoke `/insights`. Sources consumed:

- `.claude/state/session-signals/*.jsonl`
- `.claude/state/cc-insights/*.json`
- `.claude/state/sessions/*.json`
- `.claude/state/daily-summaries/*.md`

Extract: skill usage frequency, repeated tool call patterns, task success/failure
signals, user correction events.

---

### Phase 2 — Reflect  *(non-mandatory)*

Invoke `/reflect` (workspace-hub/claude-reflect). Sources:

- `.claude/state/reflect-history/`
- `.claude/state/trends/*.json`
- `git log --all --oneline` across repos

Extract: cross-session patterns, velocity trends, recurring blockers.

---

### Phase 3 — Knowledge  *(non-mandatory)*

Invoke `/knowledge`. Sources: Phase 1 + 2 output + session context.

Extract: new institutional knowledge worth persisting across sessions.

---

### Phase 4 — Improve  *(mandatory)*

Invoke `/improve`. Sources:

- `.claude/state/corrections/*.jsonl`
- `.claude/state/accumulator.json`
- `.claude/state/patterns/`
- `.claude/state/pending-reviews/*.jsonl`
- `.claude/state/learned-patterns.json`
- `.claude/state/skill-scores.yaml`
- `.claude/state/cc-user-insights.yaml`

Extract: skill/memory improvements, correction-driven updates to ecosystem files.

---

### Phase 5 — Action Candidates  *(non-mandatory; skipped if mode ≠ full)*

> Skip entirely if `CL_MACHINE_MODE == skip-candidates` or `lightweight`.

Read each candidate file. For every non-trivial, non-null entry: assess and create
a WRK item. Reset the candidate file to empty template after processing.

**Candidate files:**

| File | Domain | Assessment focus |
|------|--------|-----------------|
| `skill-candidates.md` | Skills | Repeated manual workflows → candidate skill |
| `script-candidates.md` | Scripts | Recurring bash commands → candidate script |
| `hook-candidates.md` | Hooks | Pre/post task patterns → candidate hook |
| `mcp-candidates.md` | MCP tools | Tool-call gaps → candidate MCP integration |
| `agent-candidates.md` | Agents | Complex sub-tasks → candidate agent type |

**Also scan for signal-based candidates:**

- `.claude/state/session-signals/*.jsonl` — high-frequency repetitive tool calls
  suggest a missing script or automation; failed patterns suggest missing validation
  hooks
- `.claude/state/cc-insights/*.json` (tool_usage sections) — surface unreached
  or underused capabilities that might warrant a dedicated skill
- Tool call sequences that repeat across sessions (Read→Edit→Bash cycles)
  suggest a scriptable workflow

**Skip a candidate if:**
- Name field is empty or null (invalid session-analysis.sh output)
- Description is a generic placeholder only (no actionable signal)
- Occurrence count ≤ 2 (too infrequent to warrant a WRK item)

**WRK auto-creation pattern:**

```bash
NEXT_ID=$(bash scripts/work-queue/next-id.sh)
WRK_FILE=".claude/work-queue/pending/WRK-${NEXT_ID}.md"
# Write frontmatter + title + description to WRK_FILE
# state.yaml last_id is updated by next-id.sh auto-correction on next call
```

**Sanitization required:** Before writing any candidate-derived content into WRK
frontmatter or body, sanitize to prevent YAML/Markdown corruption:
- Escape or strip `---` sequences that would terminate YAML frontmatter
- Truncate title to 80 chars; replace newlines with space
- Quote YAML scalar values that contain `:` or `#`
- Strip markdown control characters from free-text fields

WRK item template for candidate actioning:

```markdown
---
id: WRK-NNN
title: "[domain]: <candidate name> — auto-actioned from candidates"
status: pending
priority: low
source: comprehensive-learning/phase-5
computer: <MACHINE>   # set to runtime hostname (ace-linux-1, ace-linux-2, etc.)
---
## Context
Auto-created from `.claude/state/candidates/<type>-candidates.md`.
Occurrence count: N | Sessions: ...

## Description
<candidate description>

## Acceptance Criteria
- [ ] Candidate assessed and implemented (or closed as not worth building)
```

**Candidate file reset template** (written after processing each file):

```markdown
# <Type> Candidates
*Updated by session-analysis.sh — do not edit manually*
*Last run: <ISO8601 timestamp of this run>*

## Candidates

<!-- Populated automatically by morning cron -->
```

---

### Phase 6 — Report  *(always runs — use `trap EXIT` to guarantee execution)*

Register Phase 6 as a `trap EXIT` handler at pipeline start so it runs even if a
mandatory phase exits 1. The exit code is set *after* the report is written.

Write `.claude/state/learning-reports/$(date +%Y-%m-%d-%H%M).md`:

```markdown
# Learning Report — <timestamp>

| Phase | Status | Notes |
|-------|--------|-------|
| 1 Insights | DONE / SKIPPED / FAILED | <brief> |
| 2 Reflect  | ... | ... |
| 3 Knowledge | ... | ... |
| 4 Improve  | ... | ... |
| 5 Candidates | DONE (N WRK items created) / SKIPPED | ... |
| 6 Report | DONE | <elapsed>s total |

Machine: <hostname> | Mode: <CL_MACHINE_MODE>
```

**Exit codes:** 0 = all mandatory phases pass; 1 = fatal failure in mandatory phase.

## Scheduling

Safe for cron — no interactive prompts, no blocking checklist.

```bash
# ace-linux-1: nightly 22:00 (full pipeline)
0 22 * * * cd /mnt/local-analysis/workspace-hub && \
  claude --skill comprehensive-learning >> .claude/state/learning-reports/cron.log 2>&1

# acma-ansys05: nightly 23:00 (lightweight — Phase 1 only)
0 23 * * * cd /path/to/workspace && \
  claude --skill comprehensive-learning >> cron.log 2>&1
```

The `learning-reports/` directory is at `.claude/state/learning-reports/`. Create it
with `mkdir -p` on first run if absent.

## Integration with post-task-review.sh

The post-task hook shows a single non-blocking line instead of the old checklist:

```
→ Run /comprehensive-learning post-session to process learnings.
```

Counts (insights, skill candidates, memory updates) are still displayed above it.
See `.claude/hooks/post-task-review.sh`.

## Related

- workstations skill: `cron_variant` field maps to `CL_MACHINE_MODE`
- WRK-299: implementation tracking
- `/insights`, `/reflect`, `/knowledge`, `/improve`: individual pipeline stages
