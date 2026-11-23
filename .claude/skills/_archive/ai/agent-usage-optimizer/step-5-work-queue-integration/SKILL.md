---
name: agent-usage-optimizer-step-5-work-queue-integration
description: "Sub-skill of agent-usage-optimizer: Step 5 \u2014 Work Queue Integration."
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Step 5 — Work Queue Integration

## Step 5 — Work Queue Integration


When showing recommendations before the plan gate in `/work run`:

```
=== Agent Allocation Check ===
Cache age: 12m  |  Claude: 73%  |  Codex: 100%  |  Gemini: 100%

Next 3 queue items:
  WRK-301 [Route B] → Claude Sonnet (primary),  Codex (secondary)
  WRK-302 [Route A] → Codex (primary),          Claude Haiku (secondary)
  WRK-303 [Route C] → Claude Opus (primary),    Claude Sonnet (secondary)

No providers critical. Proceeding to plan gate.
==============================
```

If any provider is critical (< 20%), show:

```
=== Agent Allocation Check ===
[CRITICAL] Claude quota at 14% — Routes B and C rerouted.

  WRK-301 [Route B] → Codex (primary),   Gemini (secondary)   [rerouted]
  WRK-302 [Route A] → Codex (primary),   Claude Haiku (sec)
  WRK-303 [Route C] → Gemini (primary),  Codex (secondary)    [rerouted]

Approve rerouted allocation? (y/n)
==============================
```
