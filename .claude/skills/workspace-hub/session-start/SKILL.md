---
name: session-start
description: >
  Session startup briefing — surfaces readiness warnings, last session snapshot,
  top 3 unblocked pending work items, and quota status. Run at the beginning of
  every session before starting work.
version: 1.0.0
updated: 2026-02-19
category: workspace-hub
triggers:
  - session start
  - start session
  - morning briefing
  - what should I work on
  - session briefing
  - startup check
related_skills:
  - workspace-hub/save
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/improve
capabilities:
  - readiness-surface
  - snapshot-surface
  - queue-briefing
  - quota-check
requires: []
invoke: session-start
tags: []
---
# Session Start Skill

Run at the start of every session. Surfaces state from the previous session
and orients the orchestrator before any work begins.

## When to Use

- First action in every new session (before responding to any work request)
- After `/clear` (context was wiped — re-orient)
- When returning from a multi-day break

## Steps Claude Follows

### 0. Auto-Load Drift-Risk Rules (non-interactive, < 2s)

Read these three files into context before any other step. No prompts. No checks.
The goal is to have the canonical rules in context before any task begins.

- `.claude/rules/python-runtime.md` — hard rule: `uv run` always, never bare `python3`
- `.claude/rules/git-workflow.md` — conventional commits, branch naming, submodule order
- `.claude/skills/workspace-hub/file-taxonomy/SKILL.md` — where files belong in each repo

After reading, append a best-effort log event (create dir if missing, skip silently on failure):
```bash
mkdir -p logs/orchestrator/claude/
echo "{\"event\":\"drift_rules_loaded\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"files\":[\"python-runtime\",\"git-workflow\",\"file-taxonomy\"]}" \
  >> logs/orchestrator/claude/session_$(date +%Y%m%d).jsonl || true
```

### 1. Readiness Report (from last session's stop hook)

Read `.claude/state/readiness-report.md`. If it contains `## Warnings`, surface each
warning to the user with the suggested fix. If "All Clear", note it briefly.

### 1b. Repo Health Check (from nightly smoke tests)

Read `.claude/state/session-health.yaml`. Check freshness and health:

```bash
# Determine age of health check
if [[ -f .claude/state/session-health.yaml ]]; then
  age_hours=$(( ($(date +%s) - $(stat -c %Y .claude/state/session-health.yaml)) / 3600 ))
  all_healthy=$(grep "^all_healthy:" .claude/state/session-health.yaml | awk '{print $2}')
fi
```

- If `all_healthy: true` and age < 36h → display "All repos healthy" (one line)
- If any repo failed → display warning with failed repo names and suggest investigating before selecting WRK work in that repo
- If file missing or stale (>36h) → display "Health check stale — consider: `bash scripts/cron/nightly-smoke-tests.sh`"

### 2. Session Snapshot (from /save before last /clear)

Check snapshot freshness (deterministic, no inline date math):
```bash
bash scripts/session/snapshot-age.sh
```
If exit 0 (fresh), read `.claude/state/session-snapshot.md` and surface the `## Ideas / Notes`
section and WRK summary. If exit 1 (stale/missing), skip.

### 2b. Knowledge Base Surfacing

If the active WRK is known, query the knowledge base for relevant past work:

```bash
bash scripts/knowledge/query-knowledge.sh --category <wrk-category> --limit 3
```

Surface up to 3 relevant entries as "Past work context:" with entry ID and mission snippet.
If `knowledge-base/` does not exist or is empty, skip silently.

### 3. Quota Status

```bash
bash scripts/session/quota-status.sh
```
Prints per-provider utilization lines when thresholds trigger (>=90% WARN, 70-89% NOTE, <70% silent).
File age and null values handled automatically. Always exits 0.

### 3b. Agent Teams Status

List `~/.claude/teams/` dirs (if any). For each, note WRK mapping (wrk-NNN-slug convention)
and whether that WRK is still active. Then run the tidy script in dry-run mode and surface
any teams or stale task dirs it would remove:

```bash
ls ~/.claude/teams/ 2>/dev/null || echo "(no active teams)"
bash scripts/hooks/tidy-agent-teams.sh --dry-run
```

If teams exist that belong to archived WRKs, note that they will be auto-removed at next
stage-gate. If you need to spawn a new team for the current WRK, use:
`bash scripts/work-queue/spawn-team.sh WRK-NNN <slug>` — prints the recipe, does not auto-create.

### 3d. Scope Discipline Check

Read `.claude/state/active-wrk`. If line 1 contains a WRK ID:

```
**Active WRK:** WRK-NNN (started: <timestamp from line 2>)
⚠ One-feature-per-session: complete or checkpoint this WRK before starting another.
```

This is informational only (the hard block is in `set-active-wrk.sh --force` to bypass).

### 3c. Active Session Audit (when starting work)

If about to pick up a WRK item, run:

```bash
bash scripts/work-queue/active-sessions.sh --unclaimed-only
```

If any items appear, investigate before starting — another session may already be
executing them. An unclaimed item has a recent session lock (< 2h) but has not yet
had `claim-item.sh` run. This indicates a session collision risk.

### 4. Top Items by Category

```bash
bash scripts/work-queue/whats-next.sh --all
```
Shows top unblocked items across all categories. Pass `--category <name>` to narrow.
Present the output verbatim — the script handles all filtering and formatting.

### 5. Computer Context

If a `computer:` field exists in recent working/ items or in `.claude/state/`,
note which machine was last active. Prompt user to confirm if working on a different
machine today (multi-machine handoff check).

### 5b. Repo-Map Context (when target_repos set)

```bash
bash scripts/session/repo-map-context.sh
```
Auto-detects the active WRK from `working/`. Outputs purpose + test_command for each
tier-1 target repo. Non-blocking: workspace-hub and unknown repos handled gracefully.

### 6. Mandatory `/work` Handoff and Approval Gate

Before any implementation begins:

- Select or create a WRK item through `/work` flow.
- Confirm plan exists for the WRK item.
- Require explicit user approval that names the WRK ID.
- If approval does not include WRK ID, continue planning only and do not execute.

This gate is mandatory and enforced by workflow policy.

## Output Format

```
## Session Briefing — 2026-02-19

**Readiness:** [All Clear | N warnings listed]
**Snapshot:** [Summary of Ideas/Notes if fresh | None]
**Quota:** Claude 11% | Codex 43% | Gemini 0%

**Top unblocked per category:**
- harness     → WRK-NNN [HIGH] title
- engineering → WRK-NNN [MEDIUM] title
- data        → (none unblocked)
- platform    → WRK-NNN [HIGH] title
- business    → (none unblocked)
- maintenance → WRK-NNN [LOW] title
- personal    → (none unblocked)
```

## Path Discipline Reminder

Surface this reminder silently at session start (do not print unless a violation is detected):

- **Prefer relative paths** inside repo-scoped scripts (e.g., `./scripts/foo.sh`, not `/mnt/...`)
- **Never hardcode** `/mnt/local-analysis/workspace-hub/` in generated scripts — use `${REPO_ROOT}`,
  `$(git rev-parse --show-toplevel)`, or `$(pwd)` instead
- **Absolute paths** are allowed only when a tool explicitly requires them (e.g., `file_path` in
  Read/Edit/Write tool calls)
- If you catch yourself writing a hardcoded `/mnt/` path in a script, stop and replace it with the
  env-var form before proceeding

## Hook Integration

This skill is also invocable as a startup context. Add to CLAUDE.md:
> At the start of every new session, run `/session-start` to orient before responding.
