---
name: crossprovider codex stash-pop-must-check-if-this-run-created-the-sta
description: Stash pop must check if this run created the stash
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-safety, error-prevention]
---

Never blindly `stash pop` at lane end. Always verify this run created the stash first; otherwise old user stashes can be accidentally applied during cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
