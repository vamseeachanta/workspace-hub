---
name: crossprovider codex large-repo-git-operations-timeout-use-narrower-p
description: Large-repo git operations timeout; use narrower probes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, large-repo, tooling-hazard]
---

Repos with ~33K files (e.g., llm-wiki) see timeout/performance cliff on `git status`, broad `find`, and full-diff operations. Workaround: use path-specific probes (`git ls-files --error-unmatch <path>`, narrowed diff ranges, `rg --files` instead of `find`) and avoid repository-wide status walks unless unavoidable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
