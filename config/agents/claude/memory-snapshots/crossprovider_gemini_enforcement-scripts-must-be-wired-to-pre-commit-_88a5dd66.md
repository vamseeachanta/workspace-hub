---
name: crossprovider gemini enforcement-scripts-must-be-wired-to-pre-commit-
description: Enforcement scripts must be wired to pre-commit/CI to prevent dead code
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [enforcement, dead-code, pre-commit]
---

Shell enforcement scripts (check-*.sh) in `.claude/hooks/` are dead code unless explicitly wired to pre-commit, CI, or settings hooks. Unenforced scripts attract scope but never execute, blocking violations they were designed to catch.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
