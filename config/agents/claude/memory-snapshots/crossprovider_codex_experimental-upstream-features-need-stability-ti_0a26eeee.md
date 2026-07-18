---
name: crossprovider codex experimental-upstream-features-need-stability-ti
description: Experimental upstream features need stability tier validation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [upstream-tools, stability, api-contracts, vendor-risk]
---

When evaluating external tools for user-facing workflows (e.g., Codex CLI voice modes), check upstream repo for feature maturity stage. Features marked "experimental" or "under-development" have no stable API contract and may be removed/changed without warning. Before recommending to users, fall back to the stable documented alternative (e.g., Codex desktop app Ctrl+Shift+D instead of CLI RealtimeConversation).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
