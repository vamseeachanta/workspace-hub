---
name: crossprovider gemini log-gate-legacy-exemption-via-creation-timestamp
description: Log gate legacy exemption via creation timestamp
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [gates, backward-compat, orchestration]
---

When enforcing mandatory logging gates retroactively across mixed-age work items, discriminate by parsing WRK creation_timestamp from frontmatter and comparing against a cutoff date constant (e.g., LOG_GATE_SINCE = 2026-03-09). Skip enforcement for items created before the cutoff; require logs for newer items. Avoids blanket exemptions while enabling gradual migration without breaking pre-existing work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
