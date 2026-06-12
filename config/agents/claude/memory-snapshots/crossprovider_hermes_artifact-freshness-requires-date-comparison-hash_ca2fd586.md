---
name: crossprovider hermes artifact-freshness-requires-date-comparison-hash
description: Artifact freshness requires date comparison + hash, not lexicographic filename sort
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-staleness, freshness-detection, timestamp-logic]
---

Lexicographic filename sorting (`max(glob('report-*'))`) for freshness fails if older artifact directories have newer report files added later. Example: 2026-05-17 report + 2026-05-18 report added to same dir picks 05-18 lexicographically even if 05-17 is stale. **Why:** timestamps decay; filename alone doesn't guarantee freshness. **How to apply:** use `max(..., key=lambda p: p.stat().st_mtime)` for freshness; add explicit date-in-filename check (e.g., assert `report-YYYY-MM-DD` matches artifact dir date); include content-hash in validator.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
