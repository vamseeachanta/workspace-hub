---
name: crossprovider codex executable-classifiers-use-runtime-string-fragme
description: Executable classifiers use runtime string fragments, not committed patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, security, enforcement]
---

Validation scripts encoding denied/allowed command patterns should construct them at runtime from string fragments to avoid self-blocking the commit. Avoid committing runnable denied expressions; use dynamic construction or forensic allowlists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
