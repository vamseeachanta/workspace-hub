---
name: crossprovider codex date-d-requires-bsd-macos-fallback-pattern
description: date -d requires BSD/macOS fallback pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, portability, date]
---

Scripts using `date -d` will fail on macOS/BSD. Use the fallback pattern `date -d ... || date -v ...` to handle both GNU and BSD date implementations across the multi-OS repo.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
