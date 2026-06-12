---
name: crossprovider hermes git-status-parsing-must-preserve-codes-d-m-r-to-
description: Git-status parsing must preserve codes (D/M/R) to enforce deletion policy
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, repo-structure, parser-robustness]
---

Parsing `git status --short` to paths-only discards critical status codes needed to detect deletions and relocations. worldenergydata#394 Phase-1 policy forbids deleting tracked generated artifacts, but a checker that strips status codes cannot detect `D` entries. Use structured parsing (status, path, old_path) or git status output that preserves codes (not just paths).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
