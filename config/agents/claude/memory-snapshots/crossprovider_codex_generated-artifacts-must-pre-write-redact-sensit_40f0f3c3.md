---
name: crossprovider codex generated-artifacts-must-pre-write-redact-sensit
description: Generated artifacts must pre-write redact sensitive content, not rely on post-hoc CI
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [redaction, pii, artifacts, generators, ci-gates]
---

Content generators (dashboards, reports) that include issue titles or repo paths must apply redaction inline BEFORE writing to tracked files. Post-hoc CI catch is necessary but insufficient—it cannot prevent future regeneration. Durable fix belongs in the generator.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
