---
name: crossprovider codex cross-review-script-routing-is-canonical-via-cro
description: Cross-review script routing is canonical via cross-review.sh all
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, architecture, cross-review]
---

Governance rule: all orchestrators (Claude, Codex, Gemini) MUST route cross-review through `cross-review.sh all`, never call per-agent submit scripts directly from orchestration code. Direct calls are classified as drift and create inconsistent output. The wrapper internally dispatches to `submit-to-claude.sh`, `submit-to-codex.sh`, `submit-to-gemini.sh` with unified timeout/INVALID_OUTPUT/2-of-3 fallback logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
