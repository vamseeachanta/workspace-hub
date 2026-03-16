---
name: work-document-exit-no-active-wrk-fallback
description: 'Sub-skill of work-document-exit: No-Active-WRK Fallback.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# No-Active-WRK Fallback

## No-Active-WRK Fallback


When `WRK_ID` is "general" (no active WRK found):

1. Still collect changed files from git diff
2. Write a general session summary to `.claude/state/session-handoff.md`
3. Skip the WRK file append step
4. Print the same commit command output

The handoff note is still useful even without an active WRK item.
