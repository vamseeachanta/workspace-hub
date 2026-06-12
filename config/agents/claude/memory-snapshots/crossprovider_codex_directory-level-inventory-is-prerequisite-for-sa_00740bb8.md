---
name: crossprovider codex directory-level-inventory-is-prerequisite-for-sa
description: Directory-level inventory is prerequisite for safe deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [deletion-safety, hygiene, inventory]
---

Before deleting a skill directory, perform full directory inventory to catch auxiliary files (references/, examples/, etc.) that might be missed by SKILL.md-only assumptions. Missing this step means orphaning docs/references and breaking inheritance contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
