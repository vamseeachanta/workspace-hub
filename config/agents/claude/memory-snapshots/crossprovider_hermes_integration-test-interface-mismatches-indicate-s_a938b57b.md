---
name: crossprovider hermes integration-test-interface-mismatches-indicate-s
description: Integration test interface mismatches indicate stale test specs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, api-design, integration-tests, backwards-compatibility]
---

When integration tests expect dict but source function signature is List[str], check source implementation first—tests are often stale. Read the actual execute() signature before fixing tests; update assertions to match implementation behavior, not the other way around.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
