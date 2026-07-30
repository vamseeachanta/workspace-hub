---
name: crossprovider codex approval-must-be-materialized-in-repository-stat
description: Approval must be materialized in repository state
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [approval, workflow, repository-ssot, parallel-agents]
---

External approval (meeting notes, emails, off-repo documents) is invisible to repository-based agents and future sessions. Always materialize approval as committed repository artifacts (approval markers, labels, or documented decision in the tracking issue) so the next agent recognizes the approval without re-interpreting external sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
