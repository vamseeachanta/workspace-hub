---
name: agent-router
description: Multi-dimensional task classifier and intelligent agent router for Claude, Codex, and Gemini CLI
version: 2.0.0
category: workspace-hub
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
  pre: |
    # Ensure jq is available
    command -v jq &>/dev/null || { echo "ERROR: jq required"; exit 1; }
requires: []
see_also: []
---

# Smart Agent Router

> Classify tasks across 10 dimensions and route to the optimal CLI agent (Claude/Codex/Gemini)

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

## Core Concepts

### 10-Dimension Scoring

Every task is scored across 10 dimensions, each returning -1.0 to +1.0:

| # | Dimension | Weight | Provider Signal |
|---|-----------|--------|-----------------|
| 1 | `reasoning_depth` | 20% | Claude |
| 2 | `code_density` | 18% | Codex |
| 3 | `architecture_scope` | 15% | Claude |
| 4 | `implementation_action` | 12% | Codex |
| 5 | `research_analysis` | 10% | Gemini |
| 6 | `task_complexity` | 8% | Tier signal |
| 7 | `agentic_markers` | 6% | Codex |
| 8 | `review_quality` | 5% | All (cross-review) |
| 9 | `data_processing` | 4% | Gemini |
| 10 | `simple_indicators` | 2% | Cheapest |

### Tier Classification

Weighted score maps to complexity tiers:
- **SIMPLE** (< 0.25): Quick queries, status checks, definitions
- **STANDARD** (0.25 - 0.50): Implementation, bug fixes, refactoring
- **COMPLEX** (0.50 - 0.75): Architecture, multi-file design, system patterns
- **REASONING** (> 0.75): Proofs, convergence analysis, deep trade-offs

### Routing Table

| Tier | Primary | Fallback 1 | Fallback 2 |
|------|---------|------------|------------|
| SIMPLE | Codex | Gemini | Claude |
| STANDARD | Codex | Claude | Gemini |
| COMPLEX | Claude | Gemini | Codex |
| REASONING | Claude | Gemini | Codex |

### Confidence & Auto-Routing

- **Confidence > 0.70**: Auto-route (high certainty in tier classification)
- **Confidence 0.50-0.70**: Suggest with explanation
- **Confidence < 0.50**: Present alternatives for user decision

### Per-Model Adaptive Routing (v2.0)

Each provider can have multiple model variants (e.g., Claude Opus vs Sonnet). The router tracks per-model EWMA ratings and selects the best model:

| Provider | Models | Cost Tier | Capability |
|----------|--------|-----------|------------|
| Claude | opus-4-6, sonnet-4-5 | premium/balanced | REASONING/COMPLEX |
| Codex | codex-cli | budget | STANDARD |
| Gemini | gemini-pro, gemini-flash | balanced/budget | COMPLEX/SIMPLE |

**EWMA Selection Logic**:
1. For each model in the provider, compute tier-specific EWMA (if >= 3 ratings)
2. Cold-start models use `default_priority / 25` as score
3. Add +0.3 capability bonus if model tier matches task tier
4. Pick highest scoring model; skip models with EWMA < 2.5

## Configuration

Config file: `config/agents/routing-config.yaml`
Model registry: `config/agents/model-registry.yaml`

```yaml
# routing-config.yaml
tiers:
  SIMPLE:
    primary: codex
    fallbacks: [gemini, claude]
  COMPLEX:
    primary: claude
    fallbacks: [gemini, codex]

models:
  registry: model-registry.yaml
  adaptive_routing:
    enabled: true

confidence:
  auto_route_threshold: 0.70
  suggest_threshold: 0.50

session_pinning:
  enabled: true
  ttl_minutes: 30
```

Provider profiles: `config/{claude,codex,gemini}_profile.json`

## Usage Examples

### Example 1: Classify a Task

```bash
$ ./scripts/coordination/routing/route.sh -q "What is a mooring line?"
{
  "classification": {
    "tier": "SIMPLE",
    "confidence": 0.92,
    "primary_provider": "codex"
  },
  "routing": {
    "provider": "codex",
    "auto_route": true
  }
}
```

### Example 2: Route a Work Queue Item

```bash
$ ./scripts/coordination/routing/route.sh --wrk WRK-110
Work item: WRK-110
Task: Implement fatigue analysis pipeline
--- Classifying task ---
Tier: STANDARD | Confidence: 0.65 | Classifier suggests: codex
Routed to: codex (Primary provider available)
```

### Example 3: Show Routing Stats

```bash
$ ./scripts/coordination/routing/route.sh --stats
=== Routing Decision History ===
Total decisions: 42

Per-provider counts:
  18 claude
  15 codex
   9 gemini

Per-tier counts:
  20 STANDARD
  12 COMPLEX
   7 SIMPLE
   3 REASONING
```

### Example 4: Rate an Agent (with model)

```bash
# Rate after task completion (auto-detects last routed provider + model)
$ ./scripts/coordination/routing/route.sh --rate 5

# Rate a specific provider
$ ./scripts/coordination/routing/route.sh --rate 4 claude
Rated claude/opus-4-6: 4/5

# Rate a specific model
$ ./scripts/coordination/routing/route.sh --rate 3 gemini/gemini-flash
Rated gemini/gemini-flash: 3/5
```

### Example 5: View Per-Model EWMA Stats

```bash
$ ./scripts/coordination/routing/route.sh --stats
...
=== Model Performance (EWMA) ===
  claude/opus-4-6:        4.200/5 (12 ratings)
  claude/sonnet-4-5:      3.800/5 (5 ratings)
  codex/codex-cli:        4.000/5 (8 ratings)
  gemini/gemini-pro:      3.500/5 (6 ratings)
  gemini/gemini-flash:    3.100/5 (3 ratings)

=== Per-Tier Model Performance ===
  COMPLEX: claude/opus-4-6 (4.500) gemini/gemini-pro (3.600)
  REASONING: claude/opus-4-6 (4.100)
```

## Execution Checklist

- [ ] Verify `jq` is installed
- [ ] Confirm at least one provider CLI is available
- [ ] Check provider profiles exist in `config/`
- [ ] Run `route.sh --config` to verify setup
- [ ] Test with a known task: `route.sh "what is Python?"`

## Integration Points

### Work Queue
- Route items during triage: `route.sh --wrk WRK-NNN`
- Tier maps to work queue routes: SIMPLE=A, STANDARD=B, COMPLEX=C

### Cross-Review Pipeline
- Tasks with high `review_quality` dimension trigger multi-agent review
- Integrates with `scripts/review/cross-review.sh`

### Session State
- Respects orchestrator lock from WRK-139 session-state.yaml
- Session pinning prevents agent switches mid-task (30min TTL)

### Audit Trail
- All decisions logged to `scripts/coordination/routing/logs/routing-decisions.jsonl`
- Use `--stats` to query aggregated history

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `jq is not installed` | Missing dependency | `apt install jq` or `brew install jq` |
| `No CLI providers detected` | No agent CLIs on PATH | Install claude, codex, or gemini CLI |
| `Work item not found` | Invalid WRK-NNN ID | Check `.claude/work-queue/` for valid items |
| Budget guardrail triggered | Daily spend limit hit | Increase budget in usage JSON or wait |

## Architecture

```
route.sh (entry point)
  ├── lib/usage_bootstrap.sh    # Zero-state usage file creation
  ├── lib/task_classifier.sh    # 10-dimension scoring engine
  ├── lib/tier_router.sh        # Tier-to-provider + model routing
  ├── lib/model_registry.sh     # Model registry + EWMA engine
  ├── lib/provider_filter.sh    # Rate limit / budget filtering
  ├── lib/cost_optimizer.sh     # Cost estimation
  ├── lib/agent_dispatcher.sh   # Model-aware agent dispatch
  └── lib/audit_logger.sh       # JSONL audit trail

config/agents/
  ├── routing-config.yaml       # Tier routing + model config
  └── model-registry.yaml       # Per-provider model variants + EWMA params
```

## Version History

- **2.0.0** (2026-02-14): Per-model EWMA tracking, adaptive routing, model-aware dispatch, enriched rating schema
- **1.0.0** (2026-02-14): Initial release -- 10-dimension classifier, tier routing, CLI entry point
