---
name: crossprovider codex codex-sandbox-blocks-file-operations-with-bwrap-
description: Codex sandbox blocks file operations with bwrap loopback permission error
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sandbox, codex, environment, blocker]
---

Multiple review sessions failed consistently with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` when attempting file reads or shell operations on workspace-hub. This is not a transient socket issue but a persistent AppArmor or capability denial preventing local file I/O, blocking code review tasks entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
