---
name: crossprovider gemini use-git-apply-3way-for-patches-on-concurrent-edi
description: Use git apply --3way for patches on concurrent-edit targets
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, concurrency, patching]
---

Bare `git apply` fails when target files have been modified by other processes. Use `git apply --3way` or `git am` to handle concurrent drift in the source tree.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
