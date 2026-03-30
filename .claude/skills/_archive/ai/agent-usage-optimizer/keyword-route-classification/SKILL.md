---
name: agent-usage-optimizer-keyword-route-classification
description: "Sub-skill of agent-usage-optimizer: Keyword \u2192 Route classification."
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Keyword → Route classification

## Keyword → Route classification


```
Compound / Route C keywords:
  architecture, design, system, multi-file, refactor, security review,
  cross-repo, orchestrat, compound, plan, spec

Standard / Route B keywords:
  implement, feature, review, documentation, test, bug, fix, config,
  update, migrate, integration

Simple / Route A keywords:
  generate, scaffold, unit test, snippet, function, debug, format,
  check, validate, search, grep

Bulk keywords:
  summarise, summarize, batch, bulk, all files, across repos, report

Long-context keywords:
  large file, full repo, 1000 lines, entire codebase, cross-repo scan
```

Output format for ad-hoc recommendation:

```
Task: "implement OAuth login for the API"
Route: B (Standard)

  Primary:    Claude Sonnet  [quota: <CLAUDE>% — OK]
  Secondary:  Codex          [quota: <CODEX>%  — OK]

  Rationale: Standard feature implementation with moderate complexity.
             Sonnet provides quality output within quota headroom.
             Codex is secondary for focused function-level generation.
```
