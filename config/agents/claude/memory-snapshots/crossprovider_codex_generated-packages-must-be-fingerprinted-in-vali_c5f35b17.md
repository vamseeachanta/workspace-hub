---
name: crossprovider codex generated-packages-must-be-fingerprinted-in-vali
description: Generated packages must be fingerprinted in validation reports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-strategy, artifact-identity, licensing]
---

When validating generated model packages on licensed third-party tools, commit only the report, not the package. But without hashes of key generated artifacts, there is no durable proof of what code was tested. Add a manifest with file hashes and record it in the committed report.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
