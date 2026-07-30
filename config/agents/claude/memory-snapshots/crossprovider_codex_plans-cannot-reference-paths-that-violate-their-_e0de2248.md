---
name: crossprovider codex plans-cannot-reference-paths-that-violate-their-
description: Plans cannot reference paths that violate their own validation scanners
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [governance, self-blocking, scanner-contract]
---

A plan that will be scanned for public-surface violations cannot cite ACE_SHARE_ROOT paths as examples; the scanner flags them as private and fails the plan itself. Replace concrete share paths with aggregate descriptions (e.g., 'Standards corpus ~43 GB') before submitting for public-surface validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
