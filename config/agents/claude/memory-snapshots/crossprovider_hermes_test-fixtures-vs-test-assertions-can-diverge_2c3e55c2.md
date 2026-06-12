---
name: crossprovider hermes test-fixtures-vs-test-assertions-can-diverge
description: Test fixtures vs test assertions can diverge
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing-gap, test-design, coverage]
---

Fixtures include edge cases (mixed-public/private corpus) but tests don't assert behavior. Coverage appears complete at fixture level but gaps hide. Every fixture case needs explicit test assertion or inline deprecation comment.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
