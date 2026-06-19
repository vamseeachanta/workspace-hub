---
name: crossprovider codex pruning-scope-cache-build-git-dirs-must-have-exa
description: Pruning scope (cache, build, git dirs) must have exact plan-implementation parity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [plan-implementation-gap, filesystem-operations, test-scope]
---

Plan required cache/git/build pruning but implementation had a narrower hardcoded list. TDD for pruning must test the exact directory names the plan specifies; mismatches become implementation defects that code review catches too late.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
