---
name: crossprovider codex dogleg-severity-and-minimum-curvature-legacy-haz
description: Dogleg severity and minimum curvature legacy hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [domain-specific, math, legacy-code]
---

Legacy trajectory math often uses dogleg where the RF formula requires interval dogleg, rounds intermediate angles before applying formulas, or substitutes fake values (e.g., 1° for zero-angle intervals). These errors compound. Require published worked examples and test against them before accepting legacy implementations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
