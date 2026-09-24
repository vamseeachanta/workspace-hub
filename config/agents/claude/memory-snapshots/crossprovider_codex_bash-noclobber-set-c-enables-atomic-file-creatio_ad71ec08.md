---
name: crossprovider codex bash-noclobber-set-c-enables-atomic-file-creatio
description: Bash noclobber (set -C) enables atomic file creation for ID reservation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash-concurrency, atomicity, technique]
---

Using `set -C` to atomically create sentinel files like `WRK-${NEXT_ID}.md` prevents race conditions in concurrent ID generation. Pairing with 5-attempt retry and exit-on-failure provides safe reservation without external locking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
