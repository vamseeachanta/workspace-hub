---
name: agent-usage-optimizer
version: 1.0.0
category: ai
description: Reads quota state and recommends optimal Claude/Codex/Gemini allocation
  per task
capabilities:
- quota-aware routing
- route-mapping
- headroom display
requires:
- ~/.cache/agent-quota.json
see_also:
- agent-usage-optimizer-usage
- agent-usage-optimizer-what-it-does
- agent-usage-optimizer-step-1-read-and-validate-quota-cache
- agent-usage-optimizer-step-2-display-quota-headroom
- agent-usage-optimizer-baseline-route-mapping-quota-agnostic-defaults
- agent-usage-optimizer-keyword-route-classification
- agent-usage-optimizer-step-5-work-queue-integration
- agent-usage-optimizer-provider-capability-reference
- agent-usage-optimizer-hours-to-reset-estimation
- agent-usage-optimizer-complexity-tier-model-mapping
tags: []
---

# Agent Usage Optimizer

## When to Use

- Before starting a work session with 3+ queued WRK items
- When Claude quota is approaching a constraint (< 50% remaining)
- When routing a task and unsure which provider fits best
- After `/session-start` to set provider allocation for the session

## Sub-Skills

- [Usage](usage/SKILL.md)
- [What It Does](what-it-does/SKILL.md)
- [Step 1 — Read and Validate Quota Cache](step-1-read-and-validate-quota-cache/SKILL.md)
- [Step 2 — Display Quota Headroom](step-2-display-quota-headroom/SKILL.md)
- [Baseline Route Mapping (quota-agnostic defaults) (+1)](baseline-route-mapping-quota-agnostic-defaults/SKILL.md)
- [Keyword → Route classification](keyword-route-classification/SKILL.md)
- [Step 5 — Work Queue Integration](step-5-work-queue-integration/SKILL.md)
- [Provider Capability Reference](provider-capability-reference/SKILL.md)
- [Hours-to-Reset Estimation](hours-to-reset-estimation/SKILL.md)
- [Complexity Tier → Model Mapping](complexity-tier-model-mapping/SKILL.md)
