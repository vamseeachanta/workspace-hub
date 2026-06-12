---
name: crossprovider codex exit-code-and-json-status-must-have-separate-con
description: Exit code and JSON status must have separate contracts for automation safety
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cli-design, automation]
---

For CLI tools used in CI/cron, define exit codes (0=pass, 1=warn, 2=block) independently from JSON status fields. This allows process-level gating without requiring JSON parsing, and JSON content can remain richer without bloating exit semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
