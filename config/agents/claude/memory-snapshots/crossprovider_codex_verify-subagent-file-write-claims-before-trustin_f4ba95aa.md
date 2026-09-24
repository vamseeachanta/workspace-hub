---
name: crossprovider codex verify-subagent-file-write-claims-before-trustin
description: Verify subagent file-write claims before trusting success
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subagent-safety, file-verification, phantom-writes]
---

Subagent Write tool may report success without the file landing on disk (phantom write hazard). Main session must ls/stat to verify before believing the artifact exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
