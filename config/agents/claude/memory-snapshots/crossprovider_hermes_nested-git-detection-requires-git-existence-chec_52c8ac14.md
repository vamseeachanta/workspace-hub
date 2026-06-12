---
name: crossprovider hermes nested-git-detection-requires-git-existence-chec
description: Nested git detection requires .git existence check, not directory type alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-introspection, path-inspection, repo-detection]
---

Detecting direct nested git repos must check for `.git` file or directory; checking that a path is a directory is insufficient. Solution: inspect `os.path.exists(.git) or os.path.isdir(.git)` to distinguish actual git repos from other nested paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
