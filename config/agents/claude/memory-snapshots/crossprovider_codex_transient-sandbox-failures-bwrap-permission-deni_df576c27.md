---
name: crossprovider codex transient-sandbox-failures-bwrap-permission-deni
description: Transient Sandbox Failures: bwrap Permission Denied is Retriable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sandbox-reliability, transient-failures, retry-logic]
---

bwrap: setting up uid map: Permission denied appears as a transient concurrency symptom in execution sandboxes, not a permanent failure. Implement retry logic with exponential backoff (up to 3 retries). On success, the same command completes normally. Critical for robustness on parallel ingest dispatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
