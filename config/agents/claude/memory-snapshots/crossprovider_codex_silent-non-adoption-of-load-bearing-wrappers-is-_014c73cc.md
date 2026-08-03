---
name: crossprovider codex silent-non-adoption-of-load-bearing-wrappers-is-
description: Silent non-adoption of load-bearing wrappers is a hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [dispatch, harness, design-flaw]
---

When a system's correctness depends on sessions using a wrapper (e.g., Windows Scheduled-Task or a Linux equivalent for dispatch), non-adoption must be made visible, not silent. A session that doesn't use the wrapper produces no record and is indistinguishable from an outage. Design should require explicit membership declaration or fail-closed enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
