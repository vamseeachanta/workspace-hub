---
name: crossprovider hermes concurrent-closeout-race-on-shared-root-requires
description: Concurrent closeout race on shared root requires lock serialization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-lock, parallel-agents, workspace-hub, closeout]
---

Multiple parallel agents committing to workspace-hub root race on .git lock, causing stale/merged/unmerged state drift. Use `.git/agent-closeout.lock` with flock() to serialize commits; coordinated branch cleanup + close + push must happen atomically per issue to prevent stale local branches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
