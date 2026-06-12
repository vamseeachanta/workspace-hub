---
name: crossprovider hermes unresolved-markdown-targets-fail-closed-with-md-
description: Unresolved markdown targets fail closed with .md fallback resolution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [link-resolution, markdown, validation]
---

Extensionless target references should attempt `.md` suffix resolution before rejection; unresolved existing repo files must fail validation. Regression tests cover both extensionless markdown targets that exist and those that don't.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
