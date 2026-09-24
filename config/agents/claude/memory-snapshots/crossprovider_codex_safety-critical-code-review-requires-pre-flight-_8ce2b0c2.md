---
name: crossprovider codex safety-critical-code-review-requires-pre-flight-
description: Safety-critical code review requires pre-flight file presence verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, process-safety, verification]
---

Reviewing code that doesn't exist on the filesystem leads to false non-APPROVE verdicts. Always verify target files exist and are readable before starting assessment. Block review if files are absent and request actual artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
