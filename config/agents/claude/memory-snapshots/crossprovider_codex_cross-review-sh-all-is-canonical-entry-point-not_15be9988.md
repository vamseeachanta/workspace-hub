---
name: crossprovider codex cross-review-sh-all-is-canonical-entry-point-not
description: Cross-review.sh all is canonical entry point, not per-agent scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, cross-review, canonical-flow, script-hierarchy]
---

`cross-review.sh all` is the single cross-review entry point for ALL orchestrators. Direct calls to submit-to-claude.sh, submit-to-codex.sh, or submit-to-gemini.sh from orchestration code are workflow drift. The wrapper internally dispatches to per-agent scripts with unified timeout, INVALID_OUTPUT detection, and 2-of-3 fallback consensus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
