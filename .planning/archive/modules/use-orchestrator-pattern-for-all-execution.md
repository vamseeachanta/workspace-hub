# Knowledge Manager Skill

> Capture, organize, and surface institutional knowledge across sessions and repositories.

## Problem

Five gaps in the current workspace-hub knowledge ecosystem:

1. **`learned-patterns.json` is broken** - 500+ entries all with `"delegation_score": "unknown"` and empty arrays
2. **No decision log** - Architectural decisions are lost between sessions
3. **No correction synthesis** - `.claude/state/corrections/` captures raw data but never produces learnings
4. **No pre-task knowledge retrieval** - Sessions start cold with no `/advise` equivalent
5. **No searchable knowledge entries** - Reflect extracts statistical patterns, not human-readable knowledge

## Research Summary

Key patterns from online research and community best practices:

| Pattern | Source | Key Insight |
|---------|--------|-------------|
| CLAUDE.md as compounding knowledge | Matt Stockton blog | Every captured instruction compounds; success depends on capture quality |
| Two-tier memory | memory-mcp community project | Auto-generated briefing + full state store with confidence decay |
| Retrospective + Advise | Sionic AI / Hugging Face | `/retrospective` extracts knowledge; `/advise` surfaces it pre-task; Failed Attempts tables most-read |
| Progressive disclosure | Anthropic skills docs | Metadata (~100 tokens) -> full content (<5K) -> resources on demand |
| Cross-repo MCP | Forgetful + Serena | Encode repo architecture into portable queryable memory |

## Design

### Storage: Markdown entries + JSON index

Each knowledge entry = markdown file with YAML frontmatter (consistent with WRK-*.md, SKILL.md, specs/).
A machine-readable `index.json` enables fast search without reading every file.

### Entry Types

| Type | Prefix | Purpose | Example |
|------|--------|---------|---------|
| Decision | `ADR-` | Architectural decision records | "Use orchestrator pattern for all execution" |
| Pattern | `PAT-` | Reusable patterns discovered | "TDD before implementation" |
| Gotcha | `GOT-` | Things to avoid / pitfalls | "learned-patterns.json is empty, don't rely on it" |
| Correction | `COR-` | Synthesized from correction logs | "Daily reflect race condition with cron" |
| Tip | `TIP-` | Quick best practices | "Use find-based repo discovery not submodule foreach" |

### Entry Format

```yaml
---
id: ADR-001
type: decision
title: Use orchestrator pattern for all execution
category: architecture    # architecture|workflow|tooling|testing|integration|data|infra
tags: [orchestrator, delegation, subagents]
repos: [workspace-hub]
confidence: 0.9           # 0.0-1.0, decays over time
created: 2026-01-30
last_validated: 2026-01-30
source_type: manual        # manual|reflect|correction-synthesis
related: []
status: active             # active|archived|superseded
access_count: 0
---

# Use Orchestrator Pattern for All Execution

## Context
[Why this decision was needed]

## Decision
[What was decided]

## Rationale
[Why this approach over alternatives]

## Consequences
[Trade-offs and implications]
```

### Confidence Decay

- Decay: 0.02/week unless revalidated
- Revalidation (confirmed useful): +0.1 confidence
- Negative feedback: -0.05 confidence
- Archive threshold: confidence < 0.3 AND no access in 90 days

### Slash Commands

| Command | Alias | Purpose |
|---------|-------|---------|
| `/knowledge` | `/k` | Main entry - shows status summary |
| `/knowledge capture` | `/kc` | Extract and store knowledge from current session |
| `/knowledge advise` | `/ka` | Surface relevant knowledge for current task |
| `/knowledge search` | `/ks` | Search by keyword/tag/type/category |
| `/knowledge review` | `/kr` | Review stale entries, prune or revalidate |
| `/knowledge stats` | - | Dashboard with health metrics |

### File Structure

```
.claude/knowledge/                              # NEW - knowledge store
  index.json                                    # Machine-readable index
  entries/
    decisions/ADR-001-orchestrator-pattern.md
    patterns/PAT-001-tdd-before-implementation.md
    gotchas/GOT-001-learned-patterns-empty.md
    corrections/COR-001-daily-reflect-race.md
    tips/TIP-001-find-based-repo-discovery.md
  archive/                                      # Decayed/superseded entries

.claude/skills/coordination/workspace/
  knowledge-manager/                            # NEW - skill definition
    SKILL.md
    scripts/
      knowledge-capture.sh
      knowledge-advise.sh
      knowledge-search.sh
      knowledge-review.sh
      knowledge-stats.sh
      knowledge-index.sh
    templates/
      decision.md
      pattern.md
      gotcha.md
      correction.md
      tip.md

.claude/commands/workspace-hub/
  knowledge.md                                  # NEW - /knowledge command
```

### Integration Points

| System | Integration | Change |
|--------|-------------|--------|
| `claude-reflect` | Auto-capture in PHASE 4 (STORE) | Add knowledge-capture call after create-skills.sh |
| `claude-reflect` | Health check in checklist | Add knowledge base health item |
| `repo-capability-map` | Context enrichment | `/ka` checks capability map for target repo |
| `work-queue` | Pre-task advise | Before processing WRK items, run `/ka` with item context |
| `learned-patterns.json` | Superseded | index.json replaces its function; old file kept for compat |

## Decisions

- **Scope**: Full system (all 4 phases)
- **Language**: Bash only (consistent with reflect scripts, uses `jq` for JSON, `grep` for search)
- **Advise UX**: Auto-suggest at session start via session-start-routine integration

## Implementation Plan

### Phase 1: Foundation
1. Create `.claude/knowledge/` directory structure (`entries/{decisions,patterns,gotchas,corrections,tips}`, `archive/`)
2. Write 5 entry templates in `templates/` (decision.md, pattern.md, gotcha.md, correction.md, tip.md)
3. Write `knowledge-index.sh` - parses YAML frontmatter from all entries, builds `index.json`
4. Write `SKILL.md` for knowledge-manager skill
5. Write `/knowledge` command file (`.claude/commands/workspace-hub/knowledge.md`)
6. Seed 3-5 entries from known decisions:
   - ADR-001: Orchestrator pattern (from CLAUDE.md)
   - ADR-002: Markdown+YAML for knowledge entries (this design)
   - PAT-001: TDD before implementation (from rules/testing.md)
   - GOT-001: learned-patterns.json is empty (current state finding)
   - TIP-001: Use find-based repo discovery (from commit dca8925)

### Phase 2: Core Scripts (all bash, using `jq` for JSON ops)
1. `knowledge-capture.sh` - interactive capture with template selection + `--auto` mode for reflect
2. `knowledge-search.sh` - index search with `--query`, `--type`, `--category`, `--repo`, `--tag`, `--full-text` filters
3. `knowledge-stats.sh` - dashboard from index.json (entry counts, types, categories, avg confidence, stale count)
4. `knowledge-advise.sh` - relevance-ranked retrieval: tag overlap + category match + repo match + keyword search

### Phase 3: Automation Integration
1. `knowledge-review.sh` - confidence decay (`--decay`), interactive pruning (`--prune`), archive/revalidate
2. Modify `daily-reflect.sh` PHASE 4: add knowledge-capture call after create-skills.sh
3. Modify `daily-reflect.sh` checklist: add knowledge base health check item
4. Modify session-start-routine: add auto `/ka` check that surfaces top 3-5 relevant entries at session start

### Phase 4: Feedback Loop
1. `--auto` mode in knowledge-capture: patterns score 0.6-0.79 -> entries, correction chains > 3 -> gotchas
2. Access tracking: advise increments `access_count` in index.json for surfaced entries
3. Deduplication: title similarity check against existing index before creating new entries
4. Register all `/knowledge` subcommands in `.claude/docs/command-registry.md`
5. Test full loop: reflect -> capture -> advise -> access tracking -> decay -> review

## Critical Files to Modify

| File | Change |
|------|--------|
| `.claude/skills/coordination/workspace/knowledge-manager/SKILL.md` | **CREATE** - skill definition |
| `.claude/commands/workspace-hub/knowledge.md` | **CREATE** - slash command |
| `.claude/knowledge/index.json` | **CREATE** - machine index |
| `.claude/knowledge/entries/**/*.md` | **CREATE** - seed entries |
| `.claude/skills/coordination/workspace/knowledge-manager/scripts/*.sh` | **CREATE** - 6 scripts |
| `.claude/skills/coordination/workspace/knowledge-manager/templates/*.md` | **CREATE** - 5 templates |
| `.claude/skills/coordination/workspace/claude-reflect/scripts/daily-reflect.sh` | **MODIFY** - add knowledge capture + health check |
| `.claude/docs/command-registry.md` | **MODIFY** - register /knowledge commands |

## Verification

1. **Manual capture**: Run `/kc`, create a decision entry, verify it appears in index.json
2. **Search**: Run `/ks --tag orchestrator`, verify ADR-001 returned
3. **Advise**: Run `/ka "implement new feature in workspace-hub"`, verify relevant entries surfaced
4. **Stats**: Run `/knowledge stats`, verify counts match entries on disk
5. **Index rebuild**: Delete index.json, run `knowledge-index.sh`, verify index regenerated
6. **Decay**: Create entry with old date, run `knowledge-review.sh --decay`, verify confidence decreased
7. **Integration**: Run reflect daily script, verify knowledge capture step executes without error

## Relationship to Existing knowledge-base-system

The existing `.claude/skills/coordination/workspace/knowledge-base-system/SKILL.md` is aspirational (conceptual only, no implementation). The new knowledge-manager skill implements the concrete, actionable subset focused on session-to-session institutional learning. The existing skill can be updated to reference knowledge-manager as its implementation.
