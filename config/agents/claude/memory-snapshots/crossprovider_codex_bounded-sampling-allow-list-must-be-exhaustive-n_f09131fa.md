---
name: crossprovider codex bounded-sampling-allow-list-must-be-exhaustive-n
description: Bounded-sampling allow-list must be exhaustive, not just negative (block find/du)
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [sampling, bounds, implementation-safety]
---

Claiming a wave is 'bounded' while only blocking `find` and `du` still permits unbounded crawl via `rg`, `fd`, `ls -R`, `os.walk`, manifest sweeps, or custom Python scripts. Effective bounds need positive allow-list: enumerate every permitted search pattern (including tool + flags), or use materialized manifest only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
