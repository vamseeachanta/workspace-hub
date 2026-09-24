---
name: crossprovider codex temperature-based-selection-filter-envelope-firs
description: Temperature-based selection: filter envelope first, then choose candidate, not select-then-validate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [selection-logic, temperature, algorithm, edge-case]
---

When selecting coatings by temperature, identify which candidates are valid for that temperature range first (envelope filtering), then choose among valid candidates. Selecting a candidate and then validating its envelope can fail on edge cases (e.g., selecting FBE at 105°C, then failing FBE's 100°C limit). Envelope filtering is primary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
