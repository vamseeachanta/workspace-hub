---
name: crossprovider gemini mandatory-legal-sanity-scan-gate-must-be-planned
description: Mandatory legal sanity scan gate must be planned explicitly
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [legal, security, gates]
---

GEMINI.md contract requires all code to pass `scripts/legal/legal-sanity-scan.sh` before merge. This gate is easy to omit from implementation plans and causes review rejections. Explicitly include it in Phase 1 planning for any feature touching code.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
