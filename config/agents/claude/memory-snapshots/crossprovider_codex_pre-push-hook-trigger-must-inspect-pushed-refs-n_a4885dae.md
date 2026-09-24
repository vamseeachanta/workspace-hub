---
name: crossprovider codex pre-push-hook-trigger-must-inspect-pushed-refs-n
description: Pre-push hook trigger must inspect pushed refs, not staged files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, pre-push, trigger-correctness]
---

A `pre-push` hook runs after commits are created, so detecting staged-file changes will miss the exact commits being pushed. Use OID diffs (`local_oid..remote_oid`) or inspect the pushed-ref log instead. Staged-file checks are unreliable for enforcement gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
