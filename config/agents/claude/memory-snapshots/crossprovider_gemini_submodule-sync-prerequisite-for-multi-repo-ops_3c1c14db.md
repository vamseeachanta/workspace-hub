---
name: crossprovider gemini submodule-sync-prerequisite-for-multi-repo-ops
description: Submodule sync prerequisite for multi-repo ops
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git, submodules, multi-repo, preflight]
---

`git submodule sync --recursive && git submodule update --init --recursive` required before any operation touching submoduled repos; add `git push --dry-run` as publishability preflight to catch policy/permission issues early.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
