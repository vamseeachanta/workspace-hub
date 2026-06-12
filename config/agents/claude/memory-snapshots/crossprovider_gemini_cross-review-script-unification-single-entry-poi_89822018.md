---
name: crossprovider gemini cross-review-script-unification-single-entry-poi
description: Cross-review script unification: single entry point for all orchestrators
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [orchestrator-governance, script-architecture, cross-review]
---

`cross-review.sh all` is the canonical cross-review dispatcher for Claude, Codex, and Gemini. Direct per-agent calls (submit-to-claude.sh, submit-to-codex.sh, submit-to-gemini.sh) are drift; orchestrators must route through the unified wrapper. Internal dispatch with 2-of-3 fallback consensus, not external orchestrator calls.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
