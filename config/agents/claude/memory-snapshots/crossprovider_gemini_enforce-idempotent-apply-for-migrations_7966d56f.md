---
name: crossprovider gemini enforce-idempotent-apply-for-migrations
description: Enforce idempotent apply for migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migrations, testing, script-contracts]
---

Migration script's --apply must be idempotent: second run on clean state (after first apply + commit) produces `git status --porcelain` empty. Verify with explicit re-run test. Non-idempotent scripts hide incomplete apply logic or state transitions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
