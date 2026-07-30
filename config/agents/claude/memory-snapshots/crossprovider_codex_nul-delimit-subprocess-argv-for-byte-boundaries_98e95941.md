---
name: crossprovider codex nul-delimit-subprocess-argv-for-byte-boundaries
description: NUL-delimit subprocess argv for byte boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [testing, subprocess, shells]
---

Newline-delimited capture loses argument boundaries when args contain newlines; NUL-delimited capture is required to strictly prove byte-for-byte argument boundaries in subprocess tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
