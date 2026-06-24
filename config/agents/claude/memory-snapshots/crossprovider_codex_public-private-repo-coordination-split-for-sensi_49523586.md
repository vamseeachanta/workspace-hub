---
name: crossprovider codex public-private-repo-coordination-split-for-sensi
description: Public/Private repo coordination split for sensitive data routing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [privacy-governance, multi-repo-coordination, issue-pattern]
---

When sensitive data must stay private, route detail-bearing work items to private repos (e.g., llm-wiki issues with path/label specifics) and keep public repos (e.g., workspace-hub) abstract with backlinks. Multiple independent searches converge on this split: workspace-hub #1579 (abstract audit/coordination) links to llm-wiki #122 (ingest umbrella) + child issues (#125, #129). This pattern is stable and repeatable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
