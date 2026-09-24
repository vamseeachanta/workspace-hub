---
name: crossprovider gemini utc-datetime-normalization-before-comparison
description: UTC datetime normalization before comparison
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [temporal-logic, robustness, timezone-handling]
---

Normalize timestamps to UTC datetime objects before comparison; never compare raw strings. Handles timezones, offsets, and format variations correctly. Parse failures are fail-closed (treat as new/enforce), rejecting non-ISO8601 strings.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
