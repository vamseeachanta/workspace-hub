---
name: crossprovider codex review-artifact-verdict-sha-parsing-is-unsafe-wi
description: Review artifact verdict/SHA parsing is unsafe with prose examples
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-artifact-metadata, parsing-safety, continuous-planning]
---

scripts/ai/continuous-planning-pipeline.py accepts the first `APPROVE|MINOR|MAJOR|UNAVAILABLE` token anywhere in a file, and any line matching `Plan-SHA256: <64 hex>`, even if quoted inside review prompt examples or plan body. Machine-checkable metadata headers must precede all prose content in review artifacts, and verdict/SHA must only be recognized in dedicated metadata block.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
