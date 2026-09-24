---
name: crossprovider codex approval-gates-are-load-bearing-never-self-autho
description: Approval gates are load-bearing; never self-authorize
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [authorization, gates, user-in-loop]
---

User-applied approval gates (status:plan-approved label, goal invocation pre-checks) exist to gate authorization boundaries. Agents must refuse to bypass them even when technically capable. The user-in-loop is the load-bearing gate; skipping it creates real incidents in multi-provider operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
