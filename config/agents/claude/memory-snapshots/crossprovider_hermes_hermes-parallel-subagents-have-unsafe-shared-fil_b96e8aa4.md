---
name: crossprovider hermes hermes-parallel-subagents-have-unsafe-shared-fil
description: Hermes parallel subagents have unsafe shared-filesystem assumptions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, parallelism, git-concurrency]
---

Separate terminal sessions don't guarantee shared working-directory state; parallel Write calls risk silent partial failures or stale HEAD. When using subagents for git-tracked work, serialize writes or use one-agent-writes pattern with manifest deferral to main session.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
