---
name: crossprovider codex absolute-paths-in-hook-commands-block-cross-mach
description: Absolute paths in hook commands block cross-machine portability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, portability, technical-debt]
---

Hook commands using absolute paths (e.g., /mnt/local-analysis/workspace-hub/...) are machine-specific and break on different checkout paths. Refactor to path-relative commands (e.g., scripts/foo.sh) to make hooks portable across machines and checkouts in the same workspace ecosystem.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
