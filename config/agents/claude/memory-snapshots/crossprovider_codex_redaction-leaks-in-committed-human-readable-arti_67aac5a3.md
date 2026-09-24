---
name: crossprovider codex redaction-leaks-in-committed-human-readable-arti
description: Redaction leaks in committed human-readable artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, redaction, review]
---

Code can redact sensitive paths from programmatic output, but committed markdown/HTML reports can still leak what the code redacts. Backup disposition reporter leaked /mnt/ace paths in docs/ while programmatic output() redacted them; separate review pass needed for artifact leakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
