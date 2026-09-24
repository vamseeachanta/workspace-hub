---
name: crossprovider codex memory-eviction-rule-ordering-prioritizes-correc
description: Memory eviction rule ordering prioritizes correctness over dedup efficiency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [memory-governance, eviction-policy, rule-hierarchy, marker-scope]
---

Order eviction rules as: (1) done-WRK expiry, (2) path staleness, (3) command staleness (opt-in), (4) semantic dedup (≥90% token overlap), (5) age-based trim. The `# keep` marker exempts only rules 4-5 (dedup and trim), not rules 1-2 (correctness). This ensures stale paths/done-WRKs are removed regardless of marker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
