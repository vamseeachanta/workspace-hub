---
name: crossprovider codex audit-wrapper-patterns-enable-reliable-scriptabl
description: Audit wrapper patterns enable reliable scriptable execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scripting, patterns, observability, cron]
---

Modular audit scripts that run at scale need documented I/O, env-variable test overrides (to run locally without side effects), distinct exit codes for different failure modes, and an evidence line for cron-health integration. This wrapper pattern (e.g., `tier1-indexing-freshness.sh`) is reusable across audit domains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
