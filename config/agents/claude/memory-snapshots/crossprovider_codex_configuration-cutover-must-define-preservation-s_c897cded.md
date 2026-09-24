---
name: crossprovider codex configuration-cutover-must-define-preservation-s
description: Configuration cutover must define preservation semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [daemon-safety, configuration-migration, fail-closed-guards]
---

Daemon/cron migration must define: what counts as 'clean'? Which live jobs preserve vs remove? Require generated-block markers, backup, rollback, and post-cutover verification to avoid silently dropping undocumented configuration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
