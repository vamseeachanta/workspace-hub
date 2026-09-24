---
name: crossprovider codex cross-artifact-contract-closure-before-implement
description: Cross-artifact contract closure before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, contract-testing, multi-plan-coordination]
---

When specifications span multiple documents defining producer/consumer relationships (e.g., proof-release formats, handoff schemas), verify end-to-end compatibility before implementation. Common defects: example-vs-prose key-count mismatches, missing cross-field validation, incompatible schema evolution across coordinated specs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
