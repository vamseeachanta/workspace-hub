---
name: crossprovider codex multi-agent-shared-checkout-pathspec-scoped-comm
description: Multi-agent shared checkout: pathspec-scoped commits prevent interference
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [multi-agent, git-safety]
---

When multiple Claude/Codex processes are active, use pathspec commits (git add <paths>) instead of git add . or -A to avoid sweeping unrelated parallel work. Verify staged state is clean and no .git/index.lock exists before committing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
