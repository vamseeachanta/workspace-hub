---
name: crossprovider codex child-issues-left-open-after-parent-pr-merge-ref
description: Child issues left open after parent PR merge (Refs vs Closes) require explicit closure with evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [workflow, git, issue-management]
---

PRs using 'Refs #123' instead of 'Closes #123' leave child issues open after merge. Track these explicitly in handoff/dispatch and close them sequentially only after the parent PR is confirmed merged, adding evidence comments. Stale open issues create the illusion of unfinished work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
