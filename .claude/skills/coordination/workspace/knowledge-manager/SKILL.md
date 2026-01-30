---
name: knowledge-manager
description: Capture, organize, and surface institutional knowledge across sessions and repositories
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - knowledge-capture
  - knowledge-search
  - knowledge-advise
  - knowledge-review
  - knowledge-stats
  - confidence-decay
  - index-rebuild
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
related_skills: [claude-reflect, work-queue, repo-capability-map, knowledge-base-system]
scripts:
  - scripts/knowledge-index.sh
  - scripts/knowledge-capture.sh
  - scripts/knowledge-search.sh
  - scripts/knowledge-advise.sh
  - scripts/knowledge-review.sh
  - scripts/knowledge-stats.sh
---

# Knowledge Manager

> Capture, organize, and surface institutional knowledge across sessions and repositories.

## Quick Start

```bash
# Show knowledge base status
/knowledge

# Capture knowledge from current session
/knowledge capture

# Get advice before starting a task
/knowledge advise "implement feature in digitalmodel"

# Search knowledge base
/knowledge search --tag orchestrator

# Review stale entries
/knowledge review
```

## When to Use

- **Starting a session**: Run `/knowledge advise` with task context to surface relevant knowledge
- **After a session**: Run `/knowledge capture` to extract learnings
- **During reflection**: Automatically called by `daily-reflect.sh` in PHASE 4
- **Weekly maintenance**: Run `/knowledge review` to prune stale entries

## Overview

The Knowledge Manager implements a structured institutional memory system with five entry types:

| Type | Prefix | Purpose |
|------|--------|---------|
| Decision | `ADR-` | Architectural decision records |
| Pattern | `PAT-` | Reusable patterns discovered |
| Gotcha | `GOT-` | Things to avoid / pitfalls |
| Correction | `COR-` | Synthesized from correction logs |
| Tip | `TIP-` | Quick best practices |

### Storage

- **Entries**: `.claude/knowledge/entries/{decisions,patterns,gotchas,corrections,tips}/`
- **Index**: `.claude/knowledge/index.json` (machine-readable, rebuilt by `knowledge-index.sh`)
- **Archive**: `.claude/knowledge/archive/` (decayed/superseded entries)
- **Templates**: `templates/` directory in this skill

### Confidence Model

Each entry has a confidence score (0.0-1.0):
- Decay: -0.02/week unless revalidated
- Revalidation (confirmed useful): +0.1
- Negative feedback: -0.05
- Archive threshold: confidence < 0.3 AND no access in 90 days

## Commands

| Command | Alias | Script | Purpose |
|---------|-------|--------|---------|
| `/knowledge` | `/k` | - | Show status summary |
| `/knowledge capture` | `/kc` | `knowledge-capture.sh` | Extract and store knowledge |
| `/knowledge advise` | `/ka` | `knowledge-advise.sh` | Surface relevant knowledge |
| `/knowledge search` | `/ks` | `knowledge-search.sh` | Search by keyword/tag/type/category |
| `/knowledge review` | `/kr` | `knowledge-review.sh` | Review stale entries, decay confidence |
| `/knowledge stats` | - | `knowledge-stats.sh` | Dashboard with health metrics |

## Integration Points

| System | Integration |
|--------|-------------|
| `claude-reflect` | Auto-capture in PHASE 4 (STORE) after create-skills.sh |
| `claude-reflect` | Health check in daily checklist |
| `repo-capability-map` | `/ka` checks capability map for target repo context |
| `work-queue` | Before processing WRK items, run `/ka` with item context |
| `learned-patterns.json` | Superseded by index.json; old file kept for compat |

## Prerequisites

- `jq` for JSON processing
- `grep` for full-text search
- Bash 4+ for associative arrays

## File Structure

```
.claude/knowledge/
  index.json
  entries/
    decisions/ADR-*.md
    patterns/PAT-*.md
    gotchas/GOT-*.md
    corrections/COR-*.md
    tips/TIP-*.md
  archive/
```
