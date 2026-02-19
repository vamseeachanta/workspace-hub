# Session Lifecycle — Hook Catalog

> Complete inventory of all hooks in the workspace-hub Claude Code session.
> Source of truth: `.claude/settings.json`

## Session Start

No Start hooks are configured. On session initialization:

1. **CLAUDE.md** loaded (workspace-hub root + any submodule CLAUDE.md)
2. **Rules** loaded from `.claude/rules/` (security, testing, coding-style, git-workflow, patterns, legal-compliance)
3. **Memory** loaded from user-level `memory/MEMORY.md` (auto-loaded, 200-line limit)
4. **Statusline** initialized via `.claude/statusline-command.sh` (AI quota + branch info)

**Architecture**: "Fix at shutdown, verify at startup."
- **Stop hook #9** (`ensure-readiness.sh`): Runs R1 (memory curation), R5 (context budget), R6 (submodule sync) at session exit. Writes `state/readiness-report.md` for next session.
- **PreToolUse hook #3** (`readiness.sh`): Lightweight startup verification. Surfaces last session's readiness report + quick R4 (agent CLIs) + R8 (tools) checks.
- R2, R3, R7 are already covered by stop hooks #5, #8, #4 respectively.

### Session Start — Readiness Recommendations

These are proposed Start hooks (not yet implemented) to ensure context quality and avoid "context overboat" — loading stale, bloated, or redundant data into the session.

| # | Check | Script (proposed) | Purpose | Priority |
|---|-------|-------------------|---------|----------|
| R1 | **Memory Curation** | `hooks/readiness/memory-health.sh` | Verify `MEMORY.md` is under 200-line limit; flag stale entries (>30 days untouched); detect duplicate topics across repo + user memory | High |
| R2 | **Index Freshness** | `hooks/readiness/index-freshness.sh` | Check `RESOURCE_INDEX.md` age (<24h); verify `data-catalog.yml` matches actual data files; check `model-registry.yaml` hasn't drifted from provider APIs | High |
| R3 | **Skill Health** | `hooks/readiness/skill-health.sh` | Count active vs archived skills (flag if >350); detect orphan skills (no command wrapper, no usage 90+ days); verify no broken SKILL.md symlinks | Medium |
| R4 | **Agent Readiness** | `hooks/readiness/readiness.sh` | Verify `behavior-contract.yaml` exists; check 3 provider CLIs available; confirm `model-registry.yaml` freshness (<30 days) | Medium | **IMPLEMENTED** |
| R5 | **Context Budget Audit** | `hooks/readiness/readiness.sh` | Measure total bytes of auto-loaded content (CLAUDE.md + rules/ + MEMORY.md); warn if >16KB context budget exceeded | High | **IMPLEMENTED** |
| R6 | **Submodule Sync** | `hooks/readiness/submodule-sync.sh` | Check all submodules are on expected branch; detect detached HEAD; warn if local is behind remote by >5 commits | Low |
| R7 | **Pending Signal Triage** | `hooks/readiness/signal-triage.sh` | Show count of unprocessed signals from last session; display session-briefing.md highlights; prompt if >50 signals queued | Medium |
| R8 | **Environment Validation** | `hooks/readiness/readiness.sh` | Verify python3 available; check `jq`, `curl` (required), `yq` (optional); confirm `WORKSPACE_HUB` env var set | Low | **IMPLEMENTED** |

**Implementation approach**: A single `readiness.sh` dispatcher script that runs all checks in parallel (each <100ms), aggregates results, and outputs a readiness summary to the terminal. Non-blocking — warnings only, never prevents session start.

**Context overload prevention**: The key insight is that every auto-loaded file (CLAUDE.md, rules/, MEMORY.md) consumes context budget. If these files grow unchecked, the agent starts each session with less room for actual work. The readiness checks enforce the 16KB context budget by measuring and warning proactively.

---

## During Session — PreToolUse

Runs **before** every tool call. Hooks receive tool input via stdin (JSON).

| # | Matcher | Script | Purpose | Latency |
|---|---------|--------|---------|---------|
| 1 | `.*` | `hooks/session-logger.sh pre` | Log tool name, input preview to `state/sessions/*.jsonl` | <5ms |
| 2 | `.*` | `hooks/propagate-ecosystem-check.sh` | Daily symlink validation across ecosystem skills | <10ms |
| 3 | `.*` | `hooks/readiness/readiness.sh` | Session readiness checks (R4+R5+R8), runs once per session | <200ms (first call) |
| 4 | `Write\|Edit\|MultiEdit` | inline `echo` | Display "Edit: \<path\>" notification in terminal | <1ms |

### Details

**session-logger.sh (pre)**: Receives piped stdin with tool input JSON. Logs tool name, timestamp, and truncated input to per-session JSONL file at `.claude/state/sessions/`.

**propagate-ecosystem-check.sh**: Checks `.claude/skills/.ecosystem-propagated` timestamp. If >24h old, validates symlinks between workspace-hub and submodules. Runs silently on success; outputs warning if broken symlinks found.

**Edit notification**: Inline command extracts `file_path` from tool input JSON via `jq` and echoes it for user awareness.

---

## During Session — PostToolUse

Runs **after** every tool call. Hooks receive tool result via stdin (JSON).

| # | Matcher | Script | Purpose | Latency |
|---|---------|--------|---------|---------|
| 1 | `.*` | `hooks/session-logger.sh post` | Log tool result status to `state/sessions/*.jsonl` | <5ms |
| 2 | `Write\|Edit\|MultiEdit` | inline `echo` | Display "Saved: \<path\>" confirmation | <1ms |
| 3 | `Write\|Edit\|MultiEdit` | `hooks/capture-corrections.sh` | Detect correction chains, record edit patterns | <50ms |

### Details

**session-logger.sh (post)**: Appends execution result (success/failure, duration) to same session JSONL.

**Save notification**: Confirms file write completed. Mirrors the PreToolUse edit notification.

**capture-corrections.sh**: Analyzes edit sequences. If same file edited 3+ times in quick succession, flags as "correction chain" — evidence of trial-and-error that should become a rule or skill. Writes to `.claude/state/corrections/.recent_edits` and `.claude/state/pending-reviews/insights.jsonl`.

---

## Context Compression — PreCompact

Runs when Claude Code compresses conversation context (manual or auto).

| # | Matcher | Script | Purpose |
|---|---------|--------|---------|
| 1 | `.*` | `hooks/session-memory/pre-compact-save.sh` | Persist active plan state, WRK context to session memory |
| 2 | `manual` | inline `echo` | Remind about delegation patterns and agent library |
| 3 | `auto` | inline `echo` | Context tips for auto-compaction |

### Details

**pre-compact-save.sh**: Saves current plan file path, active WRK item, and key context snippets to `.claude/state/session-memory/` so they survive compaction.

**Manual compact reminder**: Outputs agent library locations and TDD/batch rules to help user maintain context.

**Auto compact tips**: Reminds to preserve Task tool delegation awareness through auto-compaction.

---

## Session Exit — Stop

Fires on **`/exit`**, **Ctrl+C**, and **timeout**. All hooks run sequentially. Each wraps command in `2>/dev/null || true` for interrupt safety.

| # | Script | Purpose | Latency |
|---|--------|---------|---------|
| 1 | `hooks/session-memory/session-end-evaluate.sh` | Score delegation patterns, log session metrics | ~2s |
| 2 | inline timestamp | Print session end timestamp | <1ms |
| 3 | `hooks/post-task-review.sh` | Display learning checklist | ~1s |
| 4 | `hooks/consume-signals.sh` | Process all pending JSONL signals, generate briefing, draft WRK items, archive signals | ~3s |
| 5 | `scripts/generate-resource-index.sh` | Refresh `.claude/RESOURCE_INDEX.md` from filesystem scan | ~2s |
| 6 | `scripts/ai/assessment/query-quota.sh --refresh --log` | Snapshot AI provider quotas to `config/ai-tools/agent-quota-latest.json` | ~5s |
| 7 | `hooks/wrk-traceability-check.sh` | Warn if no WRK item was created or modified during session | <1s |
| 8 | `hooks/ecosystem-health-check.sh` | Skill/memory health signals to pending-reviews | ~1s |
| 9 | `hooks/readiness/ensure-readiness.sh` | Ensure next session starts clean (R1+R5+R6) | ~1s |
| 10 | `scripts/improve/improve.sh` | Autonomous /improve — shell + Anthropic API hybrid | ~30-60s |

### Details

**session-end-evaluate.sh** (#1): Reads session log, scores delegation ratio (subagent use vs direct execution). Appends delegation score to `.claude/state/sessions/` metrics.

**Session timestamp** (#2): Prints `Session ended at YYYY-MM-DD_HH:MM:SS` for audit trail.

**post-task-review.sh** (#3): Displays checklist of learning questions: "Did you discover a new pattern?", "Should anything be added to memory?", etc. Output only — no file writes.

**consume-signals.sh** (#4): The heaviest stop hook (358 LOC). Merges all `.claude/state/pending-reviews/*.jsonl` signals, updates `accumulator.json` (cross-session tracking), generates `session-briefing.md`, optionally drafts a WRK item if new files were created. Archives processed signals to `state/archive/YYYYMMDD/`.

**generate-resource-index.sh** (#5): Scans `.claude/` filesystem for agents, skills, docs, rules. Regenerates `RESOURCE_INDEX.md` with categorized paths and descriptions.

**query-quota.sh** (#6): Queries Claude OAuth API, Codex session logs, and Gemini manual cache. Writes snapshot to `config/ai-tools/agent-quota-latest.json` and appends to usage log.

**wrk-traceability-check.sh** (#7): Scans `git diff --name-only` for WRK-*.md files. If none touched, outputs warning: "No WRK item created or modified this session."

**ecosystem-health-check.sh** (#8): Counts skills, checks memory line counts, detects orphan skills. Writes health signals to `.claude/state/pending-reviews/ecosystem-review.jsonl`.

**improve.sh** (#9): Hybrid shell + Anthropic API script that implements the `/improve` skill autonomously. 8 phases: collects signals (shell), classifies improvements (API), reviews ecosystem health (shell), applies guards (shell), generates and writes improvements (API + shell), **surfaces recommendations to user** (shell — Phase 5.5), logs changes (shell), and cleans up signals (shell). Recommendations include: skill gap detection, tool/plugin suggestions, ecosystem warnings, and correction pattern analysis.

### Session Stop — Additional Recommendations

Beyond the 9 existing stop hooks, these are recommended enhancements for review:

| # | Enhancement | Script (proposed) | Purpose | Priority |
|---|-------------|-------------------|---------|----------|
| S-R1 | **Cost Tracking** | `hooks/cost-tracker.sh` | Estimate session API cost from tool call counts + model used; append to `state/cost-log.csv`; weekly cost report | Medium |
| S-R2 | **Submodule Drift Detector** | `hooks/submodule-drift.sh` | Compare submodule pointers to remote HEAD; flag repos where local is >3 commits behind; output "pull needed" list for next session | Medium |
| S-R3 | **Dead Code Scanner** | `hooks/dead-code-scan.sh` | Scan for files created this session that were never imported/referenced; flag orphan test fixtures; check for dangling symlinks created during session | Low |
| S-R4 | **Context Efficiency Score** | `hooks/context-efficiency.sh` | Measure: (a) delegation ratio (subagent vs direct), (b) tool calls per task, (c) edit-correction chains; output efficiency grade A-F | Low |
| S-R5 | **Cross-Session Continuity** | `hooks/continuity-save.sh` | Persist active WRK item, current file being worked on, last test results; restore these as "session resume context" on next start | High |
| S-R6 | **Legal Compliance Gate** | `hooks/legal-quick-scan.sh` | Run fast legal deny-list scan on files modified this session; warn (not block) if potential client references detected | High |

**Key observation**: Stop hooks currently total ~45-95s. Adding more hooks should be carefully weighed against exit latency. Recommendations S-R1 through S-R4 are lightweight (<1s each). S-R5 and S-R6 would add ~2-3s. The total budget should stay under 120s.

---

## Signal Flow Summary

```
PreToolUse ──→ session-logger.sh ──→ state/sessions/*.jsonl
PostToolUse ──→ capture-corrections.sh ──→ state/corrections/, state/pending-reviews/
Stop #1 ──→ session-end-evaluate.sh ──→ state/sessions/ (metrics)
Stop #4 ──→ consume-signals.sh ──→ accumulator.json, session-briefing.md, archive/
Stop #8 ──→ ecosystem-health-check.sh ──→ state/pending-reviews/ecosystem-review.jsonl
Stop #9 ──→ improve.sh ──→ writes to .claude/{memory,rules,skills,docs}, logs to state/improve-changelog.yaml
```

---

## Pre-Clear Workflow

`/clear` is a Claude Code built-in CLI command that destroys all in-session context. It
**cannot be intercepted** by any hook (PreToolUse, PostToolUse, PreCompact, Stop). The only
way to preserve context before `/clear` is a user-initiated snapshot.

### Pattern: `/save` → `/clear`

```
/save    ← run this FIRST — captures WRK state + Claude writes Ideas/Notes
/clear   ← then clear safely
```

### What `/save` captures

1. **File-based state** (via `save-snapshot.sh`):
   - Active WRK items from `work-queue/working/` — id, title, percent complete, last done step, next step
   - Recently modified WRK items (`git diff --name-only HEAD`)
   - Current branch + timestamp

2. **Conversational context** (via Claude):
   - Ideas discussed but not yet in a WRK item
   - Decisions made (architectural, process, tooling)
   - Follow-up tasks mentioned conversationally

### Output

`.claude/state/session-snapshot.md` — gitignored, human-readable Markdown.

```markdown
# Session Snapshot — 2026-02-19T14:30:00Z
Branch: feature/WRK-205-skills-knowledge-graph

## Active WRK Items
- WRK-205: Skills knowledge graph (60% complete)
  - Last done: Step 3 — canonical_ref to 115 _diverged/ SKILL.md
  - Next: Step 5 — 12 category INDEX.md files

## Recently Modified
- WRK-080: added Blog Post 5 candidate

## Ideas / Notes
- [Claude writes conversational context here]
```

### Auto-surfacing in next session

`ensure-readiness.sh` (Stop hook R9) checks at session exit whether a snapshot exists and is
<48h old. If so, it writes an info message to the readiness report:

```
R9: Session snapshot found (Xh old) — read .claude/state/session-snapshot.md to resume last session context
```

The readiness report is surfaced by `readiness.sh` (PreToolUse hook #3) at the start of the
next session, so Claude sees the snapshot hint on the first tool call.

### Implementation

| File | Role |
|------|------|
| `.claude/hooks/session-memory/save-snapshot.sh` | Captures file-based state; writes snapshot |
| `.claude/skills/workspace-hub/save/SKILL.md` | `/save` user-invocable skill definition |
| `.claude/hooks/readiness/ensure-readiness.sh` | R9 check: surface snapshot if <48h old |

---

## State Directories

| Directory | Purpose | Persists? |
|-----------|---------|-----------|
| `.claude/state/sessions/` | Per-session tool logs (JSONL) | Gitignored |
| `.claude/state/corrections/` | Edit correction chains | Gitignored |
| `.claude/state/pending-reviews/` | Unprocessed signals for consume-signals.sh | Gitignored |
| `.claude/state/archive/YYYYMMDD/` | Archived processed signals | Gitignored |
| `.claude/state/session-memory/` | Context survival across compaction | Gitignored |
| `.claude/state/patterns/` | Patterns from /reflect | Gitignored |
| `.claude/state/improve-changelog.yaml` | /improve audit trail | Gitignored |
| `.claude/state/session-snapshot.md` | Pre-clear session snapshot (from /save) | Gitignored |
| `config/ai-tools/agent-quota-latest.json` | AI provider quota snapshot | Tracked |
