---
name: agent-router
description: Multi-dimensional task classifier and intelligent agent router for Claude,
  Codex, and Gemini CLI
version: 2.0.0
category: coordination
type: hybrid
capabilities:
- multi_dimension_task_classification
- tier_based_routing
- provider_availability_check
- confidence_calibrated_routing
- session_pinning
- audit_trail
- per_model_ewma_tracking
- adaptive_model_selection
tools:
- Task
- Bash
related_skills:
- agent-orchestration
- work-queue
- compliance-check
hooks:
  pre: '# Ensure jq is available

    command -v jq &>/dev/null || { echo "ERROR: jq required"; exit 1; }

    '
requires: []
see_also:
- agent-router-10-dimension-scoring
- agent-router-configuration
- agent-router-example-1-classify-a-task
- agent-router-work-queue
- agent-router-architecture
tags: []
---

# Agent Router

## Quick Start

```bash
# Classify and recommend
./scripts/coordination/routing/route.sh "implement unit tests for hull_loader"

# Classify and auto-execute
./scripts/coordination/routing/route.sh --execute "fix the broken import in parser.py"

# Route a work queue item
./scripts/coordination/routing/route.sh --wrk WRK-110

# Rate an agent after task completion (1-5 scale)
./scripts/coordination/routing/route.sh --rate 4 claude

# Rate a specific model (provider/model syntax)
./scripts/coordination/routing/route.sh --rate 4 claude/sonnet-4-5

# Show routing stats with per-model EWMA breakdown
./scripts/coordination/routing/route.sh --stats

# Show config with model registry
./scripts/coordination/routing/route.sh --config
```

## When to Use

- Deciding which AI agent (Claude/Codex/Gemini) to assign to a task
- Triaging work queue items by complexity tier
- Understanding why a particular agent was selected for a task
- Reviewing routing decision history and agent utilization patterns
- Automating agent dispatch in multi-step workflows

## Prerequisites

- `jq` installed (JSON processing)
- At least one CLI agent available: `claude`, `codex`, or `gemini`
- Provider profiles configured in `config/*.json`

## Version History

- **2.0.0** (2026-02-14): Per-model EWMA tracking, adaptive routing, model-aware dispatch, enriched rating schema
- **1.0.0** (2026-02-14): Initial release -- 10-dimension classifier, tier routing, CLI entry point

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [10-Dimension Scoring (+4)](10-dimension-scoring/SKILL.md)
- [Configuration](configuration/SKILL.md)
- [Example 1: Classify a Task (+4)](example-1-classify-a-task/SKILL.md)
- [Work Queue (+3)](work-queue/SKILL.md)
- [Architecture](architecture/SKILL.md)
