---
name: crossprovider codex quota-exhaustion-status-cached-in-cache-agent-qu
description: Quota exhaustion status cached in ~/.cache/agent-quota.json affects provider fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, quota, provider-fallback]
---

Hermes reads HTTP 429 quota exhaustion from the agent-quota.json cache and treats it as persistent at startup, triggering fallback to backup providers. Transient quota errors can lock out a provider until manual cache invalidation or quota recovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
