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
