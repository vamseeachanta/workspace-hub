---
name: crossprovider codex dry-run-must-be-pure-no-temp-files-in-target-dir
description: Dry-run must be pure; no temp files in target directory
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [dry-run, purity, design-contract]
---

Dry-run that writes temporary files beside the real target observably mutates the filesystem (fails on read-only dirs, leaves transient state). Session 7 found this violated task contract; dry-run must stage in `/tmp` or equivalent and never touch the target directory until ready to commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
