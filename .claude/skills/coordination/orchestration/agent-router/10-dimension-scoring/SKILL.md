---
name: agent-router-10-dimension-scoring
description: 'Sub-skill of agent-router: 10-Dimension Scoring (+4).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 10-Dimension Scoring (+4)

## 10-Dimension Scoring


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

## Tier Classification


Weighted score maps to complexity tiers:
- **SIMPLE** (< 0.25): Quick queries, status checks, definitions
- **STANDARD** (0.25 - 0.50): Implementation, bug fixes, refactoring
- **COMPLEX** (0.50 - 0.75): Architecture, multi-file design, system patterns
- **REASONING** (> 0.75): Proofs, convergence analysis, deep trade-offs

## Routing Table


| Tier | Primary | Fallback 1 | Fallback 2 |
|------|---------|------------|------------|
| SIMPLE | Codex | Gemini | Claude |
| STANDARD | Codex | Claude | Gemini |
| COMPLEX | Claude | Gemini | Codex |
| REASONING | Claude | Gemini | Codex |

## Confidence & Auto-Routing


- **Confidence > 0.70**: Auto-route (high certainty in tier classification)
- **Confidence 0.50-0.70**: Suggest with explanation
- **Confidence < 0.50**: Present alternatives for user decision

## Per-Model Adaptive Routing (v2.0)


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
