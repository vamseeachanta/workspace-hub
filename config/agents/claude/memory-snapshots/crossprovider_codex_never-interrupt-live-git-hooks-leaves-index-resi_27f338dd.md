---
name: crossprovider codex never-interrupt-live-git-hooks-leaves-index-resi
description: Never interrupt live Git hooks — leaves index residue
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-operations, risk-avoidance]
---

When a repository hook owns the Git index lock, wait for it to finish. Killing the hook is more likely to leave index residue than waiting minutes for the hook to complete its staged-blob validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
