---
id: GOT-001
type: gotcha
title: "learned-patterns.json has no useful data"
category: data
tags: [learned-patterns, reflect, data-quality, broken]
repos: [workspace-hub]
confidence: 0.95
created: "2026-01-30"
last_validated: "2026-01-30"
source_type: manual
related: [ADR-002]
status: active
access_count: 0
---

# learned-patterns.json Has No Useful Data

## Symptom

The file `~/.claude/memory/patterns/learned-patterns.json` contains 500+ entries, but every entry has `"delegation_score": "unknown"` and empty arrays for patterns. No actionable data can be extracted from it.

## Root Cause

The pattern extraction pipeline in claude-reflect populates the JSON structure but does not compute meaningful delegation scores or extract specific pattern details. The entries are statistical stubs rather than knowledge.

## Fix / Workaround

Do not rely on learned-patterns.json for knowledge retrieval. Use the new knowledge manager system (`.claude/knowledge/`) which stores human-readable, validated entries with confidence scores and decay mechanisms.

## Prevention

The knowledge-manager skill replaces learned-patterns.json functionality with index.json. The old file is kept for backward compatibility but is effectively superseded.
