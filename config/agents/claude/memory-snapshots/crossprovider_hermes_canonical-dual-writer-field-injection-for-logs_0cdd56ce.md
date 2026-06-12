---
name: crossprovider hermes canonical-dual-writer-field-injection-for-logs
description: Canonical dual-writer field injection for logs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [logging, backwards-compatibility, minimal-patch]
---

When adding optional fields to long-lived persistent logs (e.g., session_id to session-logger.sh output), inject at the canonical write-once location that already dual-writes to both state/ and logs/ destinations. Downstream JSON consumers using `.get(field, default)` tolerate additive fields without schema migration. This avoids breaking consumers while unblocking analytics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
