---
name: comprehensive-learning
description: >
  Single fire-and-forget command that runs the full session learning pipeline:
  insights → reflect → knowledge → improve → action-candidates → report.
  Runs on ace-linux-1 only. Other machines contribute via git-synced state files.
  Safe for cron scheduling. Replaces running 4 skills manually.
version: 2.1.0
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
MACHINE=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')
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
in Phases 1 or 4 set `_PIPELINE_EXIT=1`. Phase 10 always runs and is itself
non-fatal (report-write failures log a warning only). Register Phase 10 as
`trap EXIT` at pipeline start.

---

### Phase 1 — Insights  *(mandatory)*

Invoke `/insights`. Sources:

- `.claude/state/session-signals/*.jsonl`
- `.claude/state/cc-insights/*.json`
- `.claude/state/sessions/*.json`
- `.claude/state/daily-summaries/*.md`

Extract: skill usage frequency, repeated tool call patterns, task success/failure
signals, user correction events, **engineering audit signals** (wall_thickness, 
fatigue, etc.), and **data provenance signals**.

**Additional session-quality signals (flag in Phase 1 report):**

| Signal | Check | Action if triggered |
|--------|-------|---------------------|
| Context reset discipline | Sessions with ≥3 unrelated WRK tasks but no `/clear` event in signals | Flag: "context pollution risk — multiple tasks without reset" |
| Plan mode skipped | Multi-file edit session (≥3 files, ≥1 WRK) with no plan-mode invocation recorded | Flag: "plan mode not used before implementation" |
| Agent loop / stuck pattern | Session where same tool+file pair appears ≥5× consecutively without progress | Flag: "possible agent loop — consider ultrathink or task decomposition" |
| Task decomposition quality | WRK item with >15 tool calls before first commit | Flag: "WRK scope too large — split or add stopping conditions" |
| Ensemble gate skipped | Route B/C WRK processed without `plan_ensemble: true` in frontmatter | Flag: "ensemble gate bypassed — plan confidence unknown" |
| Low consensus score | `ensemble_consensus_score` < 70 on a completed WRK item | Flag: "low-confidence plan executed — review for rework risk" |
| SPLIT not resolved | `synthesis.md` contains `[SPLIT:` lines but item proceeded to implementation | Flag: "unresolved SPLIT proceeded — log decision and outcome" |
| Provider NO_OUTPUT rate | ≥3 consecutive ensemble runs where same provider emits NO_OUTPUT | Flag: "provider degraded — check CLI version / auth for <provider>" |

These signals require session-signals emitters to log: `/clear` invocations, plan-mode
start/end events, and per-WRK tool-call counts. If signals are absent, skip the check
and log "signal not available — emitter not configured".

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

**Escalation WRK items must include diagnosis** (not just counts):
- Which specific tool/file combinations triggered most corrections this week?
- Top 3 error patterns (e.g., "missing null check", "wrong import path", "YAML parse error")
- 2–3 recent JSONL correction entries as concrete examples
- Suggested root cause: memory/skill mismatch vs codebase drift vs prompt pattern issue

Without diagnosis, escalations are noise. If diagnosis cannot be extracted, log to
report only — do not create a WRK item.

**Bounding:** Only process files modified in the last 90 days. Run a full compaction
(all-dates scan) at most once per quarter — log the last compaction date in
`.claude/state/correction-trend-meta.json`.

This closes the feedback loop on Phase 4 — verifying improvements are actually sticking.

---

### Phase 6 — WRK Feedback Loop  *(non-mandatory)*

Scan `.claude/work-queue/archive/` for WRK items where `source: comprehensive-learning/phase-7`
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
| `planning-candidates.md` | Planning | Ensemble quality signals → prompt/stance improvements |

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
  discard and log if parse fails. Dependency check: if `python3 -c "import yaml"`
  fails (PyYAML not installed), log "WARNING: yaml validation skipped — install
  python3-yaml" and continue without validation rather than blocking the pipeline.

**Cron preflight (ace-linux-1):** Before the first cron run, verify the dependency:
```bash
python3 -c "import yaml" || { echo "ERROR: install python3-yaml before scheduling cron"; exit 1; }
```
Add this check to `scripts/cron/comprehensive-learning-nightly.sh` as a preflight
guard so cron failures are explicit rather than silently producing malformed WRK files.

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
1. All tasks completed this week (from `.claude/work-queue/archive/` WRK items)
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

**Exit-code semantics:** Phase 10 is "always runs" but **not fatal** — a report-write
failure logs a warning and returns; it does not change the pipeline exit code.
At pipeline start, register the trap:
```bash
_PIPELINE_EXIT=0
trap '_write_report; exit $_PIPELINE_EXIT' EXIT
```
Rules:
- Every **mandatory** phase failure MUST `_PIPELINE_EXIT=1` **before** calling `exit`
  (or `return 1` to the caller which then sets it). No path should reach `exit` with
  `_PIPELINE_EXIT` still 0 after a mandatory failure.
- Non-mandatory phase failures: log FAILED + reason, do NOT touch `_PIPELINE_EXIT`.
- `_write_report` is always best-effort: write what we have, never calls `exit`.
- `exit $_PIPELINE_EXIT` preserves the mandatory-failure status deterministically;
  no `:-$REPORT_STATUS` fallback to avoid masking unexpected script failures.

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

Use a wrapper script so each step is a hard gate or explicit best-effort:

```bash
# scripts/cron/comprehensive-learning-nightly.sh
#!/usr/bin/env bash
set -euo pipefail
cd /mnt/local-analysis/workspace-hub

# Step 1: pull derived state — hard gate (pipeline must not run on stale state)
git pull --no-rebase origin main

# Step 2: rsync raw sessions — best-effort, each independently
rsync -az --no-delete --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ace-linux-2:.claude/state/sessions/ \
  .claude/state/sessions-archive/ace-linux-2/ 2>/dev/null || true

rsync -az --no-delete --timeout=30 \
  -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" \
  ACMA-ANSYS05:.claude/state/sessions/ \
  .claude/state/sessions-archive/acma-ansys05/ 2>/dev/null || true

# Step 3: run pipeline
exec claude --skill comprehensive-learning
```

Crontab entry (ace-linux-1):
```bash
0 22 * * * cd /mnt/local-analysis/workspace-hub && bash scripts/cron/comprehensive-learning-nightly.sh \
  >> /mnt/local-analysis/workspace-hub/.claude/state/learning-reports/cron.log 2>&1
```

`git pull` is a hard gate — if it fails, `set -euo pipefail` aborts before the
pipeline runs, preventing analysis on stale state. Each `rsync` is independently
`|| true` so one offline machine cannot block the others or the pipeline.
SSH key auth required (see **Session Archive** setup below).

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
prefer the incoming version from origin/main (`git checkout --ours <file> && git add <file>`)
since ace-linux-1 is the authoritative analysis machine. Note: in `git rebase` context,
`--ours` = the base branch (origin/main) and `--theirs` = your replayed local commits —
the opposite of merge semantics. Then `git rebase --continue`.

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

**Setup (once, on ace-linux-1):**

For ace-linux-1 to `rsync` FROM contributor machines, ace-linux-1's SSH public key
must be authorised on each contributor:

```bash
# Run on ace-linux-1 — push its public key to each contributor host
ssh-copy-id <user>@ace-linux-2      # authorize ace-linux-1 on ace-linux-2
ssh-copy-id <user>@ACMA-ANSYS05     # authorize ace-linux-1 on acma-ansys05
# Test: ssh ace-linux-2 "ls ~/.claude/state/sessions/" should succeed without password
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

## Session Design: Lean by Default

Sessions are pure **multi-agent execution engines** — all brain directed at the task at hand.
Analysis, maintenance, and learning are deferred to the nightly `comprehensive-learning` run.

### What belongs in a session

| In-session | Nightly pipeline |
|------------|-----------------|
| WRK gate check (gate approval, active-wrk set) | All insight/reflect/knowledge/improve runs |
| Multi-agent implementation work | Correction trend analysis |
| Fast signal capture (hooks write raw signals) | Candidate file → WRK auto-creation |
| /session-start context load | Memory and skill file updates |
| Cross-review (Codex gate) | Ecosystem health checks |
| Commit + push | Session archive rsync |

### What must NOT run standalone during sessions

- `/insights` — deferred to Phase 1 nightly
- `/reflect` — deferred to Phase 2 nightly
- `/knowledge` — deferred to Phase 3 nightly
- `/improve` — deferred to Phase 4 nightly
- `consume-signals.sh` heavy analysis — deferred to Phase 1 nightly
- `ecosystem-health-check.sh` — deferred to Phase 6 nightly
- `session-end-evaluate.sh` scoring — deferred to Phase 10 nightly

### Stop hooks: one hook only

Stop-time must complete in < 1 second. One hook, raw write only:

| Hook | Action | Allowed |
|------|--------|---------|
| `consume-signals.sh` (simplified, < 30 lines) | Append one JSONL entry to `session-signals/` | **Yes — only hook** |
| `session-signals.sh` | Superseded — removed | No |
| `engineering-audit.sh` | Superseded — removed | No |
| `data-provenance.sh` | Superseded — removed | No |
| `session-end-evaluate.sh` | Deferred to Phase 10 nightly | No |
| `ecosystem-health-check.sh` | Deferred to Phase 6 nightly | No |
| `improve.sh` | Deferred to Phase 4 nightly | No |
| Everything else | Deferred to nightly cron | No |

See WRK-304 for the settings.json + consume-signals.sh cleanup task.

## Planning Quality Loop

Planning is the highest-leverage phase of the work cycle — a bad plan compounds into
bad implementation, rework, and late corrections. The ensemble planning system (WRK-303)
produces structured signals in `scripts/planning/results/*/synthesis.md` that the
nightly pipeline should harvest and act on.

### Signals to harvest (nightly, from synthesis.md files)

```
scripts/planning/results/*/synthesis.md
```

For each synthesis file newer than last pipeline run, extract:

| Signal | Source field | Pipeline action |
|--------|-------------|----------------|
| `CONSENSUS_SCORE` | `CONSENSUS_SCORE: N` line | Record per WRK; alert if avg drops below 65 over rolling 7 days |
| SPLIT decisions | Lines matching `^\[SPLIT:` | Count per WRK; high SPLIT frequency → `planning-candidates.md` entry |
| SPLIT topic categories | First word of each SPLIT decision text | Group by category; recurring categories → stance prompt improvement candidate |
| Provider NO_OUTPUT | Files where content starts with `NO_OUTPUT:` | Count per provider per week; ≥3 consecutive → flag in Phase 1 |
| Stance contribution | Agent file that introduced most SOLO insights | Track which stances catch issues others miss; low-value stances → prompt redesign candidate |
| Plan→implementation drift | Compare WRK `## Plan` with correction events in same session | High drift → "plan was incomplete" signal; feed to planning prompt improvements |

### planning-candidates.md entries

Write to `.claude/state/candidates/planning-candidates.md`. Each entry should be:

```markdown
## Candidate: <type>
- Occurrence: N times in last 7 days
- Description: <what pattern was observed>
- Signal source: synthesis.md / corrections.jsonl / session-signals
- Suggested action: improve prompt / adjust stance / add new stance / change threshold
```

**Candidate types to watch for:**

| Type | Trigger | Action |
|------|---------|--------|
| `stance-ineffective` | One stance contributes 0 SOLO insights across 5+ items | Redesign that stance's prompt focus |
| `prompt-scope-creep` | Agents consistently raise out-of-scope concerns | Tighten stance prompts with explicit scope anchors |
| `split-category-recurring` | Same decision category SPLITS ≥3 times in a week | Add a dedicated 4th stance for that category (e.g., `claude-data-model`) |
| `consensus-score-declining` | Rolling 7-day average drops >10 points | Review recent WRK items for scope inflation or ambiguous requests |
| `provider-timeout-pattern` | Same provider times out on >20% of items | Investigate CLI version / prompt size; consider reducing context passed to that provider |
| `plan-drift-high` | >3 corrections during implementation not covered by the plan | Audit synthesis prompt — merged plan may be too abstract |

### Feeding learnings back to the ensemble system

When a `planning-candidate` WRK item is actioned:

1. **Prompt files** in `scripts/planning/prompts/` are updated or new stances added
2. **Timeout** tuned via `ENSEMBLE_TIMEOUT` in cron environment or per-provider wrapper
3. **synthesis.md prompt** updated if structured output is unreliable
4. After changes: run `scripts/planning/ensemble-plan.sh --dry-run WRK-XXX` on 3 recent
   items to validate prompt renders correctly before live run

This is the self-improvement loop: **sessions produce planning signals → nightly pipeline
analyses them → candidates surface improvements → WRK items implement them → next sessions
run better plans**. Every improvement to the planning layer compounds across all future work.

### Integration note: `unset CLAUDECODE` in synthesise.sh

`synthesise.sh` calls `claude -p` as a subprocess with `unset CLAUDECODE` to prevent
the CLI from detecting it is running inside a Claude Code session (which would alter
behaviour or reject the call). This pattern should be preserved in any future script
that calls `claude -p` from within a hook or pipeline context.

## Related

- workstations skill: machine registry and `cron_variant` fields
- WRK-299: implementation tracking
- WRK-304: Stop hook cleanup — move analysis to pipeline
- WRK-305: Session signal emitters — wire /clear, plan-mode, per-WRK tool-counts
- WRK-303: Ensemble planning — signals feed into Planning Quality Loop above
- `/insights`, `/reflect`, `/knowledge`, `/improve`: individual pipeline stages
- `scripts/planning/` — ensemble planning outputs; harvested by Planning Quality Loop
