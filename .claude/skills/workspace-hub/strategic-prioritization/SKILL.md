---
name: strategic-prioritization
description: Rank WRK items by strategic value using hybrid WSJF+RICE scoring with track balance
invocation: /strategic-brief
---

# Strategic Prioritization

Deterministic scoring engine that ranks WRK items by strategic value.

## Quick Commands

```bash
# Full strategic brief (track balance + top items)
bash scripts/strategic/strategic-brief.sh --top 5

# Score and rank all pending WRKs (YAML output)
uv run --no-project python scripts/strategic/strategic-score.py --top 10

# Classify a single WRK
uv run --no-project python scripts/strategic/strategic-classify.py WRK-1200
```

## Scoring Model

- **RICE** (Reach×Impact×Confidence/Effort): items without deadlines/blockers
- **WSJF** (Cost-of-Delay/Job-Size): items with `blocked_by` or `deferred_to`
- **Track balance penalty**: over-served tracks penalized, under-served boosted
- **Roadmap bonus** (+15): items on critical engineering path
- **Enablement bonus** (+10/dep, cap 30): items that unblock others

## Track Targets

| Track | Target | Contains |
|-------|--------|----------|
| engineering | 50% | engineering, engineering-models, knowledge-domain |
| market | 20% | data, business, career, marketing, research |
| harness | 20% | harness, skills, ai-orchestration, tooling, automation |
| other | 10% | maintenance, platform, infrastructure, personal |

## Config

- Track mapping: `config/strategic-prioritization/track-mapping.yaml`
- Weights & targets: `config/strategic-prioritization/scoring-weights.yaml`
