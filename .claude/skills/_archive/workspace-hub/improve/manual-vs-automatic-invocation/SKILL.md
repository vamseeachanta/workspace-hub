---
name: improve-manual-vs-automatic-invocation
description: 'Sub-skill of improve: Manual vs Automatic Invocation.'
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Manual vs Automatic Invocation

## Manual vs Automatic Invocation


| Mode | Trigger | Engine | AI Quality |
|------|---------|--------|------------|
| Manual | `/improve` command | Claude session (full reasoning) | Highest — full context |
| Automatic | Stop hook at session exit | `improve.sh` + API calls | Good — structured prompts |
| Quick | Ctrl+C or `--quick` | `improve.sh` shell-only | None — metrics + logging only |
