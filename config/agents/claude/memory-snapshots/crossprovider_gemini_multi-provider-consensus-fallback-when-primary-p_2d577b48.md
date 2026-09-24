---
name: crossprovider gemini multi-provider-consensus-fallback-when-primary-p
description: Multi-provider consensus fallback when primary provider unavailable
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [multi-provider, workflow-resilience, consensus]
---

When primary review provider (Codex) returns NO_OUTPUT, implement 2-of-3 consensus fallback (Claude + Gemini must both APPROVE). Avoids hard blocks from quota issues while maintaining quality gates through distributed provider agreement.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
