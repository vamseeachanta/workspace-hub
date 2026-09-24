---
name: crossprovider codex codex-provider-audit-lacks-progress-output
description: Codex provider-audit lacks progress output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-ux, observability, codex-cli]
---

The `provider_session_ecosystem_audit.py` tool buffers all output until completion (~30-56s), appearing hung in interactive use. This makes operator troubleshooting impossible during normal timeouts. Fix: add incremental progress logging and a timeout wrapper.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
