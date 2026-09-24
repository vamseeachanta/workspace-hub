---
name: crossprovider codex git-branch-r-contains-cannot-prove-boolean-pushe
description: git branch -r --contains cannot prove boolean pushed status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-refs, boolean-hazards, stale-state]
---

`git branch -r --contains` inspects only local remote-tracking refs, which are stale/incomplete in shallow, no-remote, detached-HEAD, or fetch-delayed states. It cannot reliably prove `pushed: false` — only `pushed: unknown`. Specs that need this check must declare strict preconditions or use `true | false | unknown` instead of bool.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
