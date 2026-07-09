---
name: crossprovider codex provider-harness-parity-requires-freshness-testi
description: Provider harness parity requires freshness testing, not just presence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [multi-provider, memory-management, test-assertions]
---

Memory slices for multi-provider harnesses (Codex/Gemini vs Claude) must assert freshness and critical-inclusion thresholds, not just non-empty. A 128-hour-old memory slice passes "non-empty" tests but is stale for runtime decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
