---
name: crossprovider codex handoff-prompts-with-git-mutations-become-stale-
description: Handoff prompts with git mutations become stale if referenced PR merges before execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [handoff, git-mutations, pr-workflows, execution-safety]
---

When embedding commit/push instructions for deferred nested-agent execution, verify the referenced PR/branch still exists before running the handoff. If the PR merged while the handoff was pending, the instructions will try to push to a deleted branch, creating stale residue. Post-merge follow-up issues are needed when round-N changes don't land before squash merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
