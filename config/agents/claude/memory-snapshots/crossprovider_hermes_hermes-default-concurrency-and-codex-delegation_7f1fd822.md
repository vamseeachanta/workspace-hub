---
name: crossprovider hermes hermes-default-concurrency-and-codex-delegation
description: Hermes default concurrency and Codex delegation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, configuration, concurrency, environment]
---

Hermes config: max_concurrent_children: 3, child_timeout_seconds: 600, default provider openai-codex. Supports 3-lane subagent parallelization out-of-box. Prefer direct Claude/Codex background agents for durable repo writes over Hermes delegate_task, which runs in weaker sandboxes. Working directory: /mnt/local-analysis/workspace-hub.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
