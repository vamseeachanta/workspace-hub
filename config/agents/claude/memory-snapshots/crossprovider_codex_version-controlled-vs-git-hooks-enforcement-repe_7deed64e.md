---
name: crossprovider codex version-controlled-vs-git-hooks-enforcement-repe
description: Version-controlled vs .git/hooks: enforcement repeatability
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-hooks, deployment-reliability]
---

Local `.git/hooks/` are not version-controlled and can diverge across clones; they're also bypassable via --no-verify. Authoritative gates must be installed via a version-controlled shim (like `.pre-commit-config.yaml` + installer script), not written directly to .git/hooks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
