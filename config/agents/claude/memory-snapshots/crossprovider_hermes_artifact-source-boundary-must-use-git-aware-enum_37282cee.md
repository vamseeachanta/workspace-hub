---
name: crossprovider hermes artifact-source-boundary-must-use-git-aware-enum
description: Artifact source boundary must use git-aware enumeration, not filesystem walk
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, validation, artifacts, committed-sources]
---

When artifacts claim to be generated from 'committed sources only', enumerate sources via `git ls-files` or equivalent Git-aware method, not filesystem `glob()`. Validator must also enforce the same boundary by regenerating from committed sources only, otherwise the validator becomes a gate that blesses the same violations it should reject. Repo with one committed file + one untracked file under allowed paths will emit both to artifacts if using filesystem enumeration.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
