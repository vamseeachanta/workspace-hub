---
name: crossprovider gemini cross-review-script-governance-unified-entry-poi
description: Cross-review script governance: unified entry point required
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [orchestration, governance, cross-review]
---

All orchestrators (Claude, Codex, Gemini) must route through `cross-review.sh all`, not call per-agent submit scripts directly. Direct `submit-to-claude.sh`, `submit-to-codex.sh`, or `submit-to-gemini.sh` invocations from orchestration code are classified as drift. The unified entry point provides consistent timeout, INVALID_OUTPUT detection, and 2-of-3 fallback consensus logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
