---
name: session-start-routine
description: Pre-flight checks at session start — load context, check prior state, validate env, check for in-flight work from other terminals
version: 1.0.0
category: coordination
tags: [session, startup, preflight, governance]
related_skills:
  - session-corpus-audit
  - comprehensive-learning
---

# Session Start Routine

Pre-flight checklist for every new session. Run these checks before beginning work.

## Checklist

### 1. Load context
- Load memory context files from the repo memory directory
- Check `MEMORY.md` for active project state and recent feedback

### 2. Check prior session state
- Read today's session signals: `.claude/state/session-signals/YYYY-MM-DD.jsonl`
- Look for sessions that ended mid-task (incomplete commits, unreleased `wip:` labels)
- Check `git status` for uncommitted work from prior sessions

### 3. Check for in-flight work
- Scan for wip labels on GitHub issues (gh issue list filtered by wip label)
- Check other terminals: `ps aux | grep claude | grep -v grep`
- Check `/tmp/.claude-wip-*` markers if present

### 4. Validate environment
- Verify tools: `uv --version`, `gh auth status`, `git status`
- Check disk space: `df -h /mnt/local-analysis`
- Verify governance hooks are registered in settings

### 5. Check governance limits
- Review tool-call counter: `.claude/state/session-governor/tool-call-count`
- Confirm counter is below 200 ceiling (or reset if new day)

## When to use
- Start of every interactive session
- After a context reset or conversation compression
- When resuming work after a break
- When the user asks for a terse live "status update" from mobile/Telegram

## Mobile status-update mode

When the user asks only "Status update" (especially from Telegram), produce a compact evidence-backed snapshot rather than a broad narrative.

1. Gather live state before summarizing:
   - `git status --short --branch` in the active repo.
   - Active/background agent processes or Hermes process-manager state.
   - `hermes cron`/cronjob list for active, paused, failed, and next scheduled jobs.
   - GitHub counts for `wip`, `status:plan-review`, `status:plan-approved`, and recent closed issues.
   - Most recent relevant cron output files when scheduled jobs produced user-facing findings.
2. Separate counts clearly:
   - live label counts are not the same as artifact-audited approval readiness;
   - closed/recent results are not the same as currently running lanes;
   - paused autofeed monitors are not active throughput.
3. For Telegram/mobile delivery:
   - avoid pipe tables; use numbered bullets and labeled key/value lines;
   - link GitHub issues as `[#{number}](url)`;
   - keep to the shortest useful update, with risks and next best action last.
4. Never clean/reset/stage dirty control-plane files during a status-only request; report dirty state and recommend a narrow reconciliation pass if needed.
