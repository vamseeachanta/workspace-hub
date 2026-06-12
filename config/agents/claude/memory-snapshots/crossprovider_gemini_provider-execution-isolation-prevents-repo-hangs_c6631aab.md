---
name: crossprovider gemini provider-execution-isolation-prevents-repo-hangs
description: Provider execution isolation prevents repo hangs
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [provider-isolation, reliability, review-transport, tool-drift]
---

Execute Claude/Gemini in isolated temp directories with `cd <tmpdir>` and `--permission-mode bypassPermissions --tools ''` to avoid repo-context hangs and tool-availability drift. Discovered as critical for reliable review transport in WRK-640.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
