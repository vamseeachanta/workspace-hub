---
name: crossprovider gemini github-first-numbering-via-offline-fallback-elim
description: GitHub-first numbering via offline fallback eliminates dual-ID confusion
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [id-scheme, github-integration, offline-handling]
---

Make GitHub issue number the WRK ID (WRK-NNN where NNN = issue #). For offline capture, use temporary WRK-LOCAL-YYYYMMDD-HHMMSS, then promote to real ID when online. This eliminates the dual-number confusion that occurs during Stages 0-3. 78% of items already had GitHub issues; this unifies them.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
