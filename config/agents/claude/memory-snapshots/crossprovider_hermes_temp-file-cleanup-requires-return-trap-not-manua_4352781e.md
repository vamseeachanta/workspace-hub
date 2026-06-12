---
name: crossprovider hermes temp-file-cleanup-requires-return-trap-not-manua
description: Temp file cleanup requires RETURN trap, not manual rm in each path
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-safety, temp-files, cleanup-pattern]
---

Functions that create temp files leak them on errexit/early-return unless using trap. Pattern: `local tmp=""; trap 'rm -f "$tmp"' RETURN; tmp="$(mktemp ...)"; ... mv "$tmp" target; tmp=""`. Resetting var after mv prevents trap from deleting the moved file. Manual rm in each branch is error-prone.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
