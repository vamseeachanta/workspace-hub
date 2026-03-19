---
name: agent-usage-optimizer-baseline-route-defaults
description: 'Sub-skill of agent-usage-optimizer: Baseline Route Mapping (quota-agnostic
  defaults) (+1).'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Baseline Route Mapping (quota-agnostic defaults) (+1)

## Baseline Route Mapping (quota-agnostic defaults)


| Route | Complexity | Primary         | Secondary        | Use For                              |
|-------|-----------|-----------------|------------------|--------------------------------------|
| A     | Simple    | Codex           | Claude Haiku     | Focused code gen, unit tests, debug  |
| B     | Standard  | Claude Sonnet   | Codex            | Reviews, docs, standard features     |
| C     | Compound  | Claude Opus     | Claude Sonnet    | Architecture, multi-file refactors   |
| —     | Bulk      | Claude Haiku    | Gemini           | Summarisation, data processing       |
| —     | Long-ctx  | Gemini          | Claude Sonnet    | Large file review, cross-repo scan   |


## Quota-Adjusted Routing


Apply these overrides on top of baseline when quota thresholds are triggered:

```
IF claude_pct < 20%:
  Route B primary → Codex  (demote Sonnet; fallback secondary = Gemini)
  Route C primary → Gemini (demote Opus;   fallback secondary = Codex)
  Emit CRITICAL warning before plan gate

ELIF claude_pct < 50%:
  Route C primary remains Opus  (preserve for compound/architecture only)
  Route B primary → Codex       (save Sonnet for Route C overflow)
  Emit LOW warning before plan gate

ELSE (claude_pct >= 50%):
  Use baseline route mapping above (Claude is the preferred quality provider)

ALWAYS:
  Bulk operations → Claude Haiku regardless of quota level
  Long-context    → Gemini first when file count > 10 or token estimate > 50K
```
