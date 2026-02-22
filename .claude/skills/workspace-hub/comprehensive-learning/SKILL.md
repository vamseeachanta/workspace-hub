---
name: comprehensive-learning
description: >
  Single fire-and-forget command that runs the full session learning pipeline:
  insights → reflect → knowledge → improve → action-candidates → report.
  Runs on ace-linux-1 only. Other machines contribute via git-synced state files.
  Safe for cron scheduling. Replaces running 4 skills manually.
version: 2.0.0
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
capabilities: [session-learning, ecosystem-improvement, candidate-actioning, cron-safe,
               continual-learning, cross-machine-analysis]
tags: [learning, meta, session-exit, cron, continual-learning]
platforms: [linux]
wrk_ref: WRK-299
---
# comprehensive-learning — Session Learning Pipeline

Single fire-and-forget skill running the complete learning loop on **ace-linux-1 only**.
Other machines (ace-linux-2, acma-ansys05) contribute data by committing derived state
files to git; ace-linux-1 reads them all during its nightly run.

## Single-Machine Guard

```bash
MACHINE=$(hostname | tr '[:upper:]' '[:lower:]')
if [[ "$MACHINE" != "ace-linux-1" ]]; then
  echo "comprehensive-learning runs on ace-linux-1 only."
  echo "From this machine, commit state files and push:"
  echo "  git add .claude/state/candidates/ .claude/state/corrections/"
  echo "  git add .claude/state/patterns/ .claude/state/session-signals/"
  echo "  git commit -m 'chore: session learnings from $(hostname)'"
  exit 0
fi
```

## Cross-Machine Data Flow

Other machines contribute by committing these gitignored-exceptions after sessions:

| Machine | Commits | Notes |
|---------|---------|-------|
| ace-linux-2 | `candidates/`, `corrections/`, `patterns/`, `session-signals/` | Open-source CFD/dev sessions |
| acma-ansys05 | `candidates/`, `corrections/` | OrcaFlex/ANSYS sessions; minimal hub access |
| acma-ws014 | `candidates/` | Windows sessions |

ace-linux-1 `git pull` before running pipeline picks up all contributions.

## Pipeline

Run phases sequentially. Record each result (DONE / SKIPPED / FAILED + reason) for
the Phase 10 report. Non-mandatory phases log failure and continue; fatal failures
in Phases 1, 4, or 10 exit 1. Register Phase 10 as `trap EXIT` at pipeline start.

---

### Phase 1 — Insights  *(mandatory)*

Invoke `/insights`. Sources:

- `.claude/state/session-signals/*.jsonl`
- `.claude/state/cc-insights/*.json`
- `.claude/state/sessions/*.json`
- `.claude/state/daily-summaries/*.md`

Extract: skill usage frequency, repeated tool call patterns, task success/failure
signals, user correction events.

---

### Phase 2 — Reflect  *(non-mandatory)*

Invoke `/reflect`. Sources:

- `.claude/state/reflect-history/`
- `.claude/state/trends/*.json`
- `git log --all --oneline` across repos

Extract: cross-session patterns, velocity trends, recurring blockers.

**Re-derivation check:** If any script in `scripts/analysis/` or `scripts/learning/`
is newer than derived files in `.claude/state/patterns/` or `.claude/state/corrections/`,
flag for manual re-derivation on the originating machine.

---

### Phase 3 — Knowledge  *(non-mandatory)*

Invoke `/knowledge`. Sources: Phase 1 + 2 output + session context.

Extract: new institutional knowledge worth persisting across sessions.

**Memory staleness check:** For key claims in `.claude/memory/MEMORY.md` and topic
files, spot-check 3–5 entries against current codebase reality (file paths, commands,
test invocations). Flag stale entries for correction. Mark checked entries with
`*verified: <date>*` or `*stale: <date>*`.

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

### Phase 5 — Correction Trend Analysis  *(non-mandatory)*

Read `corrections/*.jsonl` for the **rolling 90-day window** (use `--since` or filter
by file date). Group by `type` and `tool` fields. For each group compute:
- Occurrence count this week vs last week vs 4-week average
- Top 3 most frequent correction types (by count)
- Any type with count **increasing** week-over-week for 2+ consecutive weeks → flag
  as structural issue, create WRK item: `"fix: recurring <type> correction pattern"`

**Bounding:** Only process files modified in the last 90 days. Run a full compaction
(all-dates scan) at most once per quarter — log the last compaction date in
`.claude/state/correction-trend-meta.json`.

This closes the feedback loop on Phase 4 — verifying improvements are actually sticking.

---

### Phase 6 — WRK Feedback Loop  *(non-mandatory)*

Scan `work-queue/archive/` for WRK items where `source: comprehensive-learning/phase-7`
(auto-created candidates). For each:
- **Actioned** (status: done): record as positive signal for that candidate type
- **Stale** (>30 days in pending with no activity): downgrade its candidate type's
  score in `skill-scores.yaml`; log to learning report
- **Never created pattern**: if occurrence count kept rising without a WRK item,
  candidate threshold (currently ≤2) may be too high

Output: candidate effectiveness score per type. Adjust Phase 7 thresholds accordingly.

---

### Phase 7 — Action Candidates  *(non-mandatory)*

Read each candidate file. For every non-trivial, non-null entry: assess and create
a WRK item. Reset candidate file after processing.

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
  suggest a missing script; failed patterns suggest missing validation hooks
- `.claude/state/cc-insights/*.json` (tool_usage) — surface unreached capabilities
- Tool call sequences repeating across sessions (Read→Edit→Bash) → scriptable workflow
- Contributions from other machines (committed by ace-linux-2, acma-ansys05, etc.)

**Code quality signal scan (test · lint · architecture · refactor):**

| Signal | Source | Candidate action |
|--------|--------|-----------------|
| Same file edited ≥3× this week, no test file touched | `corrections/*.jsonl` `tool: Edit` | WRK: "add tests for `<file>`" |
| `type: lint` correction recurring ≥2 weeks | `corrections/*.jsonl` | WRK: "add pre-commit lint hook / fix config for `<type>`" |
| Architectural violation recurring (circular import, God object, hardcoded literal) | `corrections/*.jsonl` | WRK: "add guardrail hook for `<pattern>`" |
| Read→Edit→Bash(fail)→Edit loop on same function across sessions | `sessions-archive/` (if available) or `session-signals/` | WRK: "refactor `<fn>` — brittle, repeated rework" |
| No test file exists for a module touched in ≥2 sessions this week | `session-signals/` + `glob tests/` | WRK: "add unit tests for `<module>`" |

Back-analysis path: if `sessions-archive/` is populated (see **Session Archive** below),
scan raw session JSONL for the patterns above across all machines and all historical
dates — not just the rolling window used for derived files. Future agent improvements
will make this richer over time.

**Skip a candidate if:**
- Name field is empty or null
- Description is a generic placeholder only
- Occurrence count ≤ 2 (adjust threshold based on Phase 6 feedback)

**Sanitization required:** Before writing candidate-derived content into WRK YAML/MD:
- Strip `---` sequences that would terminate YAML frontmatter
- Truncate title to 80 chars; replace newlines with space
- Quote YAML scalars containing `:`, `#`, `"`, `'`, or `|`
- Strip markdown control characters from free-text fields
- Reject multiline values in scalar YAML fields (replace `\n` with space)
- Validate the complete frontmatter block via
  `python3 -c 'import yaml,sys; yaml.safe_load(sys.stdin)'` before writing;
  discard and log if parse fails

**WRK auto-creation pattern (concurrency-safe):**

```bash
# Use flock to prevent duplicate IDs from parallel or manual runs
(
  flock -x 200
  NEXT_ID=$(bash scripts/work-queue/next-id.sh)
  WRK_FILE=".claude/work-queue/pending/WRK-${NEXT_ID}.md"
  # Write frontmatter + title + description to WRK_FILE
  # Update state.yaml last_id inside the lock
) 200>/tmp/workspace-hub-next-id.lock
```

WRK item template:

```markdown
---
id: WRK-NNN
title: "[domain]: <candidate name> — auto-actioned from candidates"
status: pending
priority: low
source: comprehensive-learning/phase-7
computer: <MACHINE>
---
## Context
Auto-created from `.claude/state/candidates/<type>-candidates.md`.
Occurrence count: N | Sessions: ...

## Description
<candidate description>

## Acceptance Criteria
- [ ] Candidate assessed and implemented (or closed as not worth building)
```

Candidate file reset template:

```markdown
# <Type> Candidates
*Updated by session-analysis.sh — do not edit manually*
*Last run: <ISO8601 timestamp>*

## Candidates

<!-- Populated automatically by morning cron -->
```

---

### Phase 8 — Learning Report Review  *(non-mandatory)*

Read the last 4 learning reports from `.claude/state/learning-reports/`.
For each phase, compare what was flagged vs what was flagged last run:

- If the same correction type appears in Phase 5 of 3+ consecutive reports →
  escalate: create a P1 WRK item (`"fix: <type> corrections not responding to improve"`)
- If Phase 6 consistently shows stale auto-created WRK items → reduce candidate
  actioning aggressiveness (raise occurrence threshold)
- If Phase 3 memory staleness flags the same entry 2+ times → that entry is
  structurally wrong; create WRK to fix it

Prevents the pipeline from surfacing the same issues indefinitely without resolution.

---

### Phase 9 — Skill Coverage Audit  *(non-mandatory; run weekly, not nightly)*

Cross-reference:
1. All tasks completed this week (from `work-queue/archive/` WRK items)
2. Available skills in `.claude/skills/`
3. Tool call sequences in `session-signals/`

Identify workflows performed manually (multi-step tool sequences) that:
- Have no corresponding skill
- Occurred ≥3 times this week
- Each instance took >5 tool calls to complete

Create candidate skill entries for the top 3 gaps. This is the proactive skill
coverage check — catches automation opportunities that candidate files miss because
they rely on the user triggering the pattern, not the pipeline discovering it.

Run trigger: only if `$(date +%u)` == 7 (Sunday) or explicit invocation.

---

### Phase 10 — Report  *(always runs — registered via `trap EXIT`)*

**Exit-code semantics:** At pipeline start, register the trap and capture the
original exit status:
```bash
_PIPELINE_EXIT=0
trap 'REPORT_STATUS=$?; _write_report; exit ${_PIPELINE_EXIT:-$REPORT_STATUS}' EXIT
```
Mandatory-phase failures set `_PIPELINE_EXIT=1` before exiting; the trap reads
`_PIPELINE_EXIT` first so report-write errors never mask upstream failures.
The report write itself must not call `exit` — write best-effort, then return.

Write `.claude/state/learning-reports/$(date +%Y-%m-%d-%H%M).md`:

```markdown
# Learning Report — <timestamp>

| Phase | Status | Notes |
|-------|--------|-------|
| 1 Insights | DONE/SKIPPED/FAILED | <brief> |
| 2 Reflect | ... | re-derivation needed: yes/no |
| 3 Knowledge | ... | stale memory entries: N |
| 4 Improve | ... | ... |
| 5 Correction Trends | ... | escalated types: N |
| 6 WRK Feedback | ... | stale auto-WRK: N, threshold adj: yes/no |
| 7 Candidates | ... | WRK items created: N (incl. code-quality: N) |
| 8 Report Review | ... | escalated recurring issues: N |
| 9 Coverage Audit | ... | SKIPPED (not Sunday) / gaps found: N |
| 10 Report | DONE | <elapsed>s total |

Machine: ace-linux-1 | Sources: ace-linux-1 + <N other machines via git>
```

**Exit codes:** 0 = all mandatory phases pass; 1 = fatal failure in mandatory phase.

## Scheduling

```bash
# ace-linux-1 only: nightly 22:00
# Step 1: pull derived state files from all machines (git)
# Step 2: pull raw session archives from reachable machines (rsync, best-effort)
# Step 3: run pipeline
0 22 * * * cd /mnt/local-analysis/workspace-hub && \
  git pull --no-rebase origin main && \
  rsync -az --no-delete ace-linux-2:.claude/state/sessions/ \
    .claude/state/sessions-archive/ace-linux-2/ 2>/dev/null || true && \
  rsync -az --no-delete ACMA-ANSYS05:.claude/state/sessions/ \
    .claude/state/sessions-archive/acma-ansys05/ 2>/dev/null || true && \
  claude --skill comprehensive-learning >> \
  .claude/state/learning-reports/cron.log 2>&1
```

The `git pull` picks up derived state; `rsync` pulls raw sessions for back-analysis.
Machines that are offline are skipped silently (`|| true`). SSH key auth required
between ace-linux-1 and contributing machines (`ssh-copy-id ace-linux-1` from each).

## Other Machines — End-of-Session Commit

On ace-linux-2, acma-ansys05, acma-ws014 — run at session end:

```bash
cd /path/to/workspace-hub

# 1. Commit derived state to git (fast, lightweight)
git add .claude/state/candidates/ .claude/state/corrections/ \
        .claude/state/patterns/ .claude/state/session-signals/
git diff --staged --quiet || \
  git commit -m "chore: session learnings from $(hostname)"
# Pull with rebase first to avoid push rejection; retry once on transient fail
git pull --rebase origin main && git push origin main || {
  sleep 5
  git pull --rebase origin main && git push origin main
}

# 2. Raw sessions are pulled by ace-linux-1 nightly via rsync (no action needed here)
#    ace-linux-1 rsync: ace-linux-2:.claude/state/sessions/ → sessions-archive/ace-linux-2/
```

**On push conflict:** If `git pull --rebase` produces a conflict in a state file,
prefer the incoming version (`git checkout --theirs <file> && git add <file>`)
since ace-linux-1 is the authoritative analysis machine. Then `git rebase --continue`.

This is what acma-ansys05 contributes instead of running the full pipeline locally.

## Integration with post-task-review.sh

```
→ Run /comprehensive-learning post-session to process learnings.
```

## Session Archive (ace-linux-1 local — not git)

Raw session transcripts are centralised on ace-linux-1 via rsync. They are never
committed to git — too large and binary-noisy. The 7.3 TB HDD on ace-linux-1 is
the long-term store.

```
.claude/state/sessions-archive/
  ace-linux-1/      # local sessions (symlink or copy of .claude/state/sessions/)
  ace-linux-2/      # rsync'd nightly by ace-linux-1 cron
  acma-ansys05/     # rsync'd when reachable
  acma-ws014/       # rsync'd when reachable
```

**Why keep raw sessions:** As agent capabilities improve, re-running analysis on
full decision traces (tool-call sequences, abandoned paths, correction events)
surfaces signals that derived files lose. Back-analysis on the archive unlocks this
retroactively — data collected today becomes more valuable over time.

**Setup (once per contributing machine):**
```bash
# On ace-linux-2 / acma-ansys05: grant ace-linux-1 SSH read access
ssh-copy-id ace-linux-1   # or add ace-linux-1's public key to authorized_keys
```

**Retention:** no automated purge policy — ace-linux-1 HDD capacity governs.
Review annually; oldest sessions can be compressed (`gzip *.jsonl`) if space tightens.

## State Files Committed to Git

Gitignore exceptions in `.gitignore` (all under `.claude/state/`):

| Path | Size | Why |
|------|------|-----|
| `candidates/` | ~26 KB | Feeds Phase 7; all machines contribute |
| `corrections/` | ~3.4 MB | Feeds Phases 4+5; correction trend analysis |
| `patterns/` | ~3.5 MB | Feeds Phases 2+4; already distilled |
| `reflect-history/` | ~1.2 MB | Feeds Phase 2; avoids re-analysis |
| `trends/` | ~136 KB | Feeds Phase 2 |
| `session-signals/` | ~126 KB | Feeds Phases 1+7 |
| `cc-insights/` | ~27 KB | Feeds Phase 7 |
| `learned-patterns.json` | ~16 KB | Feeds Phase 4 |
| `skill-scores.yaml` | ~8 KB | Feeds Phases 4+6 |
| `cc-user-insights.yaml` | ~4 KB | Feeds Phase 4 |

Not committed: `sessions/` (13 MB), `archive/` (29 MB), `session-reports/` (5.2 MB),
`sessions-archive/` (grows unbounded) — raw data stays local on ace-linux-1 HDD.

## Related

- workstations skill: machine registry and `cron_variant` fields
- WRK-299: implementation tracking
- `/insights`, `/reflect`, `/knowledge`, `/improve`: individual pipeline stages
