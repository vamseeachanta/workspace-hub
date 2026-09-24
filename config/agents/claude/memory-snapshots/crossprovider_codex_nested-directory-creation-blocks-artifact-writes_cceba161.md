---
name: crossprovider codex nested-directory-creation-blocks-artifact-writes
description: Nested directory creation blocks artifact writes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-writes, directory-structure, shell-unavailability]
---

When an artifact path includes missing parent directories and the local shell is unavailable (or blocked by permissions), both direct patch tools and GitHub write fallbacks fail silently without creating the directories. Avoid deeply nested new paths; prefer artifacts in pre-existing directories or use flat paths within `docs/session-handoffs/` or similar established structures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
