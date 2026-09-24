---
name: crossprovider codex output-path-write-guards-required-even-in-dry-ru
description: Output path write guards required even in dry-run tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety, dry-run, output-guards]
---

Dry-run reporters must reject writes to sensitive system paths (e.g., /mnt/ace) even if the underlying operation is non-destructive, preventing accidental mutations through --output argument misuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
