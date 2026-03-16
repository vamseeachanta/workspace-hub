---
name: agent-usage-optimizer-step-2-display-quota-headroom
description: "Sub-skill of agent-usage-optimizer: Step 2 \u2014 Display Quota Headroom."
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Step 2 — Display Quota Headroom

## Step 2 — Display Quota Headroom


Render quota headroom table from the parsed values above.

```
Provider      │ % Remaining │ Status      │ Best for
──────────────┼─────────────┼─────────────┼──────────────────────────────────
Claude Opus   │  <CLAUDE>%  │  <STATUS>   │ Architecture, compound reasoning
Claude Sonnet │  <CLAUDE>%  │  <STATUS>   │ Standard tasks, code review
Claude Haiku  │  <CLAUDE>%  │  <STATUS>   │ Bulk ops, summaries (cost-save)
Codex         │  <CODEX>%   │  <STATUS>   │ Focused code gen, unit tests
Gemini        │  <GEMINI>%  │  <STATUS>   │ Long-context, large file review

Cache: <CACHE_TS>   Fresh: <CACHE_FRESH>
```

Status thresholds:
- >= 50%  → OK (green)
- 20-49%  → LOW (yellow) — prefer alternatives for heavy tasks
- < 20%   → CRITICAL (red) — steer away, flag before routing
