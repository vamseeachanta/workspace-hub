---
name: crossprovider codex embedded-text-review-is-reliable-for-immutable-c
description: Embedded text review is reliable for immutable commits
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [code-review, immutable-state, tooling]
---

When reviewing frozen/immutable commits, embed all relevant source text directly in the review prompt, disable provider filesystem tools, and use realistic timeouts (180s with text-mode is reliable). This avoids filesystem I/O hangs and produces faster, more reliable verdicts than filesystem-driven review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
