---
name: crossprovider gemini multi-machine-parity-automation-needs-explicit-f
description: Multi-machine parity automation needs explicit fallback evidence sources
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [evidence-collection, fallback-strategies, parity-reporting, fault-handling]
---

When primary evidence collection fails (SSH unavailable, non-responsive host), define a fallback chain: direct probes → bridge artifacts → cached state → explicit blocked status. Silent omission creates false parity; always report machine state explicitly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
