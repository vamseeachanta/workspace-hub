---
name: crossprovider codex configuration-defaults-need-empirical-grounding
description: Configuration defaults need empirical grounding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration, thresholds, production]
---

Thresholds and defaults in validators, gates, or filters require (a) measurement from live data, (b) explicit formula/principle (e.g., '0.80 × observed minimum'), and (c) grep of all production callers to confirm the default is actually used. Round-number guesses and aspirational targets without measurement are MAJOR defects masquerading as simplicity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
