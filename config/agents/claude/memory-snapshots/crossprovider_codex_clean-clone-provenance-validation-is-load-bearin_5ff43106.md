---
name: crossprovider codex clean-clone-provenance-validation-is-load-bearin
description: Clean-clone provenance validation is load-bearing for approval trust
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git, provenance, trust-path]
---

Git-based approval validation must be testable in fresh clones without pre-existing local state. Tests that pass only against contaminated worktrees hide trust-path regressions. Validate reviewed ancestry under PR refs and published ancestry under fetched `origin/main`, and add clean-clone, depth-one, missing-ref, and hash-mismatch test cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
