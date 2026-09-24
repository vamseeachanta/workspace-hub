---
name: crossprovider codex tree-object-identity-must-be-verified-after-revi
description: Tree object identity must be verified after review approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, verification, integrity-gate]
---

After a review approves a commit, verify the tree object hash matches the reviewed source exactly before allowing downstream dependencies to build on it. A byte-mismatch indicates unreviewed changes slipped through.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
