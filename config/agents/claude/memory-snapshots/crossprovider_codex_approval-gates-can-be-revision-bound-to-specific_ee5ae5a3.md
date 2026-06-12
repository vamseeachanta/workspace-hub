---
name: crossprovider codex approval-gates-can-be-revision-bound-to-specific
description: Approval gates can be revision-bound to specific commits
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, github-workflow]
---

Some GitHub approval comments bind execution to a specific plan commit SHA (e.g., 'approved plan at 7cc1c0b1a'). Must validate locally that current branch contains that SHA; divergence is a hard blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
