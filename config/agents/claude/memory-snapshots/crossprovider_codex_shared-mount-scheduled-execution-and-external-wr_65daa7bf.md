---
name: crossprovider codex shared-mount-scheduled-execution-and-external-wr
description: Shared-mount, scheduled execution, and external writes require explicit threat modeling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, security, threat-model]
---

Plans introducing shared-mount reads, cron scheduling, subprocess execution, or external API calls must include threat models for poisoning, TOCTOU, subprocess escaping, concurrent access, and clock skew. Generic 'path sanitization' is insufficient; state the exact validation strategy and cross-machine safety mechanism.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
