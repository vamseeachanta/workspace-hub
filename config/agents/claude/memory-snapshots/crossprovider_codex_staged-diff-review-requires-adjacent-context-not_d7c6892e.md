---
name: crossprovider codex staged-diff-review-requires-adjacent-context-not
description: Staged diff review requires adjacent context, not just the diff itself
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, scope, api, standards]
---

When reviewing a new standards helper module, scope collisions, export patterns, and public API hazards often lie outside the staged diff (e.g., package-level __init__.py exports, existing enums in other modules). Read nearby context to spot false traceability or API clashes before approving.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
