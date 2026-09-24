---
name: crossprovider codex issue-comment-body-scanning-fail-open-risk-in-cl
description: Issue-comment body scanning fail-open risk in CLI validators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-safety, validation-gaps, security]
---

When a CLI accepts `--issue-comment-body-file`, that path must run the same deny/legal/snapshot checks as publication paths. Default behavior often skips validation for CLI-only paths. Test with negative synthetic bodies (secrets, URLs, metadata) to verify fail-closed behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
