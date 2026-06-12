---
name: crossprovider codex validation-only-lanes-post-evidence-never-no-op-
description: Validation-only lanes post evidence, never no-op commits
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [validation-lanes, evidence-comments, workflow-efficiency]
---

When implementation already landed elsewhere (merged PR, sibling branch, prior lane), stay in validation mode: run checks, post evidence comment with validation results and blockers, do not create a no-op commit. Only implement if explicit contract gap emerges during validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
