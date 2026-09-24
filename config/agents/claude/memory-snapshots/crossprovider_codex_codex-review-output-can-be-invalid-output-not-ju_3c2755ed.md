---
name: crossprovider codex codex-review-output-can-be-invalid-output-not-ju
description: Codex review output can be INVALID_OUTPUT (not just parsing failure)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, review, output-validation, provider-specific]
---

Codex can emit structurally valid JSON/YAML that does not conform to the expected review schema (INVALID_OUTPUT state). This is distinct from parse failure and requires fallback handling in cross-review script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
