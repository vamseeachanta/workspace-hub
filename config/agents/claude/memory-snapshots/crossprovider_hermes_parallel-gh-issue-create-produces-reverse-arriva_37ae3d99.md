---
name: crossprovider hermes parallel-gh-issue-create-produces-reverse-arriva
description: Parallel gh issue create produces reverse-arrival issue numbers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-cli, parallelization, gh-issue]
---

`gh issue create &` in parallel assigns issue numbers in reverse order of creation completion. Always post-batch audit via `gh issue list --json number,title` to verify correct issue-to-title pairing before proceeding with comments/labels.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
