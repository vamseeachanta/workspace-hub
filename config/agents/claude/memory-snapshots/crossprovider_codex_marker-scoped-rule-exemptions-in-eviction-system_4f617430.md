---
name: crossprovider codex marker-scoped-rule-exemptions-in-eviction-system
description: Marker-scoped rule exemptions in eviction systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [memory-management, rule-design, eviction, graduated-enforcement]
---

Use markers (e.g., `# keep`) that selectively exempt rules by phase — the marker exempts from later rules (dedup, trim-to-limit) but NOT earlier ones (expiry, path staleness). This allows both selective preservation and gradual cleanup within the same framework.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
