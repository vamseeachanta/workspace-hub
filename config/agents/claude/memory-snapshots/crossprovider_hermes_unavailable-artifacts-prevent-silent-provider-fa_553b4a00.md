---
name: crossprovider hermes unavailable-artifacts-prevent-silent-provider-fa
description: UNAVAILABLE artifacts prevent silent provider failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-integration, error-handling, visibility]
---

When provider CLI fails (nonzero exit), times out, or returns empty output, create an explicit `UNAVAILABLE` artifact (structured header + reason). Never advance plans based on UNAVAILABLE artifacts. This makes provider failures visible and prevents cascading downstream work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
