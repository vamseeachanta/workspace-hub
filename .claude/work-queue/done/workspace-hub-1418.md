---
id: WRK-1418
title: "Weekly: lean out CLAUDE.md, AGENTS.md, memory, rules, patterns, feedback into bash files or microskills"
repo: workspace-hub
type: task
complexity: A
priority: medium
status: done
created: 2026-03-25
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1418
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1418
---

# WRK-1418: Weekly lean-out of harness files

## Description

Create a weekly recurring story to audit and lean out transient/bloated content from:
- CLAUDE.md, AGENTS.md, GEMINI.md (max 20 lines each per coding-style rule)
- MEMORY.md and memory files (prune stale, deduplicate)
- .claude/rules/ (patterns.md, coding-style.md)
- Feedback memory files (consolidate or graduate to hooks/scripts)
- Other transient files that accumulate clutter

Migrate excess content into:
- Bash scripts (for enforceable rules)
- Microskills (for guidance/checklists)
- Hooks (for must-never-miss enforcement)

Goal: keep harness files concise, reduce context window overhead, avoid confusion from contradictory or redundant instructions.

## Acceptance Criteria

- Each harness file stays within its line budget
- Stale memory files removed or updated
- Rules that can be scripted are promoted per enforcement gradient (patterns.md)
- No duplicate guidance across files
