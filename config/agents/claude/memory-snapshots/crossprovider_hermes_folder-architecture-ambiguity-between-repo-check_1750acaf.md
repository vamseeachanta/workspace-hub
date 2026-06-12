---
name: crossprovider hermes folder-architecture-ambiguity-between-repo-check
description: Folder architecture ambiguity between repo/checkout/runtime/sibling-repo prevents agent dispatch readiness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, architecture, agent-readiness, hermes]
---

Confusion between `/workspace-hub` repo subfolders, `/mnt/local-analysis/workspace-hub` machine checkout, `~/.hermes/.codex/.gemini` runtime dirs, and sibling tier-1 repos (digitalmodel, etc.) makes it hard to write clear handoff specs for parallel agents. Clarification issue #2758 must be resolved before dispatch lane readiness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
