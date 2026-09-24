---
name: crossprovider codex test-instrumentation-predicates-don-t-measure-st
description: Test instrumentation predicates don't measure storage reads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, verification-hazards]
---

Callback predicates used in tests to instrument query evaluation are not row-read counters—they observe the query plan at Python level, not actual storage-engine reads. Test observable SQL artifacts (LIMIT, projection, column authorization) rather than callback invocation counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
