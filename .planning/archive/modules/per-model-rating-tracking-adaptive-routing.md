# Per-Model Rating Tracking & Adaptive Routing

---
title: Per-Model Rating Tracking & Adaptive Routing
description: Expand model roster, track per-model EWMA ratings, and auto-shift routing based on performance
version: 2.0.0
module: coordination/orchestration
session:
  id: peppy-wishing-ritchie
  agent: claude-opus-4-6
review: pending
---

## Context

The Smart Agent Router (v1.0) routes tasks to 3 providers (claude/codex/gemini) but:
1. Each provider is treated as a **single model** — no Claude Sonnet vs Opus, no Gemini Flash vs Pro
2. `--rate` logs scores but they **never influence routing** — pure dead-end data
3. No mechanism to **automatically deprioritize** poorly-performing models or **promote** strong ones

**Goal**: Expand to per-model tracking with EWMA-based adaptive routing so the system learns which models perform best for which task types and auto-shifts traffic accordingly.

## Approach

### Phase A: Model Registry + EWMA Engine

#### A.1 New: `config/agents/model-registry.yaml` (~60 lines)

Declares model variants per provider with cost tier, capability tier, and default priority:

```yaml
version: 1.0.0
ewma:
  alpha: 0.3          # Recent ratings weighted 30%
  min_ratings: 3       # Cold-start protection
  poor_threshold: 2.5  # Below this → try next model

providers:
  claude:
    default_model: opus-4-6
    models:
      opus-4-6:
        display_name: "Claude Opus 4.6"
        cost_tier: premium
        capability_tier: REASONING
        default_priority: 100
      sonnet-4-5:
        display_name: "Claude Sonnet 4.5"
        cost_tier: balanced
        capability_tier: COMPLEX
        default_priority: 80
  codex:
    default_model: codex-cli
    models:
      codex-cli:
        display_name: "Codex CLI"
        cost_tier: budget
        capability_tier: STANDARD
        default_priority: 90
  gemini:
    default_model: gemini-pro
    models:
      gemini-pro:
        display_name: "Gemini Pro"
        cost_tier: balanced
        capability_tier: COMPLEX
        default_priority: 90
      gemini-flash:
        display_name: "Gemini Flash"
        cost_tier: budget
        capability_tier: SIMPLE
        default_priority: 70
```

#### A.2 New: `scripts/coordination/routing/lib/model_registry.sh` (~200 lines)

Core library with these functions:

| Function | Purpose |
|----------|---------|
| `_load_model_registry()` | Parse YAML into bash arrays via `awk` state machine |
| `_compute_ewma(model, [tier])` | Scan `agent-ratings.jsonl`, compute EWMA via `awk` |
| `_count_ratings(model, [tier])` | Count ratings for cold-start check |
| `select_model_for_provider(provider, tier)` | Pick best model: EWMA if sufficient data, else default_priority |
| `get_model_display_name(model)` | Lookup display name |

**EWMA formula**: `ewma_new = alpha * rating + (1 - alpha) * ewma_prev` (seed = 3.0)

**Selection logic**:
1. Get all models for provider from registry
2. For each model, compute tier-specific EWMA (if >= min_ratings) or use default_priority/25
3. Add capability-tier bonus (+0.3 if model's capability_tier matches task tier)
4. Pick highest scoring model
5. If best EWMA < poor_threshold (2.5), skip to next model

### Phase B: Enriched Rating Schema

#### B.1 Edit: `route.sh` `--rate` handler

New JSONL schema for `agent-ratings.jsonl`:

```json
{
  "timestamp": "2026-02-14T10:00:00Z",
  "provider": "claude",
  "model": "opus-4-6",
  "score": 4,
  "tier": "COMPLEX",
  "task_hash": "a7b3c1"
}
```

- `model` auto-detected from last routing decision's audit log
- `tier` captured from last classification
- `task_hash` = first 6 chars of `echo "$TASK" | md5sum` (for audit join)
- Accepts `--rate <1-5> [provider/model]` syntax (e.g., `--rate 4 claude/sonnet-4-5`)
- Old entries without `model` field remain valid (ignored in per-model EWMA)

### Phase C: Integrate Model Selection into Pipeline

#### C.1 Edit: `lib/tier_router.sh` — `route_by_tier()` (+15 lines)

After provider is chosen, call `select_model_for_provider "$chosen" "$tier"`. Add `model` and `model_selection` to output JSON.

#### C.2 Edit: `route.sh` pipeline section (+10 lines)

Extract `selected_model` and `model_ewma` from routing JSON. Include in final output and audit log.

### Phase D: Model-Aware Dispatch

#### D.1 Edit: `lib/agent_dispatcher.sh` — `get_dispatch_command()` (+10 lines)

Accept `$4` = model. Map model variants to CLI flags:
- `claude/sonnet-4-5` → `claude --model claude-sonnet-4-5-20250514 -p "$task"`
- `claude/opus-4-6` → `claude -p "$task"` (default)
- `gemini/gemini-flash` → `gemini --model gemini-2.5-flash -p ... -y`
- `gemini/gemini-pro` → `gemini -p ... -y` (default)
- `codex/codex-cli` → `echo "$task" | codex exec -` (unchanged)

### Phase E: Stats & Config Updates

#### E.1 Edit: `route.sh` `--stats` (+15 lines)

Add per-model EWMA breakdown:
```
=== Model Performance (EWMA) ===
  claude/opus-4-6:    4.2/5 (12 ratings)
  claude/sonnet-4-5:  3.8/5 (5 ratings)
  codex/codex-cli:    4.0/5 (8 ratings)
  gemini/gemini-pro:  3.5/5 (6 ratings)
  gemini/gemini-flash: 3.1/5 (3 ratings)

=== Per-Tier Model Performance ===
  SIMPLE:    codex/codex-cli (4.3), gemini/gemini-flash (3.2)
  STANDARD:  codex/codex-cli (4.0), claude/sonnet-4-5 (3.8)
  COMPLEX:   claude/opus-4-6 (4.5), gemini/gemini-pro (3.6)
  REASONING: claude/opus-4-6 (4.1)
```

#### E.2 Edit: `route.sh` `--config` (+8 lines)

Show model registry under each provider:
```
Provider Status:
  claude: AVAILABLE
    Models: opus-4-6 (priority=100, EWMA=4.2), sonnet-4-5 (priority=80, EWMA=3.8)
  codex: AVAILABLE
    Models: codex-cli (priority=90, EWMA=4.0)
  gemini: AVAILABLE
    Models: gemini-pro (priority=90, EWMA=3.5), gemini-flash (priority=70, EWMA=3.1)
```

#### E.3 Rewrite: `optimize_weights.sh` (~60 lines)

Replace placeholder with actual EWMA reporting:
- Show effective routing table after adaptive adjustments
- Flag models below poor_threshold
- Suggest tier-specific model swaps

#### E.4 Edit: `routing-config.yaml` (+10 lines)

Add model section:
```yaml
models:
  registry: model-registry.yaml
  adaptive_routing:
    enabled: true
```

### Phase F: SKILL.md + Deprecation

#### F.1 Edit: `.claude/skills/.../agent-router/SKILL.md`

Add model-aware docs: `--rate` with model syntax, `--stats` model EWMA display, model registry concept.

#### F.2 Edit: `feedback.sh` (+5 lines)

Add deprecation notice pointing to `route.sh --rate`.

## Files Summary

| File | Action | Est. Lines |
|------|--------|------------|
| `config/agents/model-registry.yaml` | New | 60 |
| `scripts/coordination/routing/lib/model_registry.sh` | New | 200 |
| `scripts/coordination/routing/route.sh` | Edit | +44 → 295 |
| `scripts/coordination/routing/lib/tier_router.sh` | Edit | +15 → 135 |
| `scripts/coordination/routing/lib/agent_dispatcher.sh` | Edit | +12 → 95 |
| `scripts/coordination/routing/optimize_weights.sh` | Rewrite | 60 |
| `scripts/coordination/routing/feedback.sh` | Edit | +5 → 42 |
| `config/agents/routing-config.yaml` | Edit | +10 → 78 |
| `.claude/skills/.../agent-router/SKILL.md` | Edit | +20 → 268 |
| **Total new/changed** | | **~970** |

## Verification

1. **EWMA math**: Feed known ratings `[4,3,2,3,5]`, verify EWMA = 3.525 (hand-calculated)
2. **Cold start**: Empty ratings → default_priority model returned
3. **Poor model fallback**: Push EWMA below 2.5 → next model selected
4. **Backward compat**: Old rating entries (no `model` field) → no crash
5. **End-to-end**: `route.sh "design architecture"` → JSON includes `model: opus-4-6`
6. **Rate enrichment**: `route.sh --rate 4` → JSONL has model, tier, task_hash
7. **Stats display**: `route.sh --stats` → shows per-model EWMA
8. **Syntax check**: `bash -n` on all modified `.sh` files
9. **No hardcoded paths**: `grep -r '/mnt/' scripts/coordination/routing/` → empty

## EWMA Worked Example

```
Ratings for claude/opus-4-6 on COMPLEX: [4, 3, 2, 3, 5]
Alpha = 0.3, Seed = 3.0

Rate 4: ewma = 0.3*4 + 0.7*3.0  = 3.30
Rate 3: ewma = 0.3*3 + 0.7*3.3  = 3.21
Rate 2: ewma = 0.3*2 + 0.7*3.21 = 2.85  ← approaching poor threshold
Rate 3: ewma = 0.3*3 + 0.7*2.85 = 2.89  ← recovering
Rate 5: ewma = 0.3*5 + 0.7*2.89 = 3.52  ← recovered

Two bad ratings in a row would cross 2.5 → triggers fallback to sonnet-4-5
```
