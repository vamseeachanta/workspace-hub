---
name: crossprovider codex pr-link-pattern-refs-vs-closes-affects-closure
description: PR link pattern: Refs vs Closes affects closure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-workflows, issue-management]
---

Using 'Refs' instead of 'Closes' in PR descriptions leaves linked child/epic issues open. They require manual closure in a dependent step — a common housekeeping footgun when closing issue hierarchies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
