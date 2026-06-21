---
name: crossprovider codex source-boundary-guards-require-path-level-constr
description: Source-boundary guards require path-level constraints, not just token scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [safety, input-validation, generators, fail-closed]
---

When generators read/write artifacts, constraining paths to repo-owned directories at the CLI/function level is essential; token-check tests alone are insufficient to prevent read/write access to arbitrary source roots (discovered as MAJOR vulnerability: arbitrary --source-issues and output paths could read/mutate /mnt/ace).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
