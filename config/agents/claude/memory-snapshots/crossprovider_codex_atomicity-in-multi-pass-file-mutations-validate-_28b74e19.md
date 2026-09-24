---
name: crossprovider codex atomicity-in-multi-pass-file-mutations-validate-
description: Atomicity in multi-pass file mutations: validate before writes, keep traps active
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, error-handling, atomicity]
---

When scripts do multi-pass processing with ID allocation and file writes (e.g., reserve IDs → validate → write children), keep cleanup traps active through ALL write phases. Disarming the trap before the final write means failures leave partial state (orphaned files). Instead, prevalidate everything in a read-only pass, then write atomically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
