---
name: crossprovider codex partial-fetch-reconcilers-must-fail-closed-not-s
description: Partial-fetch reconcilers must fail-closed, not silent-drop
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-safety, reconcilers, external-api]
---

When fetching external state (gh issue list --limit) and rebuilding cached board, if fetched count < cached count, assume truncation and abort unless explicitly overridden (--allow-shrink). Silent truncation loses data; fast-fail prevents corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
