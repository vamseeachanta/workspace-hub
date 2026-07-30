---
name: crossprovider codex scheduler-integration-is-often-deferred-in-plans
description: Scheduler integration is often deferred in plans; must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [planning, scheduler-integration, end-to-end]
---

Plans proposing new features to loaders called by scheduler jobs must explicitly include scheduler config updates, job parameter wiring, and scheduler tests. Omitting this creates silent degradation where features are implemented but never used operationally due to missing scheduler-level propagation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
