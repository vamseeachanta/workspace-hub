---
name: crossprovider gemini pre-commit-framework-differs-from-native-git-hoo
description: Pre-commit framework differs from native git hooks on stdin/file passing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hooks, pre-commit, ci-cd]
---

Pre-commit hooks with `stages: [push]` do not receive stdin from git the way native `.git/hooks/pre-push` does. Pre-commit uses file-based filtering (`files:` key) to determine hook invocation; manual STDIN parsing will silently exit without testing. Rely on file-filtering config, not stdin parsing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
