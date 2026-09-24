---
name: crossprovider codex adversarial-contract-review-scope-codec-api-surf
description: Adversarial contract review scope: codec, API surface, security, records, test discipline
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, specification, security]
---

Contract reviews must verify: exact encoding/codec specs, public API surface (constants, exceptions, field names, type annotations), descriptor-walk security/race behavior, internal record structure, and one-behavior-per-test discipline. Sparse coverage in these areas allows weak implementations to pass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
