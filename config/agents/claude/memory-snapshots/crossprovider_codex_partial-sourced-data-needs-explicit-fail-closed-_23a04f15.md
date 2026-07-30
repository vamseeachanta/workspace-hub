---
name: crossprovider codex partial-sourced-data-needs-explicit-fail-closed-
description: Partial sourced data needs explicit fail-closed design
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-sourcing, validation, fallback-design]
---

When enrichment data (e.g., crude API/density by field) is partially available across domains, audit coverage first, then design explicit fail-closed handling (reject missing, surface gaps as errors) rather than silent defaulting. Incomplete data silently filled with defaults hides quality gaps in downstream analytics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
