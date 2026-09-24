---
name: crossprovider codex multi-provider-consensus-planning-with-degraded-
description: Multi-provider consensus planning with degraded-mode fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-provider, consensus-planning, degraded-mode]
---

When orchestrating independent planning passes across multiple providers (e.g., Claude, Codex, Gemini), the workflow can degrade to fewer providers if one is unavailable, but must record which providers contributed via explicit metadata. Consensus (combining and rating plans) applies only when all intended providers contribute; degraded mode is tracked separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
