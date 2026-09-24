---
name: crossprovider codex local-enforcement-gates-are-not-repo-wide-gates
description: Local enforcement gates are not repo-wide gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-architecture, pre-push-hooks, cross-repo-testing]
---

Pre-push hooks live only on developer machines, are easy to bypass with `--no-verify`, and don't enforce across CI or contributor clones. A real cross-repo integration test gate needs version-controlled installation infrastructure plus CI/server-side enforcement. Local hooks are advisory only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
