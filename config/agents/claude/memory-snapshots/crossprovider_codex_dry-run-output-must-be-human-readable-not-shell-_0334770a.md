---
name: crossprovider codex dry-run-output-must-be-human-readable-not-shell-
description: Dry-run output must be human-readable, not shell-escaped
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [dry-run, output-format, operator-ux]
---

When a script has `--dry-run`, print a readable command line (not `%q` shell-escaped). Operator should be able to read and understand what will execute, not decode escape sequences. Readability aids verification and debugging.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
