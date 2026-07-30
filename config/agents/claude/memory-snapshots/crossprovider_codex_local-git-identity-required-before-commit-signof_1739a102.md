---
name: crossprovider codex local-git-identity-required-before-commit-signof
description: Local git identity required before commit --signoff on fresh clones
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, config]
---

When global git identity is disabled, `git commit --signoff` on a fresh clone fails unless a trusted local identity is first established with `git config user.{name,email}`. Silent global-config disable without local setup causes downstream failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
