---
name: crossprovider codex redaction-must-occur-at-data-intake-not-output-r
description: Redaction must occur at data intake, not output rendering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [redaction, security, data-flows]
---

Secret redaction applied only at CLI output time allows raw material to leak through in-process APIs like collect_readiness(). Redact remote evidence and untrusted fields before storing them in data structures; apply output redaction as a defense-in-depth layer, not the primary barrier.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
