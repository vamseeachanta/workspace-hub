---
name: crossprovider codex client-identifier-exposure-risk-in-architecture-
description: Client-identifier exposure risk in architecture documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, documentation, data-isolation, legal-scanning]
---

Architecture and data-boundary documentation risks leaking client names, project identifiers, and private paths even in examples. Use neutral placeholders and run legal-sanity-scan + forbidden-literal scans on all new public artifacts—issue #2727 R1 blocked on MAJOR finding of exposed client-specific content, requiring scrub and rescan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
