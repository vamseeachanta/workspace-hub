---
name: crossprovider codex architectural-decisions-propagate-with-redaction
description: Architectural decisions propagate with redaction splits across repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, redaction, multi-tier-design]
---

When an architectural contract (like alias indirection retirement in #581) changes mid-cycle, dependent plans must update and redact differently for public vs private tiers. The public artifact uses neutral tokens; physical hostnames, IPs, and account principals live only in private appendices, referenced by path never by value. Violating the redaction scope is a security/privacy defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
