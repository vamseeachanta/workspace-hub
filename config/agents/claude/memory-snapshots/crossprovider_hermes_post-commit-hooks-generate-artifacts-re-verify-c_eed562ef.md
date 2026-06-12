---
name: crossprovider hermes post-commit-hooks-generate-artifacts-re-verify-c
description: Post-commit hooks generate artifacts; re-verify clean state before declaring done
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, hooks, verification, hygiene]
---

After git push/commit, re-check for hook-generated files (e.g., `logs/orchestrator/hermes/skill-patches.jsonl`, digest outputs) before declaring repo clean. Push success ≠ clean working tree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
