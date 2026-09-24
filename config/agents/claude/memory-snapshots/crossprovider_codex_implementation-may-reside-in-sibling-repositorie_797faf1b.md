---
name: crossprovider codex implementation-may-reside-in-sibling-repositorie
description: Implementation may reside in sibling repositories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monorepo, architecture, sibling-repos]
---

In workspace-hub ecosystem, an issue may live in workspace-hub while its implementation lives in a sibling repo (e.g., aceengineer-website). Validate by checking out the sibling branch directly and inspecting its diff/state; do not assume local changes are the canonical implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
