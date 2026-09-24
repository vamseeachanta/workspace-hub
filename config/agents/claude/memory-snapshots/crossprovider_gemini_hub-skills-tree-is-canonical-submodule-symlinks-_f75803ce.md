---
name: crossprovider gemini hub-skills-tree-is-canonical-submodule-symlinks-
description: Hub skills tree is canonical; submodule symlinks enforce single source of truth
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workspace-structure, invariants, governance, symlink-patterns]
---

`.claude/skills/` at workspace-hub root is the canonical skill source; all submodules use symlinks (e.g., `.codex/skills → ../../.claude/skills`) to the hub. This constraint is fragile and requires explicit invariant documentation. Changes to hub/submodule directory structure require WRK items; propagation scripts enforce the symlink relationship across the ecosystem.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
