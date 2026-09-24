---
name: crossprovider codex git-submodule-readiness-prerequisites-before-mul
description: Git submodule readiness prerequisites before multi-repo operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-operations, submodules, prerequisites, validation]
---

Before operating on a submodule (migrations, syncs, checkouts), verify: stage is 160000, git-dir is valid, working tree is clean, and upstream tracking is set. Missing any indicates incomplete setup that will cause silent failures or partial migrations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
