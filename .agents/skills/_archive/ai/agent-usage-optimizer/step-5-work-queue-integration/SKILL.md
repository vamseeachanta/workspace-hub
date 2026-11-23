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
Cache age: 12m  |  Codex: 73%  |  Codex: 100%  |  Gemini: 100%

Next 3 queue items:
  WRK-301 [Route B] → Codex Sonnet (primary),  Codex (secondary)
  WRK-302 [Route A] → Codex (primary),          Codex Haiku (secondary)
  WRK-303 [Route C] → Codex Opus (primary),    Codex Sonnet (secondary)

No providers critical. Proceeding to plan gate.
==============================
```

If any provider is critical (< 20%), show:

```
=== Agent Allocation Check ===
[CRITICAL] Codex quota at 14% — Routes B and C rerouted.

  WRK-301 [Route B] → Codex (primary),   Gemini (secondary)   [rerouted]
  WRK-302 [Route A] → Codex (primary),   Codex Haiku (sec)
  WRK-303 [Route C] → Gemini (primary),  Codex (secondary)    [rerouted]

Approve rerouted allocation? (y/n)
==============================
```
