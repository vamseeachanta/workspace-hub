---
name: crossprovider gemini absolute-paths-in-plans-break-cross-machine-sync
description: Absolute paths in plans break cross-machine sync workflows
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [portability, cross-machine, paths]
---

Plans that reference hardcoded paths like `/home/user/...`, `/mnt/...`, or `~/...` fail when executed on different machines or in CI. Use repository-relative paths or environment variables. Verify paths via `git ls-files` or repo config, not absolute assumptions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
