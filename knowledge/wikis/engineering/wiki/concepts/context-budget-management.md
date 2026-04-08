---
title: "Context Budget Management"
tags: [agents, context, tokens, quota, efficiency]
sources:
  - ai-orchestration-memory
added: 2026-04-08
last_updated: 2026-04-08
---

# Context Budget Management

Managing the token cost and context window budget across AI agent sessions. Token efficiency is a binding constraint -- the Sonnet-only quota often hits 100% before the all-models cap.

## Model Cost & Routing

| Model | Input/Output per M tokens | Best Use |
|-------|--------------------------|----------|
| Opus 4.6 | $5/$25 | Complex architecture, 1M-context analysis |
| Sonnet 4.6 | $3/$15 | Default for most work (more concise) |

**Key insight**: Opus is ~5x more verbose, creating HIGH quota risk. Use Sonnet unless Opus's depth is required.

## CLI vs MCP Token Cost

CLI tools use significantly fewer tokens than MCP server equivalents -- Playwright CLI uses ~90K fewer tokens than MCP browser automation.

**Rule**: When both CLI and MCP options exist, prefer CLI for token efficiency.

## Quota Monitoring

- OAuth API: `GET https://api.anthropic.com/api/oauth/usage`
- Tracks: `seven_day.utilization`, `seven_day_sonnet.utilization`, `five_hour.utilization`
- Sonnet-only quota is the real binding constraint

## Budget Thresholds

- 35% context usage: consider delegation to subagents
- 25% context remaining: start wrapping up or compressing

## Cross-References

- **Related concept**: [[orchestrator-worker-separation]]
- **Related concept**: [[agent-delegation]]
- **Related concept**: [[multi-agent-parity]]
