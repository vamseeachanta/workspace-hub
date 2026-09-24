---
name: crossprovider codex pre-push-hook-gates-are-coupled-by-path-assumpti
description: Pre-push hook gates are coupled by path assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hooks, scope-discovery, interdependency]
---

Pre-push hooks with multiple scripts (mypy-ratchet, coverage, secrets-scan) share nested repo-layout assumptions. Fixing one script leaves related gates failing. Require holistic gate-surface mapping and shared resolver before scope closure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
