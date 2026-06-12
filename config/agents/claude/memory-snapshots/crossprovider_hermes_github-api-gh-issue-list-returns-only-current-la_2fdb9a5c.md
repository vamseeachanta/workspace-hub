---
name: crossprovider hermes github-api-gh-issue-list-returns-only-current-la
description: GitHub API gh issue list returns only current labels, not historical timeline
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, historical-data, approval-audit]
---

The pseudocode `gh issue list --json number,title,labels` only captures current label state, not when labels were added/removed. To prove approval sequencing (e.g., status:plan-approved existed before implementation), use `gh issue view --json timeline` or the events API instead. Blocks validation of approval-before-implementation ordering.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
