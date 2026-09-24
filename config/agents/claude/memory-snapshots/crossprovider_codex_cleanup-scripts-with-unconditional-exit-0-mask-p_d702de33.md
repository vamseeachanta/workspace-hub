---
name: crossprovider codex cleanup-scripts-with-unconditional-exit-0-mask-p
description: Cleanup scripts with unconditional exit 0 mask partial failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, error-handling, automation, fail-open-bug]
---

Destructive cleanup scripts (e.g., `rm -rf` operations) that unconditionally exit with status 0 will report success even if the underlying command partially fails (e.g., `Directory not empty`). The failure is logged but invisible to orchestration. Removal operations must exit with the actual command status, not a hardcoded zero.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
