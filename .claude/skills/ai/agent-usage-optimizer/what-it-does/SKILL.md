---
name: agent-usage-optimizer-what-it-does
description: 'Sub-skill of agent-usage-optimizer: What It Does.'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# What It Does

## What It Does


1. Reads `~/.cache/agent-quota.json` — no external calls if cache age < 1 hour
2. Displays quota headroom per provider: % remaining + estimated hours to daily reset
3. Applies routing rules based on quota state and task complexity
4. Recommends primary + secondary provider with rationale
5. Flags any provider critically low (< 20% remaining)
6. Shows as pre-gate output before the plan gate when used with `/work run`

---
