---
name: crossprovider gemini repository-local-lockfiles-beat-tmp-for-cross-se
description: Repository-local lockfiles beat /tmp for cross-session state
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [infrastructure, locking]
---

For persistent lockfiles (fcntl locks), use `<repo>/.locks/` instead of `/tmp`. Survives session boundaries and avoids system-level conflicts across multiple machines.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
