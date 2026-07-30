---
name: crossprovider codex embedded-fixture-fallbacks-bypass-new-provenance
description: Embedded/fixture fallbacks bypass new provenance contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [architecture, provenance, fallback, data-quality]
---

Legacy embedded data paths (e.g., hard-coded conversion factors like tonnes*7.33 in production adapters) silently bypass new strict/default provenance gates introduced elsewhere in the codebase. These need explicit opt-in flags or hard-fail removal signals, not silent fallthrough.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
