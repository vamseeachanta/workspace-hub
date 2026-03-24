---
title: "chore(harness): trim 30 child repo CLAUDE.md files to 20-line adapter format"
priority: high
category: harness
subcategory: compliance
complexity: medium
created_at: "2026-03-20T20:00:00Z"
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1247
---

30 child repo CLAUDE.md files exceed the 20-line limit. Apply same treatment as workspace-hub: AGENTS.md canonical, CLAUDE.md thin adapter. Propagate via scripts/compliance/propagate_claude_config.py. Delete CODEX.md from child repos where present.

Spawned from WRK-1384 harness-audit findings.
