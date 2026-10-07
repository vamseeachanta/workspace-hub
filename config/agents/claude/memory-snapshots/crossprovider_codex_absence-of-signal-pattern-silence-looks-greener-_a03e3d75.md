---
name: crossprovider codex absence-of-signal-pattern-silence-looks-greener-
description: Absence-of-signal pattern: silence looks greener than failure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [observability, alarms, audit-blindspots]
---

Codex found this across multiple sessions: missing checks appear as healthy, failing checks are visible. This bias causes broken alarms and suppressed tests to evade review. Every suppression (--no-telegram, skipped test, disabled guard) must cite a reason that can be verified, not just stated. Liveness requires explicit probes, not absence-inference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
