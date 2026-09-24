---
name: crossprovider codex file-reading-in-shell-must-be-bounded-to-prevent
description: File reading in shell must be bounded to prevent OOM
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, resource-limits, robustness]
---

Agents accidentally provide binaries or huge reports; use head -c 5MB + tr -d '\000' to clamp reads and strip nulls before bash assignment. Prevents OOMs when concatenating unbounded file content into variables.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
