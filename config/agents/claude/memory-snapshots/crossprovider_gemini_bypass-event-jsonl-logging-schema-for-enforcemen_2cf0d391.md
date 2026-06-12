---
name: crossprovider gemini bypass-event-jsonl-logging-schema-for-enforcemen
description: Bypass event JSONL logging schema for enforcement audit
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [enforcement, audit-logging, gate-bypass]
---

Enforcement gates log bypass events to `logs/hooks/<gate>-bypass.jsonl` with schema `{timestamp, user, branch, local_oid, remote_oid, action}`. Aggregated by compliance dashboard for audit visibility and rollback decision support.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
