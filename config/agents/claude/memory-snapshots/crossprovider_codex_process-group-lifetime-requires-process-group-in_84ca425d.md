---
name: crossprovider codex process-group-lifetime-requires-process-group-in
description: Process group lifetime requires process group inspection, not child PID alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-groups, unix-semantics, supervisor, health-check]
---

Supervisors intentionally holding locks or resources for process group lifetime (after direct child exits) must inspect the entire process group, not just the original child PID. Checking only the dead child can misclassify valid active protected states as stale/reused PIDs. Found in cron runtime health classification. Fix: inspect process group liveness, not just direct child.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
