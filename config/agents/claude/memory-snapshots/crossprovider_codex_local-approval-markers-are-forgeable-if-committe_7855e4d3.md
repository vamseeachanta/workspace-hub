---
name: crossprovider codex local-approval-markers-are-forgeable-if-committe
description: Local approval markers are forgeable if committed
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, approval, markers, fail-closed]
---

Age check (<120s) only catches uncommitted markers. Committed markers are always trusted, creating a bypass; retire local markers in favor of server-side label-actor authority with timeline verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
