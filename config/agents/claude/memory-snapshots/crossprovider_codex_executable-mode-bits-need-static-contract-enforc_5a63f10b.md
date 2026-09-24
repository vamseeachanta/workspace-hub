---
name: crossprovider codex executable-mode-bits-need-static-contract-enforc
description: Executable mode bits need static contract enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, contracts, unix, static-checks]
---

Unix entry-point scripts require `chmod +x` validation in test fixtures; git attribute tracking and post-checkout hooks are unreliable across clones. Explicit mode check (`test -x <file>`) belongs in static contract suite, not deferred to runtime.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
