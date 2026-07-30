---
name: crossprovider codex no-mutation-testing-external-apis-without-explic
description: No mutation-testing external APIs without explicit owner approval
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [security, api-safety, authorization]
---

Write capability to external systems (HF, cloud storage, webhooks) carries live-data risk. Preflight checks (token validity, auth role) are safe; write operations must not be tested without explicit pre-authorization, even in isolated branches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
