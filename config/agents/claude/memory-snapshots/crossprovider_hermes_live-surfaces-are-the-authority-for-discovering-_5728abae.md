---
name: crossprovider hermes live-surfaces-are-the-authority-for-discovering-
description: Live surfaces are the authority for discovering legacy compatibility needs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legacy-discovery, debugging-pattern, surface-audit]
---

Find legacy wrappers by searching live surfaces (docs, scripts, config rules), not historical reports or tests. Live surfaces show where stale code is still invoked; grep those references to identify which compatibility stubs are load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
