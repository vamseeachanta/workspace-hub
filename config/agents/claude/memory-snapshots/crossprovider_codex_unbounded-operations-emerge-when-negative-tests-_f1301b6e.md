---
name: crossprovider codex unbounded-operations-emerge-when-negative-tests-
description: Unbounded operations emerge when negative tests are absent
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [testing, scope-enforcement, negative-test-coverage, tdd]
---

Specs requiring bounded operations (header-only reads, sampled walks, no full-manifest hashing) get implemented as full traversals if validators lack separate negative tests for each denied class. Spec banning 'find', 'jq', 'wc -l', and 'sha256sum' must test each denial independently; testing only one lets the others pass silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
