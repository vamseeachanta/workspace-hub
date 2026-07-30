---
name: crossprovider codex crosswalk-validation-specific-evidence-locators-
description: Crosswalk validation: specific evidence locators, all-row fingerprints, pinned units
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [data-validation, cost-analysis, testing]
---

Three recurring cost-data defects: (1) blank evidence locators hide source cell references—require exact Sheet/range citations; (2) last-write-wins fingerprinting masks row-level corruption—validate every row against its hash; (3) unit semantics (USD vs USD MM, per-well, per-day) must be asserted per allowlisted cell in tests, not just checked for presence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
