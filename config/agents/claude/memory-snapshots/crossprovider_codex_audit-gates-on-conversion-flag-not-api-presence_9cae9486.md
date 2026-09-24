---
name: crossprovider codex audit-gates-on-conversion-flag-not-api-presence
description: Audit gates on conversion flag, not API presence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, audit, fail-closed, worldenergydata]
---

Entry validation gates on `accepted_for_conversion=false`, not on whether `api_gravity_deg` or `bbl_per_tonne` fields exist. Evidence-only entries with present API values must still fail strict audit. The loader checks the boolean flag first; field existence is decoupled from conversion eligibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
