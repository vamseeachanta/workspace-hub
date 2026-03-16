---
name: work-document-exit-what-it-does
description: 'Sub-skill of work-document-exit: What It Does.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# What It Does

## What It Does


1. Identifies the active WRK item
2. Collects session context: files changed, progress summary, next steps
3. Writes `## Session Handoff — <date>` to the WRK item file
4. Stages changed files (or prints the `git add` command)
5. Outputs a ready-to-run commit command
6. Clears `.claude/state/active-wrk` if it exists
7. Captures gatepass status notes for next close verification

---
