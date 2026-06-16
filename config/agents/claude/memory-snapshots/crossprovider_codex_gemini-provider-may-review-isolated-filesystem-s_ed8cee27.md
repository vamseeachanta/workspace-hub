---
name: crossprovider codex gemini-provider-may-review-isolated-filesystem-s
description: Gemini provider may review isolated filesystem snapshot, not live repo state
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [provider-quirks, code-review, gemini, snapshot-mismatch]
---

Session 6 shows Gemini reviewing an isolated `/tmp/wf0/repo` snapshot that contradicted live `git ls-files` and `test -e` evidence in the actual repo; provider's findings were kept as disagreement evidence rather than accepted fact. When using multi-provider review, verify provider is reading current repo state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
