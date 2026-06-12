---
name: crossprovider hermes git-diff-check-is-strict-on-review-artifacts
description: Git diff --check is strict on review artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, whitespace, pre-commit]
---

Plan review markdown files must have trailing whitespace stripped and exactly one final newline; `git diff --check` will fail on mixed line endings or missing EOF newline. Normalize all markdown review artifacts before staging (`sed -i 's/[[:space:]]*$//' && echo '' >> file`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
