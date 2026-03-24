---
title: "chore(harness): propagate canonical AGENTS.md format to child repos"
priority: medium
category: harness
subcategory: compliance
complexity: simple
blocked_by: [WRK-1386]
created_at: "2026-03-20T20:00:00Z"
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1249
---

Child repos have AGENTS.md files (9-11 lines each) that predate the WRK-1384 canonical format. Update them to include hard gates and commands from the workspace-hub AGENTS.md template, adapted per-repo (test commands, primary modules).

Blocked by WRK-1386 (child repo CLAUDE.md trimming — do together).
