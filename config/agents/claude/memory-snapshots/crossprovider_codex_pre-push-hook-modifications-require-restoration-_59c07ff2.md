---
name: crossprovider codex pre-push-hook-modifications-require-restoration-
description: Pre-push hook modifications require restoration after failure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pre-push-artifacts, hook-side-effects, state-restoration]
---

When pre-push hook blocks, it may rewrite tracked files (e.g., coverage JSON to `{}`). Restore those files to their committed state before posting blocker comment; the commit itself is valid and the hook failure is the actual blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
