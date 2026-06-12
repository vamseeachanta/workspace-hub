---
name: crossprovider hermes git-lock-contention-preserves-subagent-work
description: Git lock contention preserves subagent work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, parallel, reliability, multi-agent]
---

When parallel subagents hit git lock failures during commit, parent session can still commit their outputs afterward. Work is never lost; it bundles into later parent commits. Don't panic on subagent git errors — verify the files exist and parent can recover.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
