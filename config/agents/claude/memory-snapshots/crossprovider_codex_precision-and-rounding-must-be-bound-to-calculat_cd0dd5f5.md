---
name: crossprovider codex precision-and-rounding-must-be-bound-to-calculat
description: Precision and rounding must be bound to calculations, not rendering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, reporting, reproducibility]
---

Hardcoded formatting rules in HTML rendering (e.g., `.1e` vs `.3e` rules in Python) drift from bound calculation records. Encode field-specific precision/rounding in calculation metadata and render all numeric output directly from those bound inputs, asserting rendered values match calculation outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
