---
name: crossprovider gemini folder-skill-migration-parallel-setup-then-cutov
description: Folder-skill migration: parallel setup, then cutover, then cleanup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration-strategy, backward-compat, verification-gates]
---

Build new folder-skill structure in parallel with old (Copy phase). Verify all runtime paths resolve and tests pass (Verification phase). Only then delete old structure (Cleanup phase). Atomic cutover prevents silent path-resolution failures. Requires explicit error handling for missing folders and stale references.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
