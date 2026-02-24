---
id: PAT-004
type: pattern
title: "Parallel team execution for independent WRK items"
category: orchestration
tags: [orchestration, team, parallel, wrk, delegation]
repos: [workspace-hub]
confidence: 0.85
created: "2026-02-24"
last_validated: "2026-02-24"
source_type: session
related: [ADR-001]
status: active
access_count: 0
---

# Parallel Team Execution for Independent WRK Items

## Problem

Related WRK items that are nominally sequenced (WRK-315 → WRK-316) may actually
be independent in practice if they touch completely different files. Sequential
execution wastes wall-clock time.

## Solution

Identify file-level independence before assuming sequential ordering. If two WRK
items have no shared files, spawn them as parallel team agents:

```
Team lead
├── wrk-315-agent  (aggregator.py, test_extractors.py, pipeline postproc scripts)
└── wrk-316-agent  (scripts/inventory/, LEGACY_SCRIPT_INVENTORY.md)
```

Key conditions for safe parallelism:
- No shared files (verify before spawning)
- Both agents have complete context in their prompts (no cross-agent dependencies)
- Worktrees not required if files are cleanly disjoint

## When to Use

- Discovery tasks (WRK-316 inventory) alongside implementation tasks (WRK-315)
- Any WRK pair where sequencing is "logical" but not "file-level"
- Multi-repo work where repos are independent

## Validated In

WRK-315 + WRK-316 parallel execution (2026-02-24):
- WRK-316 completed in ~5 min while WRK-315 ran concurrently (~15 min)
- Zero merge conflicts, both legal scans passed independently
