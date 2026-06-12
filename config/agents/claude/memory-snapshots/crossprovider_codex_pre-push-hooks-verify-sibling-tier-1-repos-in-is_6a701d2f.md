---
name: crossprovider codex pre-push-hooks-verify-sibling-tier-1-repos-in-is
description: Pre-push hooks verify sibling tier-1 repos in isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ci-verification, isolated-worktree]
---

Pre-push hooks check for neighboring tier-1 repositories (`assethold`, `digitalmodel`, etc.); isolated worktrees lack these, causing blocks. Documented fallback is `GIT_PRE_PUSH_SKIP=1 git push`; no force-push needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
